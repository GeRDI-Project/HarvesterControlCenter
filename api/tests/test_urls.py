"""
Testing Module for urls_v2.py and urls.py
"""
import os
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.urls import include, path, resolve, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase

from api.models import Harvester

__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class UrlsV2Tests(APITestCase, URLPatternsTestCase):
    """Test suite for the url paths."""
    urlpatterns = [
        path('v1/', include('api.urls_v2')),
    ]

    def setUp(self):
        """Define the test variables."""
        super(UrlsV2Tests, self).setUp()
        self.user = User.objects.create(username="ChuckNorris")
        self.harvester = Harvester.objects.create(
            name="Harvester1",
            owner=self.user,
            url='http://somewhere.url/v1'
        )

    def test_home_reverses_to_correct_url(self):
        """
        Test, if 'home' reverses to the correct url.
        """
        url = reverse('api:home')
        self.assertEqual(url, '/v1/')

    def test_home_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/' resolves to the correct view.
        """
        view = resolve('/v1/')
        self.assertEqual(view.func.__name__, 'index')

    def test_create_reverses_to_correct_url(self):
        """
        Test, if 'create' reverses to the correct url.
        """
        url = reverse('api:create')
        self.assertEqual(url, '/v1/harvesters/')

    def test_create_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/' resolves to the correct view.
        """
        view = resolve('/v1/harvesters/')
        self.assertEqual(view.func.__name__, 'HarvesterCreateView')

    def test_start_harvest_reverses_to_correct_url(self):
        """
        Test, if 'start-harvest' reverses to the correct url.
        """
        url = reverse('api:start-harvest', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/v1/harvesters/Harvester1/start/')

    def test_start_harvest_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/Harvester1/start/' resolves to the correct view.
        """
        view = resolve('/v1/harvesters/Harvester1/start/')
        self.assertEqual(view.func.__name__, 'start_harvest')

    def test_stop_harvest_reverses_to_correct_url(self):
        """
        Test, if 'stop-harvest' reverses to the correct url.
        """
        url = reverse('api:stop-harvest', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/v1/harvesters/Harvester1/stop/')

    def test_stop_harvest_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/Harvester1/stop/' resolves to the correct view.
        """
        view = resolve('/v1/harvesters/Harvester1/stop/')
        self.assertEqual(view.func.__name__, 'stop_harvest')

    def test_run_harvesters_reverses_to_correct_url(self):
        """
        Test, if 'run-harvesters' reverses to the correct url.
        """
        url = reverse('api:run-harvesters')
        self.assertEqual(url, '/v1/harvesters/start')

    def test_run_harvesters_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/start' resolves to the correct view.
        """
        view = resolve('/v1/harvesters/start')
        self.assertEqual(view.func.__name__, 'start_harvesters')

    def test_stop_harvesters_reverses_to_correct_url(self):
        """
        Test, if 'stop-harvesters' reverses to the correct url.
        """
        url = reverse('api:stop-harvesters')
        self.assertEqual(url, '/v1/harvesters/stop')

    def test_stop_harvesters_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/stop' resolves to the correct view.
        """
        view = resolve('/v1/harvesters/stop')
        self.assertEqual(view.func.__name__, 'stop_harvesters')

    def test_harvester_status_reverses_to_correct_url(self):
        """
        Test, if 'harvester-status' reverses to the correct url.
        """
        url = reverse('api:harvester-status', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/v1/harvesters/Harvester1/status/')

    def test_harvester_status_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/Harvester1/status/' resolves to the correct view.
        """
        view = resolve('/v1/harvesters/Harvester1/status/')
        self.assertEqual(view.func.__name__, 'get_harvester_state')

    def test_all_harvester_status_reverses_to_correct_url(self):
        """
        Test, if 'all-harvester-status' reverses to the correct url.
        """
        url = reverse('api:all-harvester-status')
        self.assertEqual(url, '/v1/harvesters/status')

    def test_all_harvester_status_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/status' resolves to the correct view
        """
        view = resolve('/v1/harvesters/status')
        self.assertEqual(view.func.__name__, 'get_harvester_states')

    def test_harvester_cron_reverses_to_correct_url(self):
        """
        Test, if 'harvester-cron' reverses to the correct url.
        """
        url = reverse('api:harvester-cron', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/v1/harvesters/Harvester1/schedule/')

    def test_harvester_cron_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/harvesters/Harvester1/schedule/' resolves to the correct view
        """
        view = resolve('/v1/harvesters/Harvester1/schedule/')
        self.assertEqual(view.func.__name__, 'ScheduleHarvesterView')

    def test_users_reverses_to_correct_url(self):
        """
        Test, if 'users' reverses to the correct url.
        """
        url = reverse('api:users')
        self.assertEqual(url, '/v1/users/')

    def test_users_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/users/' resolves to the correct view
        """
        view = resolve('/v1/users/')
        self.assertEqual(view.func.__name__, 'UserView')

    def test_user_details_reverses_to_correct_url(self):
        """
        Test, if 'user-details' reverses to the correct url.
        """
        url = reverse('api:user-details', kwargs={'pk': 1})
        self.assertEqual(url, '/v1/users/1/')

    def test_user_details_url_resolves_to_correct_view(self):
        """
        Test, if '/v1/users/1/' resolves to the correct view
        """
        view = resolve('/v1/users/1/')
        self.assertEqual(view.func.__name__, 'UserDetailsView')


class UrlsTests(APITestCase, URLPatternsTestCase):
    """Test suite for the url paths."""
    urlpatterns = [
        path('', include('hcc_py.urls')),
    ]

    def setUp(self):
        """Define the test variables."""
        super(UrlsTests, self).setUp()
        self.user = User.objects.create(username="ChuckNorris")
        self.harvester = Harvester.objects.create(
            name="Harvester1",
            owner=self.user,
            url='http://somewhere.url/v1'
        )

    def test_home_reverses_to_correct_url(self):
        """
        Test, if 'home' reverses to the correct url.
        """
        url = reverse('home')
        self.assertEqual(url, '/')

    def test_home_url_resolves_to_correct_view(self):
        """
        Test, if '/' resolves to the correct view.
        """
        view = resolve('/')
        self.assertEqual(view.func.__name__, 'index')

    def test_hcc_gui_reverses_to_correct_url(self):
        """
        Test, if 'hcc_gui' reverses to the correct url.
        """
        url = reverse('hcc_gui')
        self.assertEqual(url, '/hcc/')

    def test_hcc_gui_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/' resolves to the correct view.
        """
        view = resolve('/hcc/')
        self.assertEqual(view.func.__name__, 'home')

    def test_update_session_reverses_to_correct_url(self):
        """
        Test, if 'update-session' reverses to the correct url.
        """
        url = reverse('update-session')
        self.assertEqual(url, '/hcc/updatesession')

    def test_update_session_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/updatesession' resolves to the correct view.
        """
        view = resolve('/hcc/updatesession')
        self.assertEqual(view.func.__name__, 'update_session')

    def test_etls_reverses_to_correct_url(self):
        """
        Test, if 'etls' reverses to the correct url.
        """
        url = reverse('etls', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/Harvester1/etls')

    def test_etls_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/Harvester1/etls' resolves to the correct view.
        """
        view = resolve('/hcc/Harvester1/etls')
        self.assertEqual(view.func.__name__, 'harvester_status_history')

    def test_toggle_harvester_reverses_to_correct_url(self):
        """
        Test, if 'toggle-harvester' reverses to the correct url.
        """
        url = reverse('toggle-harvester', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/Harvester1/toggle')

    def test_toggle_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/Harvester1/toggle' resolves to the correct view.
        """
        view = resolve('/hcc/Harvester1/toggle')
        self.assertEqual(view.func.__name__, 'toggle_harvester')

    def test_toggle_harvesters_reverses_to_correct_url(self):
        """
        Test, if 'toggle-harvesters' reverses to the correct url.
        """
        url = reverse('toggle-harvesters', kwargs={'hnames': 'Harvester1'})
        self.assertEqual(url, '/hcc/toggle/Harvester1')

    def test_toggle_harvesters_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/toggle/Harvester1' resolves to the correct view.
        """
        view = resolve('/hcc/toggle/Harvester1')
        self.assertEqual(view.func.__name__, 'toggle_harvesters')

    def test_stop_harvester_reverses_to_correct_url(self):
        """
        Test, if 'stop-harvester' reverses to the correct url.
        """
        url = reverse('stop-harvester', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/Harvester1/stop')

    def test_stop_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/Harvester1/stop' resolves to the correct view.
        """
        view = resolve('/hcc/Harvester1/stop')
        self.assertEqual(view.func.__name__, 'stop_harvester')

    def test_start_harvester_reverses_to_correct_url(self):
        """
        Test, if 'start-harvester' reverses to the correct url.
        """
        url = reverse('start-harvester', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/Harvester1/start')

    def test_start_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/Harvester1/start' resolves to the correct view.
        """
        view = resolve('/hcc/Harvester1/start')
        self.assertEqual(view.func.__name__, 'start_harvester')

    def test_start_selected_harvesters_reverses_to_correct_url(self):
        """
        Test, if 'sart-selected-harvesters' reverses to the correct url.
        """
        url = reverse('start-selected-harvesters', kwargs={'hnames': 'Harvester1-Harvester2'})
        self.assertEqual(url, '/hcc/start/Harvester1-Harvester2')

    def test_start_selected_harvesters_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/start/Harvester1-Harvester2' resolves to the correct view.
        """
        view = resolve('/hcc/start/Harvester1-Harvester2')
        self.assertEqual(view.func.__name__, 'start_selected_harvesters')

    def test_reset_harvester_reverses_to_correct_url(self):
        """
        Test, if 'reset-harvester' reverses to the correct url.
        """
        url = reverse('reset-harvester', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/Harvester1/reset')

    def test_reset_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/Harvester1/reset' resolves to the correct view.
        """
        view = resolve('/hcc/Harvester1/reset')
        self.assertEqual(view.func.__name__, 'reset_harvester')

    def test_edit_harvester_reverses_to_correct_url(self):
        """
        Test, if 'edit-harvester' reverses to the correct url.
        """
        url = reverse('edit-harvester', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/edit/Harvester1')

    def test_edit_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/edit/Harvester1' resolves to the correct view.
        """
        view = resolve('/hcc/edit/Harvester1')
        self.assertEqual(view.func.__name__, 'EditHarvesterView')

    def test_add_harvester_reverses_to_correct_url(self):
        """
        Test, if 'add-harvester' reverses to the correct url.
        """
        url = reverse('add-harvester')
        self.assertEqual(url, '/hcc/add')

    def test_add_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/add' resolves to the correct view.
        """
        view = resolve('/hcc/add')
        self.assertEqual(view.func.__name__, 'EditHarvesterView')

    def test_config_harvester_reverses_to_correct_url(self):
        """
        Test, if 'config-harvester' reverses to the correct url.
        """
        url = reverse('config-harvester', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/config/Harvester1')

    def test_config_harvester_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/config/Harvester1' resolves to the correct view.
        """
        view = resolve('/hcc/config/Harvester1')
        self.assertEqual(view.func.__name__, 'ConfigHarvesterView')

    def test_start_harvesters_reverses_to_correct_url(self):
        """
        Test, if 'start-harvesters' reverses to the correct url.
        """
        url = reverse('start-harvesters')
        self.assertEqual(url, '/hcc/startall')

    def test_start_harvesters_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/startall' resolves to the correct view.
        """
        view = resolve('/hcc/startall')
        self.assertEqual(view.func.__name__, 'start_all_harvesters')

    def test_abort_harvesters_reverses_to_correct_url(self):
        """
        Test, if 'abort-harvesters' reverses to the correct url.
        """
        url = reverse('abort-harvesters')
        self.assertEqual(url, '/hcc/abortall')

    def test_abort_harvesters_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/abortall' resolves to the correct view.
        """
        view = resolve('/hcc/abortall')
        self.assertEqual(view.func.__name__, 'abort_all_harvesters')

    def test_harvester_log_reverses_to_correct_url(self):
        """
        Test, if 'harvesters-log' reverses to the correct url.
        """
        url = reverse('harvesters-log')
        self.assertEqual(url, '/hcc/logs')

    def test_harvester_log_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/logs' resolves to the correct view.
        """
        view = resolve('/hcc/logs')
        self.assertEqual(view.func.__name__, 'get_all_harvester_log')

    def test_hcc_log_reverses_to_correct_url(self):
        """
        Test, if 'hcc-log' reverses to the correct url.
        """
        url = reverse('hcc-log')
        self.assertEqual(url, '/hcc/hcclog')

    def test_hcc_log_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/hcclog' resolves to the correct view.
        """
        view = resolve('/hcc/hcclog')
        self.assertEqual(view.func.__name__, 'get_hcc_log')

    def test_harvester_progress_reverses_to_correct_url(self):
        """
        Test, if 'harvester-progress' reverses to the correct url.
        """
        url = reverse('harvester-progress', kwargs={'name': 'Harvester1'})
        self.assertEqual(url, '/hcc/Harvester1/progress')

    def test_harvester_progress_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/Harvester1/progress' resolves to the correct view.
        """
        view = resolve('/hcc/Harvester1/progress')
        self.assertEqual(view.func.__name__, 'get_harvester_progress')

    def test_harvester_to_file_reverses_to_correct_url(self):
        """
        Test, if 'harvester-to-file' reverses to the correct url.
        """
        url = reverse('harvester-to-file')
        self.assertEqual(url, '/hcc/saveharvesters')

    def test_harvester_to_file_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/saveharvesters' resolves to the correct view.
        """
        view = resolve('/hcc/saveharvesters')
        self.assertEqual(view.func.__name__, 'harvester_data_to_file')

    def test_harvester_from_file_reverses_to_correct_url(self):
        """
        Test, if 'harvester-from-file' reverses to the correct url.
        """
        url = reverse('harvester-from-file')
        self.assertEqual(url, '/hcc/loadharvesters')

    def test_harvester_from_file_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/loadharvesters' resolves to the correct view.
        """
        view = resolve('/hcc/loadharvesters')
        self.assertEqual(view.func.__name__, 'upload_file')

    def test_harvester_file_form_reverses_to_correct_url(self):
        """
        Test, if 'harvester-file-form' reverses to the correct url.
        """
        url = reverse('harvester-file-form')
        self.assertEqual(url, '/hcc/harvesterloadform')

    def test_harvester_file_form_url_resolves_to_correct_view(self):
        """
        Test, if '/hcc/harvesterloadform' resolves to the correct view.
        """
        view = resolve('/hcc/harvesterloadform')
        self.assertEqual(view.func.__name__, 'upload_file_form')

    def test_swagger_docs_reverses_to_correct_url(self):
        """
        Test, if 'swagger-docs' reverses to the correct url.
        """
        url = reverse('swagger-docs')
        self.assertEqual(url, '/docs/')

    def test_swagger_docs_url_resolves_to_correct_view(self):
        """
        Test, if '/docs/' resolves to the correct view.
        """
        view = resolve('/docs/')
        SCHEMA_VIEW = get_swagger_view(
            title='Harvester Control Center API',
            url=os.environ.get('FORCE_SCRIPT_NAME', '')
        )
        self.assertEqual(view.func.__name__, SCHEMA_VIEW.__name__)

    def test_login_url_resolves_to_correct_view(self):
        """
        Test, if '/accounts/login/' resolves to the correct view.
        """
        view = resolve('/accounts/login/')
        self.assertEqual(view.func.__name__, auth_views.LoginView.__name__)