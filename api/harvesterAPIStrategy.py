import abc
import requests
import logging
import json
import datetime
from requests.exceptions import ConnectionError
from rest_framework import status
from rest_framework.response import Response

from api.constants import HarvesterApiConstantsV6, HarvesterApiConstantsV7
from api.constants import HCCJSONConstants as HCCJC

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class Strategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. HarvesterApi
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    """

    @abc.abstractmethod
    def get_harvesterStatus(self, harvester):
        pass

    @abc.abstractmethod
    def get_harvesterLog(self, harvester):
        pass

    @abc.abstractmethod
    def post_startHarvest(self, harvester):
        pass

    @abc.abstractmethod
    def post_stopHarvest(self, harvester):
        pass


class HarvesterApiStrategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, harvester, strategy):
        self._strategy = strategy
        self.harvester = harvester

    def set_strategy(self, strategy):
        self._strategy = strategy
    
    def get_harvester(self):
        return self.harvester

    def harvesterStatus(self):
        return self._strategy.get_harvesterStatus(self.harvester)

    def startHarvest(self):
        return self._strategy.post_startHarvest(self.harvester)

    def stopHarvest(self):
        return self._strategy.post_stopHarvest(self.harvester)
    
    def harvesterLog(self):
        return self._strategy.get_harvesterLog(self.harvester)


class VersionBased6Strategy(Strategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def get_harvesterStatus(self, harvester):
        feedback = {}
        if harvester.enabled:
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
            logging.debug("Harvester disabled - got no info; returning a Response with JSON")
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def post_startHarvest(self, harvester):
        feedback = {}
        if harvester.enabled:
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

    def post_stopHarvest(self, harvester):
        feedback = {}
        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                response = requests.post(harvester.url + HarvesterApiConstantsV6.P_HARVEST_ABORT, stream=True)
                feedback[harvester.name] = response.text
            except ConnectionError as e:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name]['health'] = response.status_text + '. ' + response.data
                feedback[harvester.name]['gui_status'] = 'warning'
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def get_harvesterLog(self, harvester):
        pass


class VersionBased7Strategy(Strategy):
    """

    Implement the algorithm for the harvester lib v7.x.x using the Strategy interface.
    
    """

    def get_harvesterStatus(self, harvester):
        now = datetime.datetime.now()
        feedback = {}
        maxDocuments = False
        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                response = requests.get(harvester.url + HarvesterApiConstantsV7.PG_HARVEST, stream=True)
                harvester_json = json.loads(response.text)
                
                if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY
                    feedback[harvester.name][HCCJC.STATUS] = 'initialization'
                    feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
                elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATUS]
                    feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
                elif response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][HCCJC.HEALTH] = 'Authentication required.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                else:

                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.HEALTH]

                    if harvester_json[HCCJC.STATE].lower() == "harvesting":
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY
                    elif harvester_json[HCCJC.HEALTH] == HCCJC.OK:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS
                    elif harvester_json[HCCJC.HEALTH] != HCCJC.OK:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    else:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATE].lower()

                    if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                        maxDocuments = True
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                    else:
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = "N/A"

                    feedback[harvester.name][HCCJC.CACHED_DOCS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    
                    if int(harvester_json[HCCJC.HARVESTED_COUNT]) != 0 and maxDocuments:
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                        int((int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100) / int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
                    else:
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(harvester_json[HCCJC.HARVESTED_COUNT])
                    
                    feedback[harvester.name][HCCJC.DATA_PROVIDER] = harvester_json[HCCJC.REPO_NAME]
                    # schedules
                    response = requests.get(harvester.url + HarvesterApiConstantsV7.G_HARVEST_CRON, stream=True)
                    harvester_json = json.loads(response.text)
                    if not harvester_json[HCCJC.SCHEDULE]:
                        feedback[harvester.name][HCCJC.CRONTAB] = HCCJC.NO_CRONTAB
                    else:
                        feedback[harvester.name][HCCJC.CRONTAB] = harvester_json[HCCJC.SCHEDULE]

                    response = requests.get(harvester.url + HarvesterApiConstantsV7.G_HARVEST_LOG 
                        + now.strftime(HarvesterApiConstantsV7.HARVESTER_LOG_FORMAT), stream=True)
                    harvester_log = response.text
                    feedback[harvester.name][HCCJC.LOGS] = harvester_log

            except ConnectionError as e:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name][HCCJC.HEALTH] = response.status_text + '. ' + response.data
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def post_startHarvest(self, harvester):
        feedback = {}
        feedback[harvester.name] = {}
        response = requests.post(harvester.url + HarvesterApiConstantsV7.PG_HARVEST, stream=True)
        harvester_json = json.loads(response.text)
        feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATUS]
        feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
        feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
        return Response(feedback, status=response.status_code)

    def post_stopHarvest(self, harvester):
        feedback = {}
        feedback[harvester.name] = {}
        response = requests.post(harvester.url + HarvesterApiConstantsV7.P_HARVEST_ABORT, stream=True)
        harvester_json = json.loads(response.text)
        feedback[harvester.name][HCCJC.HEALTH] = harvester_json['message']
        return Response(feedback, status=response.status_code)

    def get_harvesterLog(self, harvester):
        feedback = {}
        feedback[harvester.name] = {}
        response = requests.post(harvester.url + HarvesterApiConstantsV7.G_HARVEST_LOG, stream=True)
        harvester_response = response.text
        feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)

