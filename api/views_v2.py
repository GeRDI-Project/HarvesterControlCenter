from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, RedirectView
from rest_framework import status, generics, permissions
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.forms import HarvesterForm, SchedulerForm
from api.mixins import AjaxTemplateMixin
from api.models import Harvester
from api.permissions import IsOwner
from api.serializers import HarvesterSerializer, UserSerializer
from api.harvesterAPI import InitHarvester
from api.constants import HCCJSONConstants as HCCJC

import logging

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


# Get an instance of a logger
logger = logging.getLogger(__name__)


def index(request):
    """
    Index to show something meaningful instead of an empty page.
    :param request:
    :return: a HttpResponse
    """
    return HttpResponseRedirect(reverse('swagger-docs'))


@login_required
def toggle_harvester(request, name):
    """
    This function toggles the enabled and disabled status of an harvester.

    :param request: the request
    :param name: name of the harvester
    :return: an HttpResponseRedirect to the Main HCC page
    """
    harv = get_object_or_404(Harvester, name=name)
    if harv.enabled:
        harv.disable()
        messages.add_message(request, messages.INFO, name + ' harvester disabled.')
    else:
        harv.enable()
        messages.add_message(request, messages.INFO, name + ' harvester enabled.')
    return HttpResponseRedirect(reverse('hcc_gui'))


@login_required
def stop_harvester(request, name):
    """
    This function stops an harvester.

    :param request: the request
    :param name: name of the harvester
    :return: an HttpResponseRedirect to the Main HCC page
    """
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).getHarvesterApi()
    response = api.stopHarvest()
    messages.add_message(request, messages.INFO, name + ': ' + str(response.data[harvester.name]))
    return HttpResponseRedirect(reverse('hcc_gui'))


@login_required
def start_harvester(request, name):
    """
    This function starts an harvester.

    :param request: the request
    :param name: name of the harvester
    :return: an HttpResponseRedirect to the Main HCC page
    """
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).getHarvesterApi()
    response = api.startHarvest()
    messages.add_message(request, messages.INFO, name + ': ' + str(response.data[harvester.name]))
    return HttpResponseRedirect(reverse('hcc_gui'))

