"""
The is the views module which encapsulates the backend logic
"""
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import RedirectView
from django.views.generic.base import View
from django.views.generic.edit import FormMixin
from rest_framework import generics, permissions, status
from rest_framework.authentication import (BasicAuthentication,
                                           TokenAuthentication)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.constants import HCCJSONConstants as HCCJC
from api.forms import (HarvesterForm, SchedulerForm, create_config_fields,
                       create_config_form)
from api.harvester_api import InitHarvester
from api.mixins import AjaxableResponseMixin
from api.models import Harvester
from api.permissions import IsOwner
from api.serializers import HarvesterSerializer, UserSerializer

__author__ = "Jan Frömberg, Laura Höhle"
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
def toggle_harvesters(request, hnames):
    """
    This function toggles the enabled and disabled status of selected harvester.

    :param request: the request
    :param hnames: names of the harvesters
    :return: an HttpResponseRedirect to the Main HCC page
    """
    names = hnames.split('-')
    for name in names:
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
def start_selected_harvesters(request, hnames):
    """
    This function starts selected harvester.

    :param request: the request
    :param hnames: names of the harvesters
    :return: an HttpResponseRedirect to the Main HCC page
    """
    names = hnames.split('-')
    for name in names:
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

    # init session variables:
    # mode (dark/light) with default light
    mode = request.session.get('mode', 'light')
    # viewtype (card/list/table) with default card
    viewtype = request.session.get('viewtype', 'card')
    # collapse status (visible/hidden)
    collapse_status = {}
    collapse_status['toolbox'] = request.session.get('toolbox', 'collapsed')
    collapse_status['chart'] = request.session.get('chart', 'collapsed')
    collapse_status['disabled_harvs'] = request.session.get('disabled_harvs', 'collapsed')
    collapse_status['enabled_harvs'] = request.session.get('enabled_harvs', 'visible')

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
                'mode': mode,
                'viewtype': viewtype,
                'collapse_status': collapse_status
            })

    return render(request, 'hcc/index.html', {
        'status': feedback,
        'mode': mode
    })

@permission_classes((IsAuthenticated, ))
def update_session(request):
    if not request.is_ajax() or not request.method == 'POST':
        return JsonResponse({
            'status': 'failed',
            'message': 'wrong access'
        })

    if 'mode' in request.POST:
        request.session['mode'] = request.POST.get('mode')
        var = 'mode'
    elif 'viewtype' in request.POST:
        request.session['viewtype'] = request.POST.get('viewtype')
        var = 'viewtype'
    elif 'toolbox' in request.POST:
        request.session['toolbox'] = request.POST.get('toolbox')
        var = 'toolbox'
    elif 'chart' in request.POST:
        request.session['chart'] = request.POST.get('chart')
        var = 'chart'
    elif 'disabledHarvs' in request.POST:
        request.session['disabled_harvs'] = request.POST.get('disabledHarvs')
        var = 'disabled_harvs'
    elif 'enabledHarvs' in request.POST:
        request.session['enabled_harvs'] = request.POST.get('enabledHarvs')
        var = 'enabled_harvs' 
    else:
        return JsonResponse({
            'status': 'failed',  
            'message': 'Data could not been handled.'
        })
    
    return JsonResponse({
        'status': 'ok', 
        'message': 'Session variable {} was changed to {}.'.format(var, request.session[var])
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


class EditHarvesterView(View, LoginRequiredMixin,
                        AjaxableResponseMixin, FormMixin):
    """
    This class handles AJAx, GET, DELETE and POST requests
    to control the edit of the harvesters.
    """

    @staticmethod
    def get(request, *args, **kwargs):  # the form that is load into the modal
        data = {}
        if "name" not in kwargs:
            harvester = Harvester(owner=request.user)
            data['template_title'] = 'Add Harvester'
        else:
            myname = kwargs['name']
            harvester = Harvester.objects.get(name=myname)
            data['template_title'] = "Edit Harvester - {}".format(myname)
            data['hname'] = myname
        data['form'] = HarvesterForm(instance=harvester)
        return render(request, "hcc/harvester_edit_form.html", data)

    def post(self, request, *args, **kwargs):  # the actual logic behind the form
        name = self.request.POST.get('name')
        if "name" not in kwargs:  # Add Harvester
            # check if the name is not already used
            if Harvester.objects.filter(name=name).exists():
                return JsonResponse(
                    {'message': 'A Harvester named {} already exists!'.format(name)})
            else:
                _h = Harvester(owner=self.request.user)
                action = 'added'
                myname = name
        else:  # Edit Harvester
            myname = kwargs['name']
            _h = Harvester.objects.get(name=myname)
            action = 'modified'
        form = HarvesterForm(self.request.POST, instance=_h)
        if form.is_valid():
            form.save()
            success_message = (
                "{} has been {} successfully!"
                " Please hold on while the page"
                " is reloading.".format(myname, action)
            )
            if action == 'initialised':
                LOGGER.info("new harvester created: {}".format(name))
            response = {'message': success_message, 'name': myname}
        else:
            success_message = (
                "{} could not been {}!"
                " Please hold on while the page"
                " is reloading.".format(myname, action)
            )
            response = {'message': success_message}
        return JsonResponse(response)


class ConfigHarvesterView(View, LoginRequiredMixin,
                          AjaxableResponseMixin, FormMixin):
    """
    This class handles GET, DELETE and POST requests
    to control the config of the harvesters.
    """

    @staticmethod
    def get(request, *args, **kwargs):
        myname = kwargs['name']
        data = {}
        harvester = get_object_or_404(Harvester, name=myname)
        api = InitHarvester(harvester).get_harvester_api()
        response = api.get_harvester_config_data()
        if response.status_code != status.HTTP_200_OK:
            data["message"] = response.data[harvester.name][HCCJC.HEALTH]
        else:
            form = create_config_form(
                response.data[harvester.name][HCCJC.HEALTH])
            data["form"] = form
        data["hname"] = myname
        return render(request, "hcc/harvester_config_form.html", data)

    def post(self, request, *args, **kwargs):
        myname = kwargs['name']
        harvester = get_object_or_404(Harvester, name=myname)
        api = InitHarvester(harvester).get_harvester_api()
        response = api.get_harvester_config_data()
        old_config_data = response.data[harvester.name][HCCJC.HEALTH]
        (fields, old_data) = create_config_fields(old_config_data)
        data = {}
        changes = {}  # before-after data
        config_changes = {}  # only after data to send to api
        for key in fields:
            # In the response all boolean fields are either set "on" if True
            # or None if false. -> convert it
            if self.request.POST.get(key) == "on":
                new_data = "true"
            elif self.request.POST.get(key) is None:
                new_data = "false"
            else:
                new_data = self.request.POST.get(key)

            if(old_data[key] != new_data):
                changes[key] = {"before": old_data[key], "after": new_data}
                config_changes[key] = new_data
        if len(changes) > 0:
            response = api.save_harvester_config_data(config_changes)
            data["changes"] = changes
        else:
            return JsonResponse({
                "status": "unchanged",
                "message": "There have been no changes!"
            })

        message = response.data[harvester.name][HCCJC.HEALTH]["message"]
        data["message"] = message
        data["status"] = response.data[harvester.name][HCCJC.HEALTH]["status"]
        if ("Cannot change value" in message) and ("Set parameter" in message):
            data["status"] = "some issues"

        return JsonResponse(data)


class ScheduleHarvesterView(
        SuccessMessageMixin, RedirectView, AjaxableResponseMixin, FormMixin):
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
