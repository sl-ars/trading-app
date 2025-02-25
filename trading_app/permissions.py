from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """ Allows only Admin users. """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()

class IsManager(permissions.BasePermission):
    """ Allows only Manager users. """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager()

class IsSeller(permissions.BasePermission):
    """ Allows only Seller users. """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller()

class IsCustomer(permissions.BasePermission):
    """ Allows only Customer users. """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer()

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows only the owner of the object or an Admin to modify it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_admin()

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission that allows only admin users to modify objects.
    Other users can only view them.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow modification (POST, PUT, DELETE) only for admins
        return request.user.is_authenticated and request.user.is_admin()