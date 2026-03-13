from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a club to edit or post.
    Anyone can make a get request
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if the object is the Club itself or has a link to the club owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'club'):
            return obj.club.owner == request.user
        return False