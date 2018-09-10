import requests
from requests.exceptions import ConnectionError
from rest_framework import status
from rest_framework.response import Response

from .harvesterapi import HarvesterApi

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class Helpers:
    """Custom helper class to handle all the post and get requests via a request_type attribute."""

    @staticmethod
    def harvester_response_wrapper(harvester, request_type, request):
        """Return a harvester response.
        :type harvester: a harvester
        :type request_type: string indicating a request to be fullfilled
        :type request: the request
        """
        feedback = {}
        if harvester.enabled is True:
            try:
                feedback[harvester.name] = {}
                response = requests.get(harvester.url + HarvesterApi.G_STATUS, stream=True)
                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name]['health'] = 'Authentication required.'
                    feedback[harvester.name]['gui_status'] = 'warning'
                    return Response(feedback, status=status.HTTP_401_UNAUTHORIZED)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name]['health'] = 'Resource on server not found. Check URL.'
                    feedback[harvester.name]['gui_status'] = 'warning'
                    return Response(feedback, status=status.HTTP_404_NOT_FOUND)

                if request_type == 'GET_STATUS':
                    feedback[harvester.name] = {}
                    response = requests.get(harvester.url + HarvesterApi.G_STATUS, stream=True)
                    feedback[harvester.name]['status'] = response.text
                    response = requests.get(harvester.url + HarvesterApi.G_HARVESTED_DOCS, stream=True)
                    feedback[harvester.name]['cached_docs'] = response.text

                    # response = requests.get(harvester.url + Harvester_API.G_BOOLEAN_OUTDATED_DOCS, stream=True)
                    # if response.status_code is status.HTTP_404_NOT_FOUND:
                    #     feedback[harvester.name]['mdata_outdated'] = \
                    #          'offline. Resource on server not found. Check URL.'
                    # else:
                    #     feedback[harvester.name]['mdata_outdated'] = bool(response.text)

                    response = requests.get(harvester.url + HarvesterApi.G_DATA_PROVIDER, stream=True)
                    feedback[harvester.name]['data_pvd'] = response.text

                    response = requests.get(harvester.url + HarvesterApi.G_MAX_DOCS, stream=True)
                    feedback[harvester.name]['max_docs'] = response.text

                    response = requests.get(harvester.url + HarvesterApi.G_HEALTH, stream=True)
                    feedback[harvester.name]['health'] = response.text

                    if feedback[harvester.name]['health'] == 'OK' and feedback[harvester.name]['status'] == 'idling':
                        feedback[harvester.name]['gui_status'] = 'success'

                    elif feedback[harvester.name]['health'] != 'OK':
                        feedback[harvester.name]['gui_status'] = 'warning'

                    elif feedback[harvester.name]['status'].lower() == 'initialization':
                        feedback[harvester.name]['gui_status'] = 'primary'

                    else:
                        feedback[harvester.name]['gui_status'] = 'info'

                    response = requests.get(harvester.url + HarvesterApi.G_PROGRESS, stream=True)
                    feedback[harvester.name]['progress'] = response.text
                    if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR \
                            and response.status_code != status.HTTP_400_BAD_REQUEST:
                        feedback[harvester.name]['progress_cur'] = feedback[harvester.name]['cached_docs']
                        if "/" not in response.text:
                            feedback[harvester.name]['progress_max'] = int(response.text)
                        else:
                            feedback[harvester.name]['progress_max'] = int(response.text.split("/")[1])
                            feedback[harvester.name]['progress_cur'] = \
                                int((int(response.text.split("/")[0]) / int(response.text.split("/")[1])) * 100)

                    response = requests.get(harvester.url + HarvesterApi.GD_HARVEST_CRON, stream=True)
                    crontab = "Schedules:"
                    cron = response.text.find(crontab)
                    cronstring = response.text[cron + 11:cron + 11 + 9]
                    if cronstring[0] == '-':
                        cronstring = 'no crontab defined yet'
                    feedback[harvester.name]['cron'] = cronstring

                elif request_type == 'POST_STARTH':
                    response = requests.post(harvester.url + HarvesterApi.P_HARVEST, stream=True)
                    feedback[harvester.name] = response.text

                elif request_type == 'POST_STOPH':
                    response = requests.post(harvester.url + HarvesterApi.P_HARVEST_ABORT, stream=True)
                    feedback[harvester.name] = response.text

                elif request_type == 'P_HARVEST_SUBMIT':
                    response = requests.post(harvester.url + HarvesterApi.P_HARVEST_SUBMIT, stream=True)
                    feedback[harvester.name] = response.text

                elif request_type == 'POST_CRON':
                    del_response = requests.delete(harvester.url + HarvesterApi.GD_HARVEST_CRON, stream=True)
                    response = requests.post(harvester.url + HarvesterApi.PD_HARVEST_CRON + request.POST['schedule'],
                                             stream=True)
                    feedback[harvester.name] = del_response.text + ', ' + response.text

                elif request_type == 'DELETE_CRON':
                    response = requests.delete(harvester.url + HarvesterApi.PD_HARVEST_CRON + request.POST['schedule'],
                                               stream=True)
                    feedback[harvester.name] = response.text

                elif request_type == 'DELETE_ALL_CRON':
                    response = requests.delete(harvester.url + HarvesterApi.GD_HARVEST_CRON, stream=True)
                    feedback[harvester.name] = response.text

                elif request_type == 'GET_CRON':
                    response = requests.get(harvester.url + HarvesterApi.GD_HARVEST_CRON, stream=True)
                    crontab = "Schedules:"
                    cron = response.text.find(crontab)
                    feedback[harvester.name] = response.text[cron + 11:cron + 11 + 9]

                else:
                    response = Response('no request_type given', status=status.HTTP_400_BAD_REQUEST)

            except ConnectionError as e:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name]['health'] = response.status_text + '. ' + response.data
                feedback[harvester.name]['gui_status'] = 'warning'
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)
