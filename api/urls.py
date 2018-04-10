from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token 
from .views import CreateView, HarvesterDetailsView, UserView, UserDetailsView
from . import views

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

urlpatterns = {
    path('', views.index, name='index'),
    path('harvesters/', 
        CreateView.as_view(), name="create"),
    path('harvesters/go/',
        views.run_harvesters, name="run_harvesters"),
    path('harvesters/<str:name>/',
        HarvesterDetailsView.as_view(), name="harvester-detail"),
    path('harvesters/<str:name>/start/',
        views.start_harvest, name="start-harvest"),
    path('harvesters/<str:name>/state/',
        views.get_harvester_state, name="harvester_status"),
    path('auth/', 
        include('rest_framework.urls', namespace='rest_framework')),
    path('users/', 
        UserView.as_view(), name="users"),
    path('users/<int:pk>/',
        UserDetailsView.as_view(), name="user-details"),
    path('get-token/', obtain_auth_token),
}

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])