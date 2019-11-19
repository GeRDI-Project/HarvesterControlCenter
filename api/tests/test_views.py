"""
Testing Module for views_v2.py
"""
import urllib
from django.contrib.auth.models import User
from django.urls import include, path, reverse
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase
from unittest.mock import patch
# from unittest.mock import Mock, MagicMock

from api.models import Harvester
from api.constants import HCCJSONConstants as HCCJC

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
        response = self.client.get(reverse('api:user-details', kwargs={'pk': self.user.id}))
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('api.harvester_api_strategy.VersionBased7Strategy.post_start_harvest',
           return_value=Response({'Harvester1': 'ok'}, status.HTTP_200_OK))
    def test_start_harvest_view_calls_api(self, apicall):
        """Test the API command start-harvest with reverse lookup of the resource."""
        url = reverse('api:start-harvest', kwargs={'name': self.harvester.name})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, apicall())
        apicall.assert_called()

    @patch('api.harvester_api_strategy.VersionBased7Strategy.post_stop_harvest',
           return_value=Response({'Harvester1': "ok"}, status.HTTP_200_OK))
    def test_stop_harvest_view_calls_api(self, apicall):
        """Test the API command stop-harvest with reverse lookup of the resource."""
        url = reverse('api:stop-harvest', kwargs={'name': self.harvester.name})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, apicall())
        apicall.assert_called()

    @patch('api.harvester_api_strategy.VersionBased7Strategy.post_start_harvest',
           side_effect=[
               Response({'Harvester1': "ok"}, status.HTTP_200_OK),
               Response({"Harvester2": "ok"}, status.HTTP_200_OK)
           ])
    def test_start_harvesters_view_calls_api(self, apicall):
        """Test the API command run-harvesters with reverse lookup of the resource."""
        # create second harvester to have multiple harvesters in the test database
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        expected_output = {self.harvester.name: "ok", "Harvester2": "ok"}
        url = reverse('api:run-harvesters')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)
        self.assertEqual(apicall.call_count, 2)

    @patch('api.harvester_api_strategy.VersionBased7Strategy.post_stop_harvest',
           side_effect=[
               Response({'Harvester1': "ok"}, status.HTTP_200_OK),
               Response({"Harvester2": "ok"}, status.HTTP_200_OK)
           ])
    def test_stop_harvesters_view_calls_api(self, apicall):
        """Test the API command stop-harvesters with reverse lookup of the resource."""
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        expected_output = {self.harvester.name: "ok", "Harvester2": "ok"}
        url = reverse('api:stop-harvesters')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)
        self.assertEqual(apicall.call_count, 2)

    @patch('api.harvester_api_strategy.VersionBased7Strategy.get_harvester_status',
           return_value=Response({'Harvester1': "ok"}, status.HTTP_200_OK))
    def test_harvester_state_view_calls_api(self, apicall):
        """Test the API command harvester-status with reverse lookup of the resource."""
        url = reverse('api:harvester-status', kwargs={'name': self.harvester.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, apicall())
        apicall.assert_called()

    @patch('api.harvester_api_strategy.VersionBased7Strategy.get_harvester_status',
           side_effect=[
               Response({'Harvester1': "ok"}, status.HTTP_200_OK),
               Response({"Harvester2": "ok"}, status.HTTP_200_OK)
           ])
    def test_harvester_states_view_calls_api(self, apicall):
        """Test the API command get all-harvester-status with reverse lookup of the resource."""
        Harvester.objects.create(
            name="Harvester2",
            owner=self.user,
            url='http://somewhereelse.url/v1'
        )
        expected_output = {self.harvester.name: "ok", "Harvester2": "ok"}
        url = reverse('api:all-harvester-status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)
        self.assertEqual(apicall.call_count, 2)

    @patch('api.harvester_api_strategy.VersionBased7Strategy.post_add_harvester_schedule',
           return_value=Response({'Harvester1':{HCCJC.HEALTH: {"message": "ok"}}},
                                 status.HTTP_200_OK))
    def test_ScheduleHarvesterView_add_schedule_calls_api(self, apicall):
        """Test the API command get harvester-cron with reverse lookup of the resource."""
        url = reverse('api:harvester-cron', kwargs={'name': self.harvester.name})
        key = self.harvester.name + "-" + HCCJC.POSTCRONTAB
        data = {key: "crontab"}
        response = self.client.post(url, 
                                    urllib.parse.urlencode(data),
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"message": "ok"}')
        apicall.assert_called()

    @patch('api.harvester_api_strategy.VersionBased7Strategy.post_delete_harvester_schedule',
           return_value=Response({'Harvester1':{HCCJC.HEALTH: {"message": "ok"}}},
                                 status.HTTP_200_OK))
    def test_ScheduleHarvesterView_delete_schedules_calls_api(self, apicall):
        """Test the API command get harvester-cron with reverse lookup of the resource."""
        url = reverse('api:harvester-cron', kwargs={'name': self.harvester.name})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"message": "ok"}')
        apicall.assert_called()

    #-> does not work so far
    #
    #@patch('api.harvester_api_strategy.VersionBased7Strategy.post_delete_harvester_schedule',
    #       return_value=Response({'Harvester1':{HCCJC.HEALTH: {"message": "ok"}}},
    #                             status.HTTP_200_OK))
    #def test_ScheduleHarvesterView_delete_one_schedule_calls_api(self, apicall):
    #    """Test the API command get harvester-cron with reverse lookup of the resource."""
    #    url = reverse('api:harvester-cron', kwargs={'name': self.harvester.name})
    #    data = {HCCJC.POSTCRONTAB: "crontab"}
    #    response = self.client.delete(url, 
    #                                  urllib.parse.urlencode(data),
    #                                  content_type='application/x-www-form-urlencoded')
    #    self.assertEqual(response.status_code, status.HTTP_200_OK)
    #    apicall.assert_called()

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

        # Since user model instance is not serializable, use its Id/PK
        self.harvester = Harvester.objects.create(
            name='Harvester1',
            owner=self.user,
            url='http://somewhere.url/v1'
        )
