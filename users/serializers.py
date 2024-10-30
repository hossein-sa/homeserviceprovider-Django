from rest_framework import serializers
from django.contrib.auth import get_user_model

from services.models import MainService, SubService, SpecialistService
from .models import Profile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(write_only=True, required=False)
    bio = serializers.CharField(write_only=True, required=False)

    # New fields for main service and sub-services
    main_service = serializers.PrimaryKeyRelatedField(
        queryset=MainService.objects.all(), required=False, write_only=True
    )
    sub_services = serializers.PrimaryKeyRelatedField(
        queryset=SubService.objects.all(), required=False, write_only=True, many=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'profile_picture', 'bio', 'main_service', 'sub_services']

    def validate(self, data):
        # Require profile picture only for specialists
        # if data.get('role') == 'specialist' and not data.get('profile_picture'):
        #     raise serializers.ValidationError({"profile_picture": "Specialists must have a profile picture."})
        # return data

        if data.get('role') == 'specialist':
            # Check main service presence for specialist
            if not data.get('main_service'):
                raise serializers.ValidationError({"main_service": "Specialists must select a main service."})

            # Ensure at least one sub-service is selected for specialists
            if not data.get('sub_services'):
                raise serializers.ValidationError({"sub_services": "Select at least one sub-service."})

            # Validate that selected sub-services belong to the main service
            main_service = data.get('main_service')
            for sub_service in data['sub_services']:
                if sub_service.main_service != main_service:
                    raise serializers.ValidationError({"sub_services": "All sub-services must match the main service."})

            # Require profile picture only for specialists
            if not data.get('profile_picture'):
                raise serializers.ValidationError({"profile_picture": "Specialists must have a profile picture."})

        return data

    def create(self, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', "")
        main_service = validated_data.pop('main_service', None)
        sub_services = validated_data.pop('sub_services', [])

        # Set status based on role
        if validated_data['role'] == 'specialist':
            validated_data['status'] = 'pending_approval'
        else:
            validated_data['status'] = 'approved'

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            status=validated_data['status'],
        )

        # Create the Profile and assign bio and profile_picture
        profile = Profile.objects.create(user=user)
        if profile_picture:
            profile.profile_picture = profile_picture
        if bio:
            profile.bio = bio
        profile.save()  # Save after assigning the fields

        # Assign services if the user is a specialist
        if user.role == 'specialist':
            specialist_service = SpecialistService.objects.create(specialist=user, main_service=main_service)
            specialist_service.sub_service.set(sub_services)
            specialist_service.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']