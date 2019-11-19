"""
Testing Module for the model "Harvester"
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError

from api.forms import HarvesterForm
from api.models import Harvester

__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class ModelTestCase(TestCase):
    """This class defines the test suite for the harvester model."""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="AnyUser")
        self.name = "Harvester1"
        # specify owner of a harvester
        self.harvester = Harvester.objects.create(name=self.name, owner=user, url='http://somewhere.url/v1')

    def test_model_can_create_a_harvester(self):
        """Test the harvester model can create a harvester."""
        self.assertIsNotNone(self.harvester)

    def test_harvester_default_values(self):
        """Test if the default values are correct"""
        self.assertFalse(self.harvester.enabled)
        self.assertEqual(self.harvester.notes, "")

    def test_harvester_can_be_edited_correctly(self):
        """Test if editing works correctly"""
        new_name = "Harvester1_new"
        self.harvester.name = new_name
        self.harvester.save()
        self.assertEqual(self.harvester.name, new_name)

        new_url = "'http://somewhereElse.url/v1'"
        self.harvester.url = new_url
        self.harvester.save()
        self.assertEqual(self.harvester.url, new_url)

        new_notes = "some notes"
        self.harvester.notes = new_notes
        self.harvester.save()
        self.assertEqual(self.harvester.notes, new_notes)

    def test_harvester_enable_and_disable_function(self):
        """Test if the enable() and disable() functions work correctly"""
        self.harvester.enable()
        self.assertTrue(self.harvester.enabled)

        self.harvester.disable()
        self.assertFalse(self.harvester.enabled)

    def test_regex_validator_works(self):
        """Test if the regex validator works"""
        dash_name = "bad-name"
        self.harvester.name = dash_name
        self.assertRaises(ValidationError, self.harvester.save())

    def test_harvester_returns_readable_representation(self):
        """Test a readable string is returned for the model instance."""
        self.assertEqual(str(self.harvester), self.name)


class RegexTestCase(TestCase):
    """This class defines the test for harvester name registration."""

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        User.objects.create(username='Prometheus')

    def test_harvester_form_is_valid(self):
        """Test the regex for harvester name."""
        user = User.objects.get(id=1)
        url = "http://www.isgoing.to/api"
        data = {
            'name': "foo_bar1",
            'owner': user,
            'url': url,
        }
        form = HarvesterForm(data=data)
        self.assertTrue(form.is_valid())

    def test_harvester_form_is_invalid(self):
        """Test the regex for harvester name."""
        user = User.objects.get(id=1)
        url = "http://www.isgoing.to/api"
        data = {
            'name': "foo bar@1",
            'owner': user,
            'url': url,
        }
        form = HarvesterForm(data=data)
        self.assertFalse(form.is_valid())

        data = {
            'name': 'bad-name',
            'owner': user,
            'url': url
        }
        form = HarvesterForm(data=data)
        self.assertFalse(form.is_valid())
