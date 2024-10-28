from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from .models import User  # Change 'models' to '.models'
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
