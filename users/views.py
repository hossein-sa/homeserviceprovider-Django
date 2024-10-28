from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from .models import User, Profile
from .permissions import IsCustomer, IsSpecialist
from .serializers import UserRegistrationSerializer, ProfileSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the profile of the currently authenticated user
        if self.request.user.role == 'admin':
            return super().get_object()
        return Profile.objects.get(user=self.request.user)


class SpecialistOnlyView(generics.ListAPIView):
    """
        Example view that only allows specialists to access.
    """
    queryset = Profile.objects.filter(user__role='specialist')
    serializer_class = ProfileSerializer
    permission_classes = [IsSpecialist]


class CustomerOnlyView(generics.ListAPIView):
    """
    Example view that only allows customers to access.
    """
    queryset = Profile.objects.all()  # Adjust this queryset based on your requirements
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        # Customize this method to retrieve data relevant only to customers
        return Profile.objects.filter(user__role='customer')
