"""
This is the views module which encapsulates the backend logic
which will be riggered via the corresponding path (url).
"""
import collections
import json
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
from api.forms import (HarvesterForm, SchedulerForm, UploadFileForm,
                       ValidateFileForm, create_config_fields,
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
    return HttpResponseRedirect(reverse('hcc_gui'))


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
    feedback[HCCJC.LOG_DATA] = {}
    harvesters = Harvester.objects.all()
    for harvester in harvesters:
        if harvester.enabled:
            api = InitHarvester(harvester).get_harvester_api()
            response = api.harvester_log()
            feedback[HCCJC.LOG_DATA][harvester.name] = response.data[harvester.name][HCCJC.LOGS]
    return render(request, "hcc/harvester_logs.html", feedback)


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
def harvester_status_history(request, name):
    """
    Returns the status history of a harvester.
    """
    feedback = {}
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).get_harvester_api()
    response = api.status_history()
    feedback["message"] = response.data
    return JsonResponse(feedback)


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


@login_required
def harvester_api_info(request, name):
    """
    This function returns the pretty rendered
    api help text of an harvester.
    """
    harvester = get_object_or_404(Harvester, name=name)
    api = InitHarvester(harvester).get_harvester_api()
    response = api.api_infotext()
    content = response.data[harvester.name].replace('\n', '<br>')
    return HttpResponse(content, content_type='text/plain')


def create_form(response, harvester_name):
    """
    This method generates a scheduler form for a harvester
    based on a harvester specific JSON response.
    If there is no response a default empty form will be created
    for that harvester.

    :param response: the response
    :return: SchedulerForm(prefix=harvester.name)
    """
    if response:
        response_dict = response.data[harvester_name]
        if HCCJC.CRONTAB in response_dict:
            # if a GET (or any other method) we'll create form
            # initialized with a schedule for this harvester
            jsonstr = {
                HCCJC.POSTCRONTAB:
                response_dict[HCCJC.CRONTAB]
            }
            placehldr = response_dict[HCCJC.CRONTAB]
            form = SchedulerForm(prefix=harvester_name)
            if isinstance(placehldr, list):
                if len(placehldr) > 0:
                    placehldr = response_dict[HCCJC.CRONTAB][0]
            form.fields[HCCJC.POSTCRONTAB].widget.attrs.update(
                {'placeholder': placehldr})
            return form
        else:
            jsonstr = {HCCJC.POSTCRONTAB: '0 0 * * *'}
            form = SchedulerForm(initial=jsonstr,
                                 prefix=harvester_name)
            return form
    else:
        jsonstr = {HCCJC.POSTCRONTAB: '0 0 * * *'}
        form = SchedulerForm(initial=jsonstr,
                             prefix=harvester_name)
        return form


def home(request):
    """
    Home entry point of Web-Application GUI.
    """
    feedback = {}

    # init session variables:
    # theme (dark/light) with default light
    theme = request.session.get('theme', 'light')
    # viewtype (card/list/table) with default card
    viewtype = request.session.get('viewtype', 'card')
    # collapse status (visible/collapsed)
    collapse_status = {}
    collapse_status['toolbox'] = request.session.get('toolbox', 'collapsed')
    collapse_status['chart'] = request.session.get('chart', 'collapsed')
    collapse_status['disabled_harvs'] = request.session.get(
        'disabled_harvs', 'collapsed')
    collapse_status['enabled_harvs'] = request.session.get(
        'enabled_harvs', 'visible')

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
                forms[harvester.name] = create_form(response, harvester.name)
                if response:
                    feedback[harvester.name] = response.data[harvester.name]
                else:
                    feedback[harvester.name] = {}
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    err = 'Error : no response object'
                    feedback[harvester.name][HCCJC.HEALTH] = err
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
                'theme': theme,
                'viewtype': viewtype,
                'collapse_status': collapse_status
            })

    return render(request, 'hcc/index.html', {
        'status': feedback
    })


@login_required
def update_session(request):
    """
    Updates session variables via POST request.
    """
    if not request.is_ajax() or not request.method == 'POST':
        return JsonResponse({
            'status': 'failed', 'message': 'not a POST request or ajax call'
        })

    message = ""
    for key, value in request.POST.items():
        if key == "csrfmiddlewaretoken":
            continue
        elif key in HCCJC.SESSION_KEYS:
            request.session[key] = value
            status = "ok"
            message += 'Session variable {} was changed to {}.'.format(
                key, value)
        else:
            request.session[key] = value
            status = "failed"
            message += '{} is not a session variable.'.format(value)

    return JsonResponse({
        'status': status,
        'message': message
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


@login_required
def harvester_data_to_file(request):
    """
    Function that gets data of all harvesters in the database and returns it
    through a file.
    """
    data = list(Harvester.objects.values('name', 'notes', 'url', 'enabled'))

    return JsonResponse(data, safe=False)


@login_required
def upload_file(request):
    """
    This function handles POST requests to upload a file
    containing harvester data and add it to the database
    """
    data = {}
    f = request.FILES['upload_file']
    # Check if file type is correct and get the content
    if f.content_type == 'application/json':
        try:
            content = json.load(f)
        except json.JSONDecodeError:
            message = (
                'Upload failed. '
                'File content was either wrong formatted or empty. '
                'Must be a JSON array of objects with harvester data.'
            )
            messages.warning(request, message)
            return HttpResponseRedirect(reverse('hcc_gui'))
    else:
        message = (
            'Upload failed. '
            'File type could not been handled. '
            'Must be a JSON file!'
        )
        messages.warning(request, message)
        return HttpResponseRedirect(reverse('hcc_gui'))

    required_keys = ('name', 'notes', 'url', 'enabled')
    for harvester_data in content:
        # 'content' should be a list of dictionaries
        if not isinstance(harvester_data, collections.Mapping):
            message = (
                'Validation failed. '
                'File content could not been handled.'
                'Should be a list of dictionaries!'
            )
            messages.warning(request, message)
            return HttpResponseRedirect(reverse('hcc_gui'))

        # The json file should contain the required harvester data
        if not all(key in harvester_data for key in required_keys):
            message = (
                'Validation failed. '
                'Key missmatch! Required: name, notes, url, enabled'
            )
            messages.warning(request, message)
            return HttpResponseRedirect(reverse('hcc_gui'))

        data = harvester_data.copy()
        if Harvester.objects.filter(name=harvester_data['name']).exists():
            # Harvester already exists -> update harvester
            harvester = Harvester.objects.get(name=harvester_data['name'])
            data['notes'] = harvester.notes  # Notes should not be updated
            if ((harvester.url == harvester_data['url']
                 and harvester.enabled == harvester_data['enabled'])):
                continue
            elif not harvester.url == harvester_data['url']:
                if Harvester.objects.filter(
                        url=harvester_data['url']).exists():
                    # The url should be unique. Leave the existing harvester data
                    # and ignore the new one.
                    continue
                # Create new Harvester with new url
                harvester = Harvester(owner=request.user)
                counter = 1
                while True:
                    # Loop until the harvester name is not already used
                    postfix = '_{}'.format(counter)
                    temp_name = harvester_data['name'] + postfix
                    if not Harvester.objects.filter(name=temp_name).exists():
                        data['name'] = temp_name
                        break
                    counter += 1
        elif Harvester.objects.filter(url=harvester_data['url']).exists():
            # The url should be unique. Leave the existing harvester data
            # and ignore the new one
            continue
        else:
            # Create a new harvester
            harvester = Harvester(owner=request.user)

        form = ValidateFileForm(data, instance=harvester)
        if form.is_valid():
            form.save()
        else:
            message = (
                'Validation failed. '
                'Content data could not been saved.'
            )
            messages.warning(request, message)
            return HttpResponseRedirect(reverse('hcc_gui'))

    messages.success(request, 'Upload successful!')
    return HttpResponseRedirect(reverse('hcc_gui'))


@login_required
def upload_file_form(request):
    """
    This function handles GET requests to create a form
    for uploading a file containing harvester data that
    will be handled in upload_file.
    """
    data = {'uploadform': UploadFileForm()}
    return render(request, "hcc/file_upload_form.html", data)


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


class EditHarvesterView(LoginRequiredMixin, View,
                        AjaxableResponseMixin, FormMixin):
    """
    This class handles AJAx, GET, DELETE and POST requests
    to control the edit of the harvesters.
    """

    @staticmethod
    def get(request, *args, **kwargs):  # the form that is loaded into the modal
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
                action = 'initialised'
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


class ConfigHarvesterView(LoginRequiredMixin, View,
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
        data = json.loads(request.body)
        response = api.delete_schedule(data[HCCJC.POSTCRONTAB])
        messages.add_message(
            request, messages.INFO, harvester.name + ': '
            + response.data[harvester.name][HCCJC.HEALTH])
        return HttpResponseRedirect(reverse('hcc_gui'))
