"""
Testing Module for views_v2.py
"""
import json
import os
import urllib
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files import File
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase

from api.constants import HCCJSONConstants as HCCJC
from api.models import Harvester

__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class ApiViewsTests(APITestCase, URLPatternsTestCase):
    """Test suite for the api views."""
    urlpatterns = [
        path('v1/', include('api.urls_v2')),
        path('', include('hcc_py.urls')),
    ]

    def setUp(self):
        """Define the test client and other test variables."""
        super(ApiViewsTests, self).setUp()
        self.user = User.objects.create(username="ChuckNorris")
        token = Token.objects.get(user__username='ChuckNorris')

        # Initialize client and force it to use authentication
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Since user model instance is not serializable, use its Id/PK
        self.harvester = Harvester.objects.create(
            name='Harvester1',
            owner=self.user,
            url='http://somewhere.url/v1'
        )
        self.harvester.enable()

    def test_api_can_create_a_harvester(self):
        """Test the api has harvester creation capability."""
        harvester_data = {
            'name': 'Harvester2',
            'owner': self.user.id,
            'url': 'http://somewhereElse.url/v1'
        }
        response = self.client.post(reverse('api:create'),
                                    harvester_data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization."""
        new_client = APIClient()
        response = new_client.get('/v1/harvesters/',
                                  kwargs={'pk': 3},
                                  format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_can_get_a_harvester(self):
        """Test the api can get a given harvester."""
        response = self.client.get('/v1/harvesters/',
                                   kwargs={'pk': self.harvester.id},
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.harvester)

    def test_api_can_update_harvester(self):
        """Test the api can update a given harvester."""
        change_harvester = {
            'name': 'newHarSilvester',
            'url': 'http://somewhat.url/v2/'
        }
        res = self.client.put(reverse('api:harvester-detail',
                                      kwargs={'name': self.harvester.name}),
                              change_harvester,
                              format='json')

        harvester = Harvester.objects.get(pk=1)
        self.assertEqual(harvester.name, change_harvester["name"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_harvester(self):
        """Test the api can delete a harvester."""
        response = self.client.delete(reverse('api:harvester-detail',
                                              kwargs={'name': self.harvester.name}),
                                      format='json',
                                      follow=True)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_api_can_see_list_of_users(self):
        """Test the api can see a list of all users."""
        response = self.client.get(reverse('api:users'))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_can_get_user(self):
        """Test the api can see a list of all users."""
        response = self.client.get(
            reverse(
                'api:user-details',
                kwargs={
                    'pk': self.user.id}))
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           return_value=Response({'Harvester1': 'dummy message'}, status.HTTP_200_OK))
    def test_start_harvest_view_calls_api(self, apicall):
        """Test the API command start-harvest with reverse lookup of the resource."""
        url = reverse(
            'api:start-harvest',
            kwargs={
                'name': self.harvester.name})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, apicall())
        apicall.assert_called()

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.stop_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_stop_harvest_view_calls_api(self, apicall):
        """Test the API command stop-harvest with reverse lookup of the resource."""
        url = reverse('api:stop-harvest', kwargs={'name': self.harvester.name})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, apicall())
        apicall.assert_called()

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_start_harvesters_view_calls_api(self, apicall):
        """Test the API command run-harvesters with reverse lookup of the resource."""
        # create second harvester to have multiple harvesters in the test
        # database
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        Harvester.objects.get(name="Harvester2").enable()
        expected_output = {
            self.harvester.name: "dummy message",
            "Harvester2": "dummy message"}
        url = reverse('api:run-harvesters')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)
        self.assertEqual(apicall.call_count, 2)

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.stop_harvest',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_stop_harvesters_view_calls_api(self, apicall):
        """Test the API command stop-harvesters with reverse lookup of the resource."""
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        Harvester.objects.get(name="Harvester2").enable()
        expected_output = {
            self.harvester.name: "dummy message",
            "Harvester2": "dummy message"}
        url = reverse('api:stop-harvesters')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)
        self.assertEqual(apicall.call_count, 2)

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_status',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_harvester_state_view_calls_api(self, apicall):
        """Test the API command harvester-status with reverse lookup of the resource."""
        url = reverse(
            'api:harvester-status',
            kwargs={
                'name': self.harvester.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, apicall())
        apicall.assert_called()

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_status',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_harvester_states_view_calls_api(self, apicall):
        """Test the API command get all-harvester-status with reverse lookup of the resource."""
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        Harvester.objects.get(name="Harvester2").enable()
        expected_output = {
            self.harvester.name: "dummy message",
            "Harvester2": "dummy message"}
        url = reverse('api:all-harvester-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)
        self.assertEqual(apicall.call_count, 2)

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.add_schedule',
           return_value=Response({'Harvester1': {HCCJC.HEALTH: {"message": "dummy message"}}},
                                 status.HTTP_200_OK))
    def test_ScheduleHarvesterView_add_schedule_calls_api(self, apicall):
        """Test the API command get harvester-cron with reverse lookup of the resource."""
        url = reverse(
            'api:harvester-cron',
            kwargs={'name': self.harvester.name})
        key = self.harvester.name + "-" + HCCJC.POSTCRONTAB
        data = {key: "dummy data"}
        response = self.client.post(url,
                                    urllib.parse.urlencode(data),
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"message": "dummy message"}')
        apicall.assert_called()

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.delete_schedule',
           return_value=Response({'Harvester1': {HCCJC.HEALTH: {"message": "dummy message"}}},
                                 status.HTTP_200_OK))
    def test_ScheduleHarvesterView_delete_schedules_calls_api(self, apicall):
        """Test the API command get harvester-cron with reverse lookup of the resource."""
        url = reverse(
            'api:harvester-cron',
            kwargs={
                'name': self.harvester.name})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"message": "dummy message"}')
        apicall.assert_called()

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.delete_schedule',
           return_value=Response({'Harvester1': {HCCJC.HEALTH: "dummy message"}},
                                 status.HTTP_200_OK))
    def test_ScheduleHarvesterView_delete_one_schedule_redirects(
            self, apicall):
        """Test the API command get harvester-cron with reverse lookup of the resource."""
        url = reverse(
            'api:harvester-cron',
            kwargs={
                'name': self.harvester.name})
        data = {HCCJC.POSTCRONTAB: "dummy data"}
        response = self.client.delete(url,
                                      json.dumps(data),
                                      content_type='application/json')
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.delete_schedule',
           return_value=Response({'Harvester1': {HCCJC.HEALTH: "dummy message"}},
                                 status.HTTP_200_OK))
    def test_ScheduleHarvesterView_delete_one_schedule_calls_api(
            self, apicall):
        """Test the API command get harvester-cron with reverse lookup of the resource."""
        url = reverse(
            'api:harvester-cron',
            kwargs={
                'name': self.harvester.name})
        data = {HCCJC.POSTCRONTAB: "dummy data"}
        self.client.delete(url,
                           json.dumps(data),
                           content_type='application/json')
        apicall.assert_called()


class ViewsTests(APITestCase, URLPatternsTestCase):
    """Test suite for the hcc views."""
    urlpatterns = [
        path('', include('hcc_py.urls')),
    ]

    def setUp(self):
        """Define the test client and other test variables."""
        super(ViewsTests, self).setUp()
        self.user = User.objects.create(username="ChuckNorris")
        token = Token.objects.get(user__username='ChuckNorris')

        # Initialize client and force it to use authentication
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.client.force_login(user=self.user)

        self.harvester = Harvester.objects.create(
            name='Harvester1',
            owner=self.user,
            url='http://somewhere.url/v1'
        )
        self.harvester.enable()

    def test_index_view(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    def test_toggle_harvester_login_required(self):
        self.client.logout()
        url = reverse("toggle-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/Harvester1/toggle')

    def test_toggle_harvester_view_redirects(self):
        url = reverse("toggle-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    def test_toggle_harvester_view_works(self):
        url = reverse("toggle-harvester", kwargs={"name": self.harvester.name})

        self.client.get(url)
        harvester = Harvester.objects.get(pk=1)
        self.assertFalse(harvester.enabled)

        self.client.get(url)
        harvester = Harvester.objects.get(pk=1)
        self.assertTrue(harvester.enabled)

    def test_toggle_harvesters_login_required(self):
        self.client.logout()
        url = reverse(
            "toggle-harvesters",
            kwargs={
                "hnames": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/toggle/Harvester1')

    def test_toggle_harvesters_view_redirects(self):
        url = reverse(
            "toggle-harvesters",
            kwargs={
                "hnames": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    def test_toggle_harvesters_view_works(self):
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        hnames = self.harvester.name + "-Harvester2"
        url = reverse("toggle-harvesters", kwargs={"hnames": hnames})

        self.client.get(url)
        harvester = Harvester.objects.get(pk=1)
        self.assertFalse(harvester.enabled)
        harvester = Harvester.objects.get(pk=2)
        self.assertTrue(harvester.enabled)

        self.client.get(url)
        harvester = Harvester.objects.get(pk=1)
        self.assertTrue(harvester.enabled)
        harvester = Harvester.objects.get(pk=2)
        self.assertFalse(harvester.enabled)

    def test_stop_harvester_login_required(self):
        self.client.logout()
        url = reverse("stop-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/Harvester1/stop')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.stop_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_stop_harvester_view_redirects(self, apicall):
        url = reverse("stop-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.stop_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_stop_harvester_view_calls_api(self, apicall):
        url = reverse("stop-harvester", kwargs={"name": self.harvester.name})
        self.client.get(url)
        apicall.assert_called()

    def test_start_harvester_login_required(self):
        self.client.logout()
        url = reverse("start-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/Harvester1/start')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_start_harvester_view_redirects(self, apicall):
        url = reverse("start-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_start_harvester_view_calls_api(self, apicall):
        url = reverse("start-harvester", kwargs={"name": self.harvester.name})
        self.client.get(url)
        apicall.assert_called()

    def test_start_selected_harvesters_login_required(self):
        self.client.logout()
        url = reverse(
            "start-selected-harvesters",
            kwargs={
                "hnames": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/start/Harvester1')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_start_selected_harvesters_view_redirects(self, apicall):
        url = reverse(
            "start-selected-harvesters",
            kwargs={
                "hnames": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_start_selected_harvesters_view_calls_api(self, apicall):
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        Harvester.objects.get(name="Harvester2").enable()
        hnames = self.harvester.name + "-Harvester2"
        url = reverse("start-selected-harvesters", kwargs={"hnames": hnames})
        self.client.get(url)
        self.assertEqual(apicall.call_count, 2)

    def test_reset_harvester_login_required(self):
        self.client.logout()
        url = reverse("reset-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/Harvester1/reset')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.reset_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_reset_harvester_view_redirects(self, apicall):
        url = reverse("reset-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.reset_harvest',
           return_value=Response({'Harvester1': "dummy message"}, status.HTTP_200_OK))
    def test_reset_harvester_view_calls_api(self, apicall):
        url = reverse("reset-harvester", kwargs={"name": self.harvester.name})
        self.client.get(url)
        apicall.assert_called()

    def test_edit_harvester_login_required(self):
        self.client.logout()
        url = reverse("edit-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/edit/Harvester1')

    def test_get_edit_harvester_view(self):
        url = reverse("edit-harvester", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.content)
        self.assertTemplateUsed('hcc/harvester_edit_form.html')

    def test_post_edit_harvester_view(self):
        url = reverse("edit-harvester", kwargs={"name": self.harvester.name})
        data = {
            "name": "Harvester2",
            "notes": "test note",
            "url": "http://somewhereelse.url/v1"
        }
        response = self.client.post(url,
                                    urllib.parse.urlencode(data),
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        harvester = Harvester.objects.get(name=data["name"])
        self.assertIsNotNone(harvester)
        self.assertEqual(harvester.url, data["url"])
        self.assertEqual(harvester.notes, data["notes"])
        self.assertTrue("message" in json.loads(response.content))

    def test_get_add_harvester_view(self):
        url = reverse("add-harvester")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.content)
        self.assertTemplateUsed('hcc/harvester_edit_form.html')

    def test_post_add_harvester_view(self):
        url = reverse("add-harvester")
        data = {
            "name": "Harvester2",
            "notes": "test note",
            "url": "http://somewhereelse.url/v1"
        }
        response = self.client.post(url,
                                    urllib.parse.urlencode(data),
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        harvester = Harvester.objects.get(name=data["name"])
        self.assertIsNotNone(harvester)
        self.assertEqual(harvester.url, data["url"])
        self.assertEqual(harvester.notes, data["notes"])
        self.assertTrue("message" in json.loads(response.content))

    def test_start_all_harvesters_login_required(self):
        self.client.logout()
        url = reverse("start-harvesters")
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/startall')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_start_all_harvesters_view_redirects(self, apicall):
        url = reverse("start-harvesters")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.start_harvest',
           side_effect=[
               Response({'Harvester1': {HCCJC.HEALTH: "dummy message"}},
                        status.HTTP_200_OK),
               Response({'Harvester2': {HCCJC.HEALTH: "dummy message"}},
                        status.HTTP_200_OK)
           ])
    def test_start_all_harvesters_view_calls_api(self, apicall):
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        Harvester.objects.get(name="Harvester2").enable()
        for harvester in Harvester.objects.all():
            harvester.enable()
        url = reverse("start-harvesters")
        self.client.get(url)
        self.assertEqual(apicall.call_count, 2)

    def test_abort_all_harvesters_login_required(self):
        self.client.logout()
        url = reverse("abort-harvesters")
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/abortall')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.stop_harvest',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK),
               Response({"Harvester2": "dummy message"}, status.HTTP_200_OK)
           ])
    def test_abort_all_harvesters_view_redirects(self, apicall):
        url = reverse("abort-harvesters")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("hcc_gui"))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.stop_harvest',
           side_effect=[
               Response({'Harvester1': {HCCJC.HEALTH: "dummy message"}},
                        status.HTTP_200_OK),
               Response({'Harvester2': {HCCJC.HEALTH: "dummy message"}},
                        status.HTTP_200_OK)
           ])
    def test_abort_all_harvesters_view_calls_api(self, apicall):
        harvester = Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        harvester.enable()
        url = reverse("abort-harvesters")
        self.client.get(url)
        self.assertEqual(apicall.call_count, 2)

    def test_harvesters_log_login_required(self):
        self.client.logout()
        url = reverse("harvesters-log")
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/logs')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_log',
           side_effect=[
               Response({'Harvester1': {HCCJC.LOGS: "dummy message"}},
                        status.HTTP_200_OK)
           ])
    def test_harvesters_log_view_response(self, apicall):
        url = reverse("harvesters-log")
        self.client.get(url)
        self.assertTemplateUsed('hcc/harvester_logs.html')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_log',
           side_effect=[
               Response({'Harvester1': {HCCJC.LOGS: "dummy message"}},
                        status.HTTP_200_OK),
               Response({"Harvester2": {HCCJC.LOGS: "dummy message"}},
                        status.HTTP_200_OK)
           ])
    def test_harvesters_log_view_calls_api(self, apicall):
        harvester = Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        harvester.enable()
        url = reverse("harvesters-log")
        self.client.get(url)
        self.assertEqual(apicall.call_count, 2)

    def test_hcc_log_login_required(self):
        self.client.logout()
        url = reverse("hcc-log")
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/hcclog')

    def test_hcc_log_view_response(self):
        url = reverse("hcc-log")
        response = self.client.get(url)
        self.assertTrue(response.content)

    def test_harvester_progress_login_required(self):
        self.client.logout()
        url = reverse(
            "harvester-progress",
            kwargs={
                "name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/Harvester1/progress')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_progress',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK)
           ])
    def test_harvester_progress_view_response(self, apicall):
        url = reverse(
            "harvester-progress",
            kwargs={
                "name": self.harvester.name})
        response = self.client.get(url)
        self.assertTrue(self.harvester.name in json.loads(response.content))

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_progress',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK)
           ])
    def test_harvester_progress_view_calls_api(self, apicall):
        url = reverse(
            "harvester-progress",
            kwargs={
                "name": self.harvester.name})
        self.client.get(url)
        apicall.assert_called()

    def test_harvester_to_file_view_login_required(self):
        self.client.logout()
        url = reverse("harvester-to-file")
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/saveharvesters')

    def test_harvester_to_file_view_response(self):
        url = reverse("harvester-to-file")
        response = self.client.get(url)
        data = [
            {
                "name": self.harvester.name,
                "notes": self.harvester.notes,
                "url": self.harvester.url,
                "enabled": self.harvester.enabled
            }
        ]
        self.assertEqual(json.loads(response.content), data)

    def test_harvester_file_form_view_response(self):
        url = reverse("harvester-file-form")
        self.client.get(url)
        self.assertTemplateUsed('hcc/file_upload_form.html')

    def test_harvester_from_file_redirects(self):
        file_mock = MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.json'
        url = reverse("harvester-from-file")
        response = self.client.post(url, {'upload_file': file_mock})
        self.assertRedirects(response, reverse("hcc_gui"))

    def test_harvester_from_file_no_changes(self):
        """
        When there are no changes in the uploaded file,
        the harvester should not be changed either.
        """
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)  # get current directory

        file_path = os.path.join(
            module_dir, 'test_files/valid_existing_harvester_no_changes.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        harvester = Harvester.objects.get(name=self.harvester.name)
        self.assertIsNotNone(harvester)
        self.assertEqual(harvester.notes, self.harvester.notes)
        self.assertEqual(harvester.url, self.harvester.url)
        self.assertEqual(harvester.enabled, self.harvester.enabled)

    def test_harvester_from_file_notes_and_enabled_changed(self):
        """
        Notes should never be updated. The enabled status should change.
        """
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(
            module_dir,
            'test_files/valid_existing_harvester_with_changes.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        harvester = Harvester.objects.get(name=self.harvester.name)
        self.assertIsNotNone(harvester)
        # notes should not be changed
        self.assertEqual(harvester.notes, self.harvester.notes)
        self.assertEqual(harvester.url, self.harvester.url)
        self.assertTrue(harvester.enabled)

    def test_harvester_from_file_url_changed(self):
        """
        When the name is already token, but the url is new, a new harvester
        should be created with the new url and the name gets the ending "_n",
        where n is 1,2,3,4,... the first not token name
        """
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(
            module_dir,
            'test_files/valid_existing_harvester_url_changes.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        # new harvesters should have been created
        harvester = Harvester.objects.get(pk=2)
        self.assertEqual(harvester.name, self.harvester.name + "_1")
        harvester = Harvester.objects.get(pk=3)
        self.assertEqual(harvester.name, self.harvester.name + "_2")
        # the last one was not created, because of an already existing url
        self.assertEqual(Harvester.objects.all().count(), 3)

    def test_harvester_from_file_new_harvester(self):
        """
        When the name and the url are new, create a new harvester.
        """
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(
            module_dir, 'test_files/valid_new_harvester.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertEqual(Harvester.objects.all().count(), 2)

    def test_harvester_from_file_name_changed(self):
        """
        When the name is new, but the url already exists, do not make changes.
        """
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(
            module_dir,
            'test_files/valid_existing_harvester_name_changes.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertEqual(Harvester.objects.all().count(), 1)

    def test_harvester_from_file_wrong_file_type(self):
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(module_dir, 'test_files/invalid_no_json.txt')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-warning")
        self.assertEqual(Harvester.objects.all().count(), 1)

    def test_harvester_from_file_no_content(self):
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(
            module_dir, 'test_files/invalid_no_content.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-warning")
        self.assertEqual(Harvester.objects.all().count(), 1)

    def test_harvester_from_file_wrong_content_keys(self):
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(module_dir,
                                 'test_files/invalid_wrong_content_keys.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-warning")
        self.assertEqual(Harvester.objects.all().count(), 1)

    def test_harvester_from_file_wrong_content_syntax(self):
        url = reverse("harvester-from-file")
        module_dir = os.path.dirname(__file__)

        file_path = os.path.join(
            module_dir, 'test_files/invalid_wrong_content_syntax.json')
        file = File(open(file_path, 'r'))
        response = self.client.post(url, {'upload_file': file}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-warning")
        self.assertEqual(Harvester.objects.all().count(), 1)

    def test_etls_login_required(self):
        self.client.logout()
        url = reverse("etls", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/Harvester1/etls')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.status_history',
           side_effect=[
               Response({'Harvester1': "dummy message"}, status.HTTP_200_OK)
           ])
    def test_etls_view(self, apicall):
        url = reverse("etls", kwargs={"name": self.harvester.name})
        response = self.client.get(url)
        self.assertTrue("message" in json.loads(response.content))
        apicall.assert_called()

    def test_update_session_login_required(self):
        self.client.logout()
        url = reverse("update-session")
        response = self.client.get(url)
        self.assertRedirects(
            response, '/api-auth/login/?next=/hcc/updatesession')

    def test_update_session_view(self):
        url = reverse("update-session")
        # should only take post ajax requests
        response = self.client.get(url)
        self.assertEqual(json.loads(response.content)["status"], "failed")
        data = {
            "csrfmiddlewaretoken": "somecsrf",
            "theme": "dark"
        }
        response = self.client.post(url,
                                    urllib.parse.urlencode(data),
                                    content_type='application/x-www-form-urlencoded',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(json.loads(response.content)["status"], "ok")

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_status',
           return_value=Response({'Harvester1': {HCCJC.CRONTAB: HCCJC.NO_CRONTAB}},
                                 status.HTTP_200_OK))
    def test_hcc_gui_view_response(self, apicall):
        url = reverse("hcc_gui")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed('hcc/index.html')

    @patch('api.harvester_api_strategy.HarvesterApiStrategy.harvester_status',
           return_value=Response({'Harvester1': {HCCJC.CRONTAB: HCCJC.NO_CRONTAB}},
                                 status.HTTP_200_OK))
    def test_hcc_gui_view_calls_api(self, apicall):
        url = reverse("hcc_gui")
        self.client.get(url)
        apicall.assert_called()
