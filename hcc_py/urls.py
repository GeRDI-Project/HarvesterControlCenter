"""hcc_py GUI URL Configuration

The `urlpatterns` list routes URLs to views_v2. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views_v2
    1. Add an import:  from my_app import views_v2
    2. Add a URL to urlpatterns:  path('', views_v2.home, name='home')
Class-based views_v2
    1. Add an import:  from other_app.views_v2 import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
# development settings for gunicorn!!
# from django.conf import settings
# from django.conf.urls.static import static
# end here
from rest_framework import permissions

from api import views_v2 as views
from api.forms import LoginForm
from api.views_v2 import ConfigHarvesterView, EditHarvesterView

# from rest_framework.documentation import include_docs_urls


__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


SCHEMA_VIEW = get_schema_view(
    openapi.Info(
        title="Harvester Control Center API",
        default_version='v1',
        description="This is an interactive Django REST-API Swagger documentation",
        terms_of_service="https://www.gerdi-project.eu/imprint/",
        contact=openapi.Contact(email="zbw@zbw.eu"),
        license=openapi.License(name="Apache 2.0 License"),
        url=os.environ.get('FORCE_SCRIPT_NAME', ''),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.index, name='home'),
    path('hcc/', views.home, name='hcc_gui'),
    path('hcc/updatesession', views.update_session, name='update-session'),
    path('hcc/<str:name>/etls', views.harvester_status_history, name='etls'),
    path(
        'hcc/<str:name>/toggle',
        views.toggle_harvester,
        name='toggle-harvester'),
    path(
        'hcc/toggle/<str:hnames>',
        views.toggle_harvesters,
        name='toggle-harvesters'),
    path('hcc/<str:name>/stop', views.stop_harvester, name='stop-harvester'),
    path(
        'hcc/<str:name>/start',
        views.start_harvester,
        name='start-harvester'),
    path('hcc/start/<str:hnames>',
         views.start_selected_harvesters,
         name='start-selected-harvesters'),
    path(
        'hcc/<str:name>/reset',
        views.reset_harvester,
        name='reset-harvester'),
    path(
        'hcc/edit/<str:name>',
        EditHarvesterView.as_view(),
        name='edit-harvester'),
    path('hcc/add', EditHarvesterView.as_view(), name='add-harvester'),
    path(
        'hcc/config/<str:name>',
        ConfigHarvesterView.as_view(),
        name='config-harvester'),
    path('hcc/startall', views.start_all_harvesters, name='start-harvesters'),
    path('hcc/abortall', views.abort_all_harvesters, name='abort-harvesters'),
    path('hcc/logs', views.get_all_harvester_log, name='harvesters-log'),
    path('hcc/hcclog', views.get_hcc_log, name='hcc-log'),
    path(
        'hcc/<str:name>/progress',
        views.get_harvester_progress,
        name='harvester-progress'),
    path(
        'hcc/saveharvesters',
        views.harvester_data_to_file,
        name="harvester-to-file"),
    path(
        'hcc/loadharvesters',
        views.upload_file,
        name="harvester-from-file"),
    path(
        'hcc/harvesterloadform',
        views.upload_file_form,
        name="harvester-file-form"),
    path('admin/', admin.site.urls),
    path('v1/', include('api.urls_v2', namespace='v1')),
    # switch to internal docs if swagger is insufficient
    # path('docs2/', include_docs_urls(title='HCC API Documentation',
    # schema_url=os.environ.get('FORCE_SCRIPT_NAME', '')), name='doc'),
    # path('swagger(?P<format>\.json|\.yaml)$', SCHEMA_VIEW.without_ui(cache_timeout=0), name='schema-json'),
    path(
        'docs/',
        SCHEMA_VIEW.with_ui(
            'swagger',
            cache_timeout=0),
        name='schema-swagger-ui'),
    # path('redoc/', SCHEMA_VIEW.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(
        'api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework')),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            authentication_form=LoginForm)),
    path('accounts/', include('django.contrib.auth.urls')),
]
# dev settings remove for production and use nginx as reverse proxy
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
