from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from .models import Harvester

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

TokenAdmin.raw_id_fields = ('user',)

# Register your models here.
admin.site.register(Harvester)
