# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'profile_picture', 'bio']

    def validate(self, data):
        # Require profile picture only for specialists
        if data.get('role') == 'specialist' and not data.get('profile_picture'):
            raise serializers.ValidationError({"profile_picture": "Specialists must have a profile picture."})
        return data

    def create(self, validated_data):
        # Extract profile data
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', "")

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )

        # Create the Profile and assign bio and profile_picture
        profile = Profile.objects.create(user=user)
        if profile_picture:
            profile.profile_picture = profile_picture
        if bio:
            profile.bio = bio
        profile.save()  # Save after assigning the fields

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']
