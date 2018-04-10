from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.test import APIClient
from requests.exceptions import ConnectionError
from .permissions import IsOwner
from .serializers import HarvesterSerializer, UserSerializer
from .models import Harvester
from .harvester_api import Harvester_API
from .helpers import Helpers
import requests

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

def index(request):
    return HttpResponse('Chuck Norris will never have a heart attack. His heart isnt nearly foolish enough to attack him.')

@api_view(["POST"])
@authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated, ))
def run_harvesters(request, format=None):
    """
    Start all Harvesters via POST request
    """
    feedback = []
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        #Helpers.harvester_response_wrapper(harvester, 'POST')
        if harvester.enabled == True:
            try:
                response = requests.post(Harvester_API.HTTP_PROTOCOL + harvester.url + Harvester_API.P_HARVEST, stream=True)
                if response.status_code == 200:
                    feedback.append(harvester.name + ' : ' + response.text)
                elif response.status_code == 404:
                    feedback.append(harvester.name + ' : Resource on server not found. Check URL.')
                else:
                    feedback.append(harvester.name + ' : ' + response.text)
                    
            except ConnectionError as e:
                feedback.append(harvester.name + ' has a Connection Error. Host probably down.')
        else:
            feedback.append(harvester.name + ' : disabled.')     
            
    return Response(feedback, status=status.HTTP_200_OK)

    
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def start_harvest(request, name, format=None):
    """
    Start Harvest via POST request to a harvester url
    """
    harvester = Harvester.objects.get(name=name)
    
    return Helpers.harvester_response_wrapper(harvester, 'POST')
   
        
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_harvester_state(request, name, format=None):
    """
    View to show a Harvester state via GET Request
    """
    harvester = get_object_or_404(Harvester, name=name)
    return Helpers.harvester_response_wrapper(harvester, 'GET')


class CreateView(generics.ListCreateAPIView):
    """This class handles the GET and POST requests of our Harvester-Controlcenter rest api."""
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    queryset = Harvester.objects.all()
    serializer_class = HarvesterSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new harvester."""
        serializer.save(owner=self.request.user)

        
class HarvesterDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles GET, PUT, PATCH and DELETE requests."""
    authentication_classes = (BasicAuthentication, )
    lookup_field = 'name'
    queryset = Harvester.objects.all()
    serializer_class = HarvesterSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    

class UserView(generics.ListAPIView):
    """View to list the user queryset."""
    authentication_classes = (BasicAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """View to retrieve a user instance."""
    authentication_classes = (BasicAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer