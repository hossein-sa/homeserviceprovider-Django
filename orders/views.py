from rest_framework import generics, permissions, status
from rest_framework.response import Response
from services.models import MainService
from .models import Order, Proposal
from .serializers import OrderSerializer, ProposalSerializer, MainServiceSerializer
from users.permissions import IsCustomer, IsSpecialist
from django.utils import timezone


class OrderCreateView(generics.CreateAPIView):
    """
       View for customers to create an order.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsCustomer)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class ProposalCreateView(generics.CreateAPIView):
    """
        View for specialists to create a proposal for an order, but only if the order's
        sub-service is related to the specialist.
    """
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = (permissions.IsAuthenticated, IsSpecialist)

    def perform_create(self, serializer):
        # Get the authenticated specialist
        specialist = self.request.user

        # Get the order ID from the request data
        order_id = self.request.data.get('order')

        # Check if the order exists
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the order's sub-service is in the specialist's sub-services
        if hasattr(specialist, 'specialist_service'):
            specialist_sub_service = specialist.specialist_service.sub_service.all()
            if order.sub_service not in specialist_sub_service:
                return Response(
                    {"error": "You are not authorized to make a proposal for this order's sub-service."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "You are not registered as a specialist with any sub-services."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Save the proposal with the specialist and order
        serializer.save(specialist=specialist, order=order)

        # Update order's status if this is the first proposal (optional)
        if order.status == 'waiting_for_proposals':
            order.status = 'waiting_for_selection'
            order.save()


class MainServiceListView(generics.ListAPIView):
    """
    View to list all main services with their related sub-services.
    """
    queryset = MainService.objects.all()
    serializer_class = MainServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class AvailableOrdersView(generics.ListAPIView):
    """
       View to list all orders available for specialists to make proposals,
       filtered by the specialist's related sub-services.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsSpecialist]

    def get_queryset(self):
        # Get authenticated specialist
        specialist = self.request.user
        current_time = timezone.now()

        # Check if the specialist has associated sub-services
        if hasattr(specialist, 'specialist_service'):
            specialist_sub_services = specialist.specialist_service.sub_service.all()
        else:
            specialist_sub_services = []

        # Return orders filtered by sub-services, status, visibility, and no selection
        return Order.objects.filter(
            sub_service__in=specialist_sub_services,
            status='waiting_for_proposals',
            visible_until__gte=current_time,
            selected_proposal__isnull=True  # Ensures no proposal has been selected yet
        )


class SelectProposalView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsSpecialist, IsCustomer]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
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
