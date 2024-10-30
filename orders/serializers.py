from rest_framework import serializers
from .models import Order, Proposal
from services.models import MainService, SubService


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'sub_service', 'description', 'suggested_price', 'scheduled_date', 'address',
                  'status', 'created_at']
        read_only_fields = ['id', 'customer', 'status', 'created_at']


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['id', 'order', 'specialist', 'proposed_price', 'estimated_duration', 'created_at']
        read_only_fields = ['id', 'order', 'specialist', 'created_at']


class SubServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubService
        fields = ['id', 'name', 'description', 'base_price']


class MainServiceSerializer(serializers.ModelSerializer):
    sub_services = SubServiceSerializer(many=True, read_only=True)

    class Meta:
        model = MainService
        fields = ['id', 'name', 'sub_services']
