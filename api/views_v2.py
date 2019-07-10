"""
The is the views module which encapsulates the backend logic
"""
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, RedirectView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from rest_framework import status, generics, permissions
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.forms import HarvesterForm, SchedulerForm, create_config_form
from api.mixins import AjaxTemplateMixin, AjaxableResponseMixin
from api.models import Harvester
from api.permissions import IsOwner
from api.serializers import HarvesterSerializer, UserSerializer
from api.harvester_api import InitHarvester
from api.constants import HCCJSONConstants as HCCJC

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)


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
        LOGGER.info("%s disabled.", harv.name)
        messages.add_message(request, messages.INFO,
                             name + ' harvester disabled.')
    else:
        harv.enable()
        LOGGER.info("%s enabled.", harv.name)
        messages.add_message(request, messages.INFO,
                             name + ' harvester enabled.')
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
    api = InitHarvester(harvester).get_harvester_api()
    response = api.stop_harvest()
    messages.add_message(request, messages.INFO,
                         name + ': ' + str(response.data[harvester.name]))
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
    api = InitHarvester(harvester).get_harvester_api()
    response = api.start_harvest()
    messages.add_message(request, messages.INFO,
                         name + ': ' + str(response.data[harvester.name]))
    return HttpResponseRedirect(reverse('hcc_gui'))


@login_required
def reset_harvester(request, name):
    """
    This function resets an harvester.

    :param request: the request
    :param name: name of the harvester
    :return: an HttpResponseRedirect to the Main HCC page
    """
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).get_harvester_api()
    response = api.reset_harvest()
    messages.add_message(request, messages.INFO,
                         name + ': ' + str(response.data[harvester.name]))
    return HttpResponseRedirect(reverse('hcc_gui'))


@login_required
def get_all_harvester_log(request):
    """
    This function gets the logfile for each harvester.

    :param request: the request
    :return: JSON Feedback Array
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        if harvester.enabled:
            api = InitHarvester(harvester).get_harvester_api()
            response = api.harvester_log()
            feedback[harvester.name] = response.data[harvester.name]
    return JsonResponse(feedback, status=status.HTTP_200_OK)


@login_required
def get_hcc_log(request):
    """ A function to get the hcc logfile -> [settings.py] ./log/debug.log """
    filename = settings.LOGGING['handlers']['filedebug']['filename']
    content = filename + "<br>"
    with open(filename, 'r') as file:
        content += file.read().replace('\n', '<br>')
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return response


@login_required
def get_harvester_progress(request, name):
    """
    This function gets the harvester progress.

    :param request: the request
    :return: JSON Feedback Array
    """
    feedback = {}
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).get_harvester_api()
    response = api.harvester_progress()
    feedback[harvester.name] = response.data[harvester.name]
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
            api = InitHarvester(harvester).get_harvester_api()
            response = api.start_harvest()
            if HCCJC.HEALTH in response.data[harvester.name]:
                msg = harvester.name + ': ' + response.data[harvester.name][
                    HCCJC.HEALTH]
                messages.add_message(request, messages.INFO, msg)
            else:
                msg = harvester.name + ': ' + str(
                    response.data[harvester.name])
                messages.add_message(request, messages.INFO, msg)

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
            api = InitHarvester(harvester).get_harvester_api()
            response = api.stop_harvest()
            if HCCJC.HEALTH in response.data[harvester.name]:
                msg = harvester.name + ': ' + response.data[harvester.name][
                    HCCJC.HEALTH]
                messages.add_message(request, messages.INFO, msg)
            else:
                msg = harvester.name + ': ' + str(
                    response.data[harvester.name])
                messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse('hcc_gui'))


# @login_required
def home(request):
    """
    Home entry point of Web-Application GUI.
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
        response = None
        harvesters = Harvester.objects.all()
        num_harvesters = len(harvesters)
        num_enabled_harvesters = 0
        num_disabled_harvesters = 0
        # get status of each enabled harvester
        for harvester in harvesters:
            # TODO do that call at client side!!
            if harvester.enabled:
                num_enabled_harvesters += 1
                api = InitHarvester(harvester).get_harvester_api()
                response = api.harvester_status()
                if response:
                    feedback[harvester.name] = response.data[harvester.name]

                    if HCCJC.CRONTAB in response.data[harvester.name]:
                        # if a GET (or any other method) we'll create form
                        # initialized with a schedule for this harvester
                        jsonstr = {
                            HCCJC.POSTCRONTAB:
                            response.data[harvester.name][HCCJC.CRONTAB]
                        }
                        placehldr = response.data[harvester.name][
                            HCCJC.CRONTAB]
                        form = SchedulerForm(prefix=harvester.name)
                        if isinstance(placehldr, list):
                            if len(placehldr) > 0:
                                placehldr = response.data[harvester.name][HCCJC.CRONTAB][0]
                        form.fields[HCCJC.POSTCRONTAB].widget.attrs.update(
                            {'placeholder': placehldr})
                        forms[harvester.name] = form
                    else:
                        jsonstr = {HCCJC.POSTCRONTAB: '0 0 * * *'}
                        form = SchedulerForm(initial=jsonstr,
                                             prefix=harvester.name)
                        forms[harvester.name] = form
                else:
                    jsonstr = {HCCJC.POSTCRONTAB: '0 0 * * *'}
                    form = SchedulerForm(initial=jsonstr,
                                         prefix=harvester.name)
                    forms[harvester.name] = form
                    feedback[harvester.name] = {}
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    feedback[harvester.name][
                        HCCJC.HEALTH] = 'Error : no response object'
            else:
                num_disabled_harvesters += 1

        # get total amount of docs
        sum_harvested = 0
        sum_max_docs = 0
        for harvester in feedback.values():
            if isinstance(harvester, dict):
                for (_k, _v) in harvester.items():
                    if _k == HCCJC.CACHED_DOCS:
                        sum_harvested += int(_v)
                    if _k == HCCJC.MAX_DOCUMENTS:
                        if _v != 'N/A':
                            sum_max_docs += int(_v)

        feedback['sum_harvested'] = sum_harvested
        feedback['sum_maxdocs'] = sum_max_docs
        feedback['num_disabled_harvesters'] = num_disabled_harvesters
        feedback['num_enabled_harvesters'] = num_enabled_harvesters
        feedback['num_harvesters'] = num_harvesters
        msg = '{} enabled Harvesters with total amount \
               of harvested Items so far: {}'.format(num_enabled_harvesters,
                                                     sum_harvested)
        messages.add_message(request, messages.INFO, msg)

        # init form
        if request.method == 'POST':
            form = SchedulerForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('hcc_gui'))

        return render(
            request, 'hcc/index.html', {
                'harvesters': harvesters,
                'status': feedback,
                'forms': forms,
                'vt': view_type
            })

    return render(request, 'hcc/index.html', {
        'status': feedback,
        'vt': view_type
    })


