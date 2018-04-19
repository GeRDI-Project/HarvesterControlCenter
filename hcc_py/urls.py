"""hcc_py URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
# development settings for gunicorn!!
#from django.conf import settings
#from django.conf.urls.static import static
# end here
from rest_framework_swagger.views import get_swagger_view
from api import views

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

schema_view = get_swagger_view(title='Harvester ControlCenter API')

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
    path('v1/', include(('api.urls'), namespace='v1')),
    path('docs/', schema_view),
    path('auth/',
         include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) #dev settings remove for production and use nginx as reverse proxy
