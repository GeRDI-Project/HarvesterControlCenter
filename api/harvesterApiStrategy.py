# import base64
import abc
import requests
from requests.exceptions import ConnectionError
from rest_framework import status
from rest_framework.response import Response

from .harvesterapi import HarvesterApiConstantsV6

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HarvesterApiConstantsV7:
    """

     This Class holds a list of Harvester API constants which will be updated accordingly to the Harvester-BaseLibrary.
     Current version is 7.x.x See: https://wiki.gerdi-project.de/display/GeRDI/Harvester+Library+7.x.x
     
    """
    PG_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    G_HARVEST_LOG = "/log"
    P_HARVEST_CRON = "/harvest/schedule/_add" #E.g. {"cronTab" : "0 0 * * *"}
    G_HARVEST_CRON = "/harvest/schedule"
    D_HARVEST_CRON = "/harvest/schedule/_delete" #E.g. {"cronTab" : "0 0 * * *"}
    DALL_HARVEST_CRON = "/harvest/schedule/_deleteAll"
    G_HEALTH = "/health"
    G_BOOLEAN_OUTDATED = "/outdated"

    # HARVESTER_USER = ""
    # HARVESTER_PASS = ""
    # credentials = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)

class HarvesterApi:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def getStausOfHarvester(self, harvester):
        self._strategy.getStatusHarvest(harvester)

    def startHarvest(self, harvester):
        self._strategy.postStartHarvest(harvester)


class Strategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. HarvesterApi
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    """

    @abc.abstractmethod
    def getStatusHarvest(self, harvester):
        pass

    @abc.abstractmethod
    def postStartHarvest(self, harvester):
        pass


class VersionBased6Strategy(Strategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def getStatusHarvest(self, harvester):
        feedback = {}
        if harvester.enabled is True:
            try:
                feedback[harvester.name] = {}
                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_STATUS, stream=True)
                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name]['health'] = 'Authentication required.'
                    feedback[harvester.name]['gui_status'] = 'warning'
                    return Response(feedback, status=status.HTTP_401_UNAUTHORIZED)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name]['health'] = 'Resource on server not found. Check URL.'
                    feedback[harvester.name]['gui_status'] = 'warning'
                    return Response(feedback, status=status.HTTP_404_NOT_FOUND)

                feedback[harvester.name]['status'] = response.text
                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_HARVESTED_DOCS, stream=True)
                feedback[harvester.name]['cached_docs'] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_DATA_PROVIDER, stream=True)
                feedback[harvester.name]['data_pvd'] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_MAX_DOCS, stream=True)
                feedback[harvester.name]['max_docs'] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_HEALTH, stream=True)
                feedback[harvester.name]['health'] = response.text

                if feedback[harvester.name]['health'] == 'OK' and feedback[harvester.name]['status'] == 'idling':
                    feedback[harvester.name]['gui_status'] = 'success'

                elif feedback[harvester.name]['health'] != 'OK':
                    feedback[harvester.name]['gui_status'] = 'warning'

                elif feedback[harvester.name]['status'].lower() == 'initialization':
                    feedback[harvester.name]['gui_status'] = 'primary'

                else:
                    feedback[harvester.name]['gui_status'] = 'info'

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_PROGRESS, stream=True)
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

                response = requests.get(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, stream=True)
                crontab = "Schedules:"
                cron = response.text.find(crontab)
                cronstring = response.text[cron + 11:cron + 11 + 9]
                if cronstring[0] == '-':
                    cronstring = 'no crontab defined yet'
                feedback[harvester.name]['cron'] = cronstring

            except ConnectionError as e:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name]['health'] = response.status_text + '. ' + response.data
                feedback[harvester.name]['gui_status'] = 'warning'
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def postStartHarvest(self, harvester):
        feedback = {}
        if harvester.enabled is True:
            try:
                feedback[harvester.name] = {}
                response = requests.post(harvester.url + HarvesterApiConstantsV6.P_HARVEST, stream=True)
                feedback[harvester.name] = response.text
            except ConnectionError as e:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name]['health'] = response.status_text + '. ' + response.data
                feedback[harvester.name]['gui_status'] = 'warning'
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)



class VersionBased7Strategy(Strategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def getHarvest(self):
        pass