@api_view(['POST'])
# @authentication_classes((TokenAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated, ))
def start_harvesters(request, format=None):
    """
    Start all harvesters via POST request.
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        api = InitHarvester(harvester).get_harvester_api()
        response = api.start_harvest()
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def start_harvest(request, name, format=None):
    """
    Start harvest via POST request to an harvester url-endpoint.
    """
    harvester = Harvester.objects.get(name=name)
    api = InitHarvester(harvester).get_harvester_api()
    return api.start_harvest()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def stop_harvest(request, name, format=None):
    """
    Stop harvest via POST request to an harvester url-endpoint.
    """
    harvester = Harvester.objects.get(name=name)
    api = InitHarvester(harvester).get_harvester_api()
    return api.stop_harvest()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def stop_harvesters(request, format=None):
    """
    Stop all harvesters via POST request.
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        api = InitHarvester(harvester).get_harvester_api()
        response = api.stop_harvest()
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_harvester_state(request, name, format=None):
    """
    View to show an harvester state via GET request.
    """
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).get_harvester_api()
    return api.harvester_status()


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_harvester_states(request, format=None):
    """
    View to show all harvester states via GET request.
    """
    feedback = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        api = InitHarvester(harvester).get_harvester_api()
        response = api.harvester_status()
        feedback[harvester.name] = response.data[harvester.name]
    return Response(feedback, status=status.HTTP_200_OK)


class HarvesterCreateView(generics.ListCreateAPIView):
    """
    This class handles the GET and POST requests
    to create/register a new harvester
    to our Harvester Control Center REST-API.
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
    To show, modify and delete an registered harvester.
    """
    authentication_classes = (BasicAuthentication, )
    lookup_field = 'name'
    queryset = Harvester.objects.all()
    serializer_class = HarvesterSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)


