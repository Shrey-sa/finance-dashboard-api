from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    """Only admins can proceed."""
    message = "Admin access required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == Role.ADMIN
        )


class IsAnalystOrAdmin(BasePermission):
    """Analysts and admins can proceed."""
    message = "Analyst or Admin access required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in (Role.ANALYST, Role.ADMIN)
        )


class IsActiveUser(BasePermission):
    """Reject inactive users."""
    message = "Your account is inactive."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
