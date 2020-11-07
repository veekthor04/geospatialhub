from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
        
            return True
        
        # Write permissions are only allowed to the author of a post
        return obj == request.user

class IsPostOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, post):
        if request.method in permissions.SAFE_METHODS:
            return True
        return post.posted_by == request.user