@login_required
def get_allHarvesterLog(request):
    """
    This function gets the harvester logfile.

    :param request: the request
    :return: JSON Feedback Array
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        if harvester.enabled:
            api = InitHarvester(harvester).getHarvesterApi()
            response = api.harvesterLog()
            feedback[harvester.name] = response.data[harvester.name]
            #messages.add_message(request, messages.INFO, name + ': ' + str(response.data[harvester.name]))
    return JsonResponse(feedback, status=status.HTTP_200_OK)

@login_required
def get_harvesterProgress(request, name):
    """
    This function gets the harvester progress.

    :param request: the request
    :return: JSON Feedback Array
    """
    feedback = {}
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).getHarvesterApi()
    response = api.harvesterProgress()
    feedback[harvester.name] = response.data[harvester.name]
    #messages.add_message(request, messages.INFO, name + ': ' + str(response.data[harvester.name]))
    return JsonResponse(feedback, status=response.status_code)

@login_required
def start_all_harvesters(request):
    """
    This function starts all harvesters.

    :param request: the request
    :return: an HttpResponseRedirect to the Main HCC page
    """
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        if harvester.enabled:
            api = InitHarvester(harvester).getHarvesterApi()
            response = api.startHarvest()
            if HCCJC.HEALTH in response.data[harvester.name]:
                messages.add_message(request, messages.INFO, harvester.name + ': ' + response.data[harvester.name][HCCJC.HEALTH])
            else:
                messages.add_message(request, messages.INFO,
                                     harvester.name + ': ' + str(response.data[harvester.name]))
    return HttpResponseRedirect(reverse('hcc_gui'))


@login_required
def abort_all_harvesters(request):
    """
    This function aborts all harvesters.

    :param request: the request
    :return: an HttpResponseRedirect to the Main HCC page
    """
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        if harvester.enabled:
            api = InitHarvester(harvester).getHarvesterApi()
            response = api.stopHarvest()
            if HCCJC.HEALTH in response.data[harvester.name]:
                messages.add_message(request, messages.INFO, harvester.name + ': ' + response.data[harvester.name][HCCJC.HEALTH])
            else:
                messages.add_message(request, messages.INFO,
                                     harvester.name + ': ' + str(response.data[harvester.name]))
    return HttpResponseRedirect(reverse('hcc_gui'))


# @login_required
def home(request):
    """
    Home entry point of Web-Application GUI
    """
    feedback = {}
    # init view-type for list and card view
    if 'viewtype' in request.GET:
        view_type = request.GET['viewtype']
    else:
        view_type = False

    # if user is logged in
    if request.user.is_authenticated:
        forms = {}
        harvesters = Harvester.objects.all()
        # get status of each enabled harvester
        for harvester in harvesters:
            # TODO do that call at client side!!
            api = InitHarvester(harvester).getHarvesterApi()
            response = api.harvesterStatus()
            if response:
                feedback[harvester.name] = response.data[harvester.name]
                if harvester.enabled:
                    if HCCJC.CRONTAB in response.data[harvester.name]:
                        # if a GET (or any other method) we'll create form initialized with schedule for this harvester 
                        form = SchedulerForm(initial={HCCJC.POSTCRONTAB : response.data[harvester.name][HCCJC.CRONTAB]}, prefix=harvester.name)
                        forms[harvester.name] = form
                    else:
                        form = SchedulerForm(initial={HCCJC.POSTCRONTAB : '0 0 * * *'}, prefix=harvester.name)
                        forms[harvester.name] = form
            else:
                form = SchedulerForm(initial={HCCJC.POSTCRONTAB : '0 0 * * *'}, prefix=harvester.name)
                forms[harvester.name] = form
                feedback[harvester.name] = {}
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                feedback[harvester.name][HCCJC.HEALTH] = 'Error : response object is not set'
        
        sum_harvested = 0
        sum_max_docs = 0
        for key, value in feedback.items():
            try:
                for k, v in value.items():
                    if k == HCCJC.CACHED_DOCS:
                        sum_harvested += v
                    if k == HCCJC.MAX_DOCUMENTS:
                        if v != 'N/A':
                            sum_max_docs += v
            except:
                pass
        feedback['sum_harvested'] = sum_harvested
        feedback['sum_maxdocs'] = sum_max_docs
        messages.add_message(request, messages.INFO, 'Total amount of harvested Items so far: ' + str(sum_harvested) + ' of ' + str(sum_max_docs))

        # init form
        if request.method == 'POST':
            form = SchedulerForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('hcc_gui'))

        # messages.debug(request, feedback)     
        return render(request, 'hcc/index.html', {'harvesters': harvesters, 'status': feedback, 'forms': forms, 'vt': view_type})

    return render(request, 'hcc/index.html', {'status': feedback, 'vt': view_type})


@api_view(['POST'])
# @authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def start_harvesters(request, format=None):
    """
    Start all Harvesters via POST request
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        api = InitHarvester(harvester).getHarvesterApi()
        response = api.startHarvest()
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def start_harvest(request, name, format=None):
    """
    Start Harvest via POST request to a harvester url
    """
    harvester = Harvester.objects.get(name=name)
    logger.info('Starting Harvester ' + harvester.name + '(' + str(harvester.owner) + ')')
    api = InitHarvester(harvester).getHarvesterApi()
    return api.startHarvest()


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def stop_harvest(request, name, format=None):
    """
    Stop Harvest via POST request to a harvester url
    """
    harvester = Harvester.objects.get(name=name)
    api = InitHarvester(harvester).getHarvesterApi()
    return api.stopHarvest()


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def stop_harvesters(request, format=None):
    """
    Stop all Harvesters via POST request to a harvester url
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        api = InitHarvester(harvester).getHarvesterApi()
        response = api.stopHarvest()
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_harvester_state(request, name, format=None):
    """
    View to show a Harvester state via GET Request
    """
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).getHarvesterApi()
    return api.harvesterStatus()


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_harvester_states(request, format=None):
    """
    View to show all Harvester states via GET Request
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        api = InitHarvester(harvester).getHarvesterApi()
        response = api.harvesterStatus()
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


class HarvesterCreateView(generics.ListCreateAPIView):
    """
    This class handles the GET and POST requests of our Harvester Control Center REST-API.
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


class ScheduleHarvesterView(SuccessMessageMixin, RedirectView):
    """

    This class handles GET, DELETE and POST requests to control the scheduling of harvesters.

    """
    success_message = "Schedule for %(name) was created successfully"

    @staticmethod
    def get(self, request, name):
        harvester = get_object_or_404(Harvester, name=name)
        pass
        #return Helpers.harvester_response_wrapper(harvester, 'GET_CRON', request)

    def post(self, request, name):
        harvester = get_object_or_404(Harvester, name=name)
        api = InitHarvester(harvester).getHarvesterApi()
        crontab = request.POST.get(name + "-" + HCCJC.POSTCRONTAB, False);
        if crontab:
            response = api.addSchedule(crontab)
        else:
            response = api.deleteSchedule(crontab)
        messages.add_message(request, messages.INFO, name + ': ' + response.data[harvester.name][HCCJC.HEALTH])
        return HttpResponseRedirect(reverse('hcc_gui'))

    def delete(self, request, name):
        harvester = get_object_or_404(Harvester, name=name)
        api = InitHarvester(harvester).getHarvesterApi()
        response = api.deleteSchedule(request.POST[HCCJC.POSTCRONTAB])
        messages.add_message(request, messages.INFO, name + ': ' + response.data[harvester.name][HCCJC.HEALTH])
        return HttpResponseRedirect(reverse('hcc_gui'))