class UserView(generics.ListAPIView):
    """
    View to list the control center registered users.
    """
    authentication_classes = (BasicAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailsView(generics.RetrieveAPIView):
    """
    View to retrieve a user instance.
    """
    authentication_classes = (BasicAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class EditHarvesterView(View, LoginRequiredMixin, AjaxableResponseMixin, FormMixin):
#class EditHarvesterView(LoginRequiredMixin, SuccessMessageMixin, RedirectView):
    """
    This class handles AJAx, GET, DELETE and POST requests
    to control the edit of the harvesters.
    """

    @staticmethod
    def get(request, *args, **kwargs): #the form that is load into the modal
        myname = kwargs['name']
        data = {}
        if myname == ' ':
            harvester = Harvester(owner=request.user)
            data['template_title'] = 'Add Harvester'
        else:
            harvester = Harvester.objects.get(name=myname)
            data['template_title'] = 'Edit Harvester'
        data['hname'] = myname
        data['form'] = HarvesterForm(instance=harvester)
        return render(request, "hcc/harvester_edit_form.html", data)

    def post(self, request, *args, **kwargs): #the actual logic behind the form
        myname = kwargs['name']
        name = self.request.POST.get('name')
        notes = self.request.POST.get('notes')
        url = self.request.POST.get('url')
        if myname == ' ': #Add Harvester
            if Harvester.objects.filter(name=name).exists():#check if the name is not already used
                return JsonResponse({'message':'A Harvester named {} already exists!'.format(name)})
            else:
                _h = Harvester(owner=self.request.user)
                action = 'added'
                myname = name
        else: #Edit Harvester
            _h = Harvester.objects.get(name=myname)
            action = 'modified'
        form = HarvesterForm(self.request.POST, instance=_h)
        if form.is_valid():
            form.save()
            success_message = "{} has been {} successfully!".format(myname, action)
            if action == 'initialised':
                LOGGER.info("new harvester created: %s", name)
            response = {'message':success_message, 'oldname':myname, 'newname':name, 'notes':notes, 'url':url}
        else:
            success_message = "{} could not been {}!".format(myname, action)
            response = {'message':success_message}
        return JsonResponse(response)


class ConfigHarvesterView(View, LoginRequiredMixin, AjaxableResponseMixin, FormMixin):
    """
    This class handles GET, DELETE and POST requests
    to control the config of the harvesters.
    """
    success_message = "%(name) was modified successfully"

    @staticmethod
    def get(request, *args, **kwargs):
        myname = kwargs['name']
        data = {}
        harvester = get_object_or_404(Harvester, name=myname)
        api = InitHarvester(harvester).get_harvester_api()
        response = api.harvester_config()
        if response.status_code != status.HTTP_200_OK:
            data["response"] = response.data["error_message"]
        else:
            form = create_config_form(response.data)
            data["response"] = form      
        data["hname"] = myname
        return render(request, "hcc/harvester_config_form.html", data)


    def post(self, request, *args, **kwargs):
        pass


class ScheduleHarvesterView(SuccessMessageMixin, RedirectView, AjaxableResponseMixin, FormMixin):
#class ScheduleHarvesterView(SuccessMessageMixin, RedirectView):
    """
    This class handles GET, DELETE and POST requests
    to control the scheduling of harvesters.
    """
    success_message = "Schedule for %(name) was created successfully"

    @staticmethod
    def get(request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        myname = kwargs['name']
        harvester = get_object_or_404(Harvester, name=myname)
        api = InitHarvester(harvester).get_harvester_api()
        crontab = request.POST.get(harvester.name + "-" + HCCJC.POSTCRONTAB,
                                   False)
        if crontab:
            response = api.add_schedule(crontab)
        else:
            response = api.delete_schedule(crontab)
        return JsonResponse(response.data[harvester.name][HCCJC.HEALTH])

    def delete(self, request, *args, **kwargs):
        myname = kwargs['name']
        harvester = get_object_or_404(Harvester, name=myname)
        api = InitHarvester(harvester).get_harvester_api()
        response = api.delete_schedule(request.POST[HCCJC.POSTCRONTAB])
        messages.add_message(
            request, messages.INFO, harvester.name + ': ' +
            response.data[harvester.name][HCCJC.HEALTH])
        return HttpResponseRedirect(reverse('hcc_gui'))