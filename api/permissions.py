from rest_framework.permissions import BasePermission
from .models import Harvester

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

class IsOwner(BasePermission):
    """Custom permission class to allow only harvester owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the harvester owner."""
        if isinstance(obj, Harvester):
            return obj.owner == request.user
        return obj.owner == request.user