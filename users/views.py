from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from django.contrib import messages
from .models import User, Wallet
from .permissions import IsCustomer, IsSpecialist
from .serializers import UserRegistrationSerializer, ProfileSerializer



class UserRegistrationView(generics.CreateAPIView):
    """
    Handles the creation of a new user (customer or specialist) and their profile if applicable.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Allows authenticated users to retrieve or update their profile information.
    """
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the profile data for the currently authenticated user
        return self.request.user.profile


class SpecialistOnlyView(generics.ListAPIView):
    """
    Allows access only to specialists, retrieving data relevant to specialists.
    """
    queryset = User.objects.filter(role='specialist')
    serializer_class = ProfileSerializer
    permission_classes = [IsSpecialist]


class CustomerOnlyView(generics.ListAPIView):
    """
    Allows access only to customers, retrieving data relevant to customers.
    """
    queryset = User.objects.filter(role='customer')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        # Filters profiles to return only those for customer users
        return User.objects.filter(role='customer')

@login_required
def recharge_wallet(request):
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount'))
            if amount <= 0:
                messages.error(request, "Please enter a valid amount.")
                return redirect(reverse("recharge_wallet"))

            # Update the customer's wallet balance
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += amount
            wallet.save()

            messages.success(request, f"Successfully added ${amount} to your wallet!")
            return redirect(reverse("wallet"))
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, "Invalid amount. Please enter a valid number.")

    return render(request, "users/recharge_wallet.html")


@login_required
def wallet(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, "users/wallet.html", {"balance": wallet.balance})