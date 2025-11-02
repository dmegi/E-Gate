from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    message = "Access denied: Admins only."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "is_admin", False))


class IsResidentUserRole(BasePermission):
    message = "Access denied: Residents only."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and getattr(user, "is_resident", False))

