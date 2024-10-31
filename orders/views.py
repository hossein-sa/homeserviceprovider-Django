from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
from users.models import Wallet
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from services.models import MainService
from users.permissions import IsCustomer, IsSpecialist
from .models import Order, Proposal
from .serializers import OrderSerializer, ProposalSerializer, MainServiceSerializer
from .utils import process_payment  # Utility function for handling payments


class OrderCreateView(generics.CreateAPIView):
    """
    View for customers to create an order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsCustomer)

    def perform_create(self, serializer):
        # Sets visible_until based on sub-service's expiration time if not provided
        order = serializer.save(customer=self.request.user)
        if not order.visible_until:
            order.visible_until = timezone.now() + timedelta(hours=order.sub_service.expiration_hours)
            order.save()


class ProposalCreateView(generics.CreateAPIView):
    """
    View for specialists to create a proposal for an order,
    if the order's sub-service matches the specialist's service.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = (permissions.IsAuthenticated, IsSpecialist)

    def perform_create(self, serializer):
        specialist = self.request.user
        order_id = self.request.data.get('order')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check specialist's sub-service permissions
        if hasattr(specialist, 'specialist_service'):
            specialist_sub_services = specialist.specialist_service.sub_service.all()
            if order.sub_service not in specialist_sub_services:
                return Response(
                    {"error": "You are not authorized to make a proposal for this sub-service."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "You are not registered with any sub-services."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Save the proposal if authorized
        serializer.save(specialist=specialist, order=order)

        # Update order status after the first proposal
        if order.status == 'waiting_for_proposals':
            order.status = 'waiting_for_selection'
            order.save()


class MainServiceListView(generics.ListAPIView):
    """
    Lists all main services and their sub-services.
    """
    queryset = MainService.objects.all()
    serializer_class = MainServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class AvailableOrdersView(generics.ListAPIView):
    """
    Lists all orders available for specialist proposals,
    filtered by the specialist's sub-services.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsSpecialist]

    def get_queryset(self):
        specialist = self.request.user
        current_time = timezone.now()

        # Fetch specialist's sub-services
        specialist_sub_services = specialist.specialist_service.sub_service.all() if hasattr(specialist,
                                                                                             'specialist_service') else []

        # Filter orders by sub-services, status, and visibility
        return Order.objects.filter(
            sub_service__in=specialist_sub_services,
            status='waiting_for_proposals',
            visible_until__gte=current_time,
            selected_proposal__isnull=True
        )


class SelectProposalView(generics.UpdateAPIView):
    """
    Allows a customer to select a proposal for their order, updating status.
    """
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Ensure the customer selecting the proposal is the order creator
        if request.user != order.customer:
            return Response({"error": "You do not have permission to select a proposal for this order."},
                            status=status.HTTP_403_FORBIDDEN)

        proposal_id = request.data.get('proposal_id')

        try:
            selected_proposal = Proposal.objects.get(id=proposal_id)
        except Proposal.DoesNotExist:
            return Response({"error": "Proposal does not exist for this order."}, status=status.HTTP_404_NOT_FOUND)

        order.selected_proposal = selected_proposal
        order.status = 'waiting_for_arrival'
        order.visible_until = timezone.now()
        order.save()

        return Response({"status": "Proposal selected successfully, and order updated."}, status=status.HTTP_200_OK)


class MarkOrderCompleteView(generics.UpdateAPIView):
    """
    Allows only the customer who created the order to mark it as completed, triggering payment and updating status.
    """
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Ensure only the customer who created the order can mark it as completed
        if request.user != order.customer:
            return Response({"error": "You do not have permission to mark this order as completed."},
                            status=status.HTTP_403_FORBIDDEN)

        # Only proceed if the order is currently in "waiting_for_arrival" or "started" status
        if order.status not in ['waiting_for_arrival', 'started']:
            return Response({"error": "Order cannot be marked as completed at this stage."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Change the order status to 'completed'
        order.status = 'completed'
        order.save()

        # Process payment once completed
        try:
            process_payment(order.customer, order.selected_proposal.specialist, order.suggested_price)
            order.status = 'paid'
            order.save()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Order marked as completed and payment processed."}, status=status.HTTP_200_OK)


