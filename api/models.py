from __future__ import unicode_literals
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

# A harvester model which is also used for serialization
class Harvester(models.Model):
    """This class represents the Harvester model."""
    name = models.CharField(max_length=255, blank=False, unique=True)
    metadataPrefix = models.CharField(max_length=255, blank=True)
    repository = models.CharField(max_length=255, blank=True)
    enabled = models.BooleanField(default=False)
    owner = models.ForeignKey(
        'auth.User',
        related_name='harvester', on_delete=models.CASCADE)
    url = models.URLField(max_length=255, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def enable(self):
        self.enabled = True
        self.save()

    def disable(self):
        self.enabled = False
        self.save()

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.name)

# This receiver handles token creation immediately a new user is created.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
