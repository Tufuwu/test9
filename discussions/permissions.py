"""Permissions for discussions"""

from rest_framework.permissions import BasePermission


class CanCreateChannel(BasePermission):
    """
    Only a django superuser can create channels
    """

    def has_permission(self, request, view):
        return request.user.is_superuser
