from django.test import TestCase
from django.urls import include, path, reverse, resolve
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, URLPatternsTestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import Harvester

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

class ModelTestCase(TestCase):
    """This class defines the test suite for the harvester model."""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="Borat")
        self.name = "If you read this, you might be a little curious"
        # specify owner of a harvester
        self.harvester = Harvester(name=self.name, owner=user)

    def test_model_can_create_a_harvester(self):
        """Test the harvester model can create a harvester."""
        old_count = Harvester.objects.count()
        self.harvester.save()
        new_count = Harvester.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_returns_readable_representation(self):
        """Test a readable string is returned for the model instance."""
        self.assertEqual(str(self.harvester), self.name)


class ViewsTests(APITestCase, URLPatternsTestCase):
    """Test suite for the api views."""
    urlpatterns = [
        path('v1/', include('api.urls')),
    ]

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="ChuckNorris")
        token = Token.objects.get(user__username='ChuckNorris')

        # Initialize client and force it to use authentication
        self.client = APIClient()
        self.client.force_authenticate(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # Since user model instance is not serializable, use its Id/PK
        self.harvester_data = {
            'name': 'HellHarvester',
            'owner': user.id,
            'url': 'http://somewhere.url/v1/'
        }
        self.response = self.client.post(
            reverse('api:create'),
            self.harvester_data,
            format="json")

    def test_startharvesters_view_status_code(self):
        url = reverse('api:run-harvesters')
        response = self.client.post(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_harvestersgo_url_resolves_run_harvesters_view(self):
        view = resolve('/v1/harvesters/start')
        self.assertEquals(view.url_name, 'run-harvesters')

    def test_api_can_create_a_harvester(self):
        """Test the api has harvester creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization."""
        new_client = APIClient()
        res = new_client.get(
            '/v1/harvesters/',
            kwargs={'pk': 3},
            format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_can_get_a_harvester(self):
        """Test the api can get a given harvester."""
        harvester = Harvester.objects.get(id=1)
        response = self.client.get(
            '/v1/harvesters/',
            kwargs={'pk': harvester.id},
            format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, harvester)

    def test_api_can_update_harvester(self):
        """Test the api can update a given harvester."""
        harvester = Harvester.objects.get()
        change_harvester = {'name': 'newHarSilvester', 'url': 'http://somewhat.url/v2/'}
        res = self.client.put(
            reverse('api:harvester-detail', kwargs={'name': harvester.name}),
            change_harvester,
            format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_harvester(self):
        """Test the api can delete a harvester."""
        harvester = Harvester.objects.get()
        response = self.client.delete(
            reverse('api:harvester-detail', kwargs={'name': harvester.name}),
            format='json',
            follow=True)

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
