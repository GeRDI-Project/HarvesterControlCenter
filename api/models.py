"""
Model Module; holds harvester model
"""
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class Harvester(models.Model):
    """
    This class represents the Harvester model which is also used for serialization.
    """
    hRegExVal = RegexValidator(
        r'^[0-9a-zA-Z_]+$',
        'Only alphanumeric characters and underscore are allowed.')

    name = models.CharField(max_length=255,
                            blank=False,
                            unique=True,
                            validators=[hRegExVal])
    metadataPrefix = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    enabled = models.BooleanField(default=False)
    owner = models.ForeignKey('auth.User',
                              related_name='harvester',
                              on_delete=models.CASCADE)
    url = models.URLField(max_length=255, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # TODO: Preparation for future Harvester registration
    # harvester_token = models.CharField(max_length=255, blank=True)
    # harvester_user = models.CharField(max_length=255, blank=True)
    # harvester_pass = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['name']

    def enable(self):
        """enable harvester"""
        self.enabled = True
        self.save()

    def disable(self):
        """disbale harvester"""
        self.enabled = False
        self.save()

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.name)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """ This receiver handles token creation immediately a new user is created."""
    if created:
        Token.objects.create(user=instance)
