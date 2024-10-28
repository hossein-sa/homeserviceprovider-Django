from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
        Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsCustomer(BasePermission):
    """
    Allows access only to customers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'


class IsSpecialist(BasePermission):
    """
    Allows access only to specialists.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'specialist'
