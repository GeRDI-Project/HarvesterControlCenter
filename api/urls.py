from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from .views import HarvesterCreateView, HarvesterDetailsView, UserView, UserDetailsView

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

app_name = 'api'
urlpatterns = {
    path('', views.index, name='home'),
    path('harvesters/',
         HarvesterCreateView.as_view(), name="create"),
    path('harvesters/start',
         views.run_harvesters, name="run-harvesters"),
    path('harvesters/stop',
         views.stop_harvesters, name="stop-harvesters"),
    path('harvesters/<str:name>/',
         HarvesterDetailsView.as_view(), name="harvester-detail"),
    path('harvesters/<str:name>/start/',
         views.start_harvest, name="startharvest"),
    path('harvesters/<str:name>/stop/',
         views.stop_harvest, name="stopharvest"),
    path('harvesters/<str:name>/status/',
         views.get_harvester_state, name="harvester-status"),
    path('harvesters/status',
         views.get_harvester_states, name="all-harvester-status"),
    path('users/',
         UserView.as_view(), name="users"),
    path('users/<int:pk>/',
         UserDetailsView.as_view(), name="user-details"),
    path('get-token/', obtain_auth_token),
}

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])