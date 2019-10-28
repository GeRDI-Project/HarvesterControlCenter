"""
Permission Module
"""
from rest_framework import permissions

from .models import Harvester

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class IsOwner(permissions.BasePermission):
    """Custom permission class to allow only harvester owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the harvester owner."""
        if isinstance(obj, Harvester):
            return obj.owner == request.user

        # Write permissions are only allowed to the owner of the harvester.
        return obj.owner == request.user
