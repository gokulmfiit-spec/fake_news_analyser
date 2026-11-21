from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allows access only to users with role='admin' or is_superuser."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == "admin" or user.is_superuser))


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner of the object, or an admin, can access it."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        owner = getattr(obj, "user", None)
        return bool(user.is_superuser or user.role == "admin" or owner == user)
