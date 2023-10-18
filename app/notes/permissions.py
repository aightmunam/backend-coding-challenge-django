from rest_framework import permissions


class IsCreatorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Object-level permission to only allow the creator of an object to edit it.
    Assumes the model instance has an `creator` attribute.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """
        Only grant object level permissions for Safe methods to non-creators.
        Only creators retain full access.
        """

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.creator == request.user
