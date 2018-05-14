from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from rest_framework import status, generics, permissions
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.forms import HarvesterForm
from api.helpers import Helpers
from api.mixins import AjaxTemplateMixin
from api.models import Harvester
from api.permissions import IsOwner
from api.serializers import HarvesterSerializer, UserSerializer

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


def index(request):
    return HttpResponse('Chuck Norris will never have a heart attack. His heart \
                        isn\'t nearly foolish enough to attack him.')


@login_required
def toggle_harvester(request, name):
    harv = get_object_or_404(Harvester, name=name)
    if harv.enabled is True:
        harv.disable()
    else:
        harv.enable()
    return HttpResponseRedirect('/hcc/')


# @login_required
def home(request):
    """
    Home Entrypoint of GUI Web-Application
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        response = Helpers.harvester_response_wrapper(harvester, 'GET_STATUS')
        feedback[harvester.name] = response.data[harvester.name]
    return render(request, 'hcc/index.html', {'harvesters': harvesters, 'status': feedback})


@api_view(['POST'])
# @authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def run_harvesters(request, format=None):
    """
    Start all Harvesters via POST request
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        response = Helpers.harvester_response_wrapper(harvester, 'POST_STARTH')
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def start_harvest(request, name, format=None):
    """
    Start Harvest via POST request to a harvester url
    """
    harvester = Harvester.objects.get(name=name)
    return Helpers.harvester_response_wrapper(harvester, 'POST_STARTH')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def stop_harvest(request, name, format=None):
    """
    Stop Harvest via POST request to a harvester url
    """
    harvester = Harvester.objects.get(name=name)
    return Helpers.harvester_response_wrapper(harvester, 'POST_STOPH')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def stop_harvesters(request, format=None):
    """
    Stop all Harvesters via POST request to a harvester url
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        response = Helpers.harvester_response_wrapper(harvester, 'POST_STOPH')
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_harvester_state(request, name, format=None):
    """
    View to show a Harvester state via GET Request
    """
    harvester = get_object_or_404(Harvester, name=name)
    return Helpers.harvester_response_wrapper(harvester, 'GET_STATUS')


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_harvester_states(request, format=None):
    """
    View to show all Harvester states via GET Request
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        response = Helpers.harvester_response_wrapper(harvester, 'GET_STATUS')
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


class HarvesterCreateView(generics.ListCreateAPIView):
    """
    This class handles the GET and POST requests of our Harvester-Controlcenter rest api.
    """
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    queryset = Harvester.objects.all()
    serializer_class = HarvesterSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new harvester."""
        serializer.save(owner=self.request.user)


class HarvesterDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    This class handles GET, PUT, PATCH and DELETE requests.
    """
    authentication_classes = (BasicAuthentication,)
    lookup_field = 'name'
    queryset = Harvester.objects.all()
    serializer_class = HarvesterSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)


class UserView(generics.ListAPIView):
    """
    View to list the user queryset.
    """
    authentication_classes = (BasicAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """
    View to retrieve a user instance.
    """
    authentication_classes = (BasicAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterHarvesterFormView(SuccessMessageMixin, AjaxTemplateMixin, FormView):
    """
    This class handles GUI Harvester registration.
    """
    template_name = 'hcc/hreg_form.html'
    form_class = HarvesterForm
    success_url = reverse_lazy('hcc_gui')
    success_message = "New Harvester (%(name)s) successfully registered!"

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        harv_w_user = Harvester(owner=self.request.user)
        form = HarvesterForm(self.request.POST, instance=harv_w_user)
        form.save()
        return super().form_valid(form)
