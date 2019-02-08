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
    Each method must return a Response with a JSON Body (see HCC Constants)
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
    
    @abc.abstractmethod
    def get_harvesterLog(self, harvester):
        pass

    @abc.abstractmethod
    def post_addHarvesterSchedule(self, harvester, crontab):
        pass

    @abc.abstractmethod
    def post_deleteHarvesterSchedule(self, harvester, crontab):
        pass

    @abc.abstractmethod
    def get_harvesterProgress(self, harvester):
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

    def addSchedule(self, crontab):
        return self._strategy.post_addHarvesterSchedule(self.harvester, crontab)
    
    def deleteSchedule(self, crontab):
        return self._strategy.post_deleteHarvesterSchedule(self.harvester, crontab)

    def harvesterProgress(self):
        return self._strategy.get_harvesterProgress(self.harvester)


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
                    feedback[harvester.name][HCCJC.HEALTH] = 'Authentication required.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_401_UNAUTHORIZED)
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name][HCCJC.HEALTH] = 'Resource on server not found. Check URL.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_404_NOT_FOUND)

                feedback[harvester.name][HCCJC.STATUS] = response.text
                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_HARVESTED_DOCS, stream=True)
                feedback[harvester.name][HCCJC.CACHED_DOCS] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_DATA_PROVIDER, stream=True)
                feedback[harvester.name][HCCJC.DATA_PROVIDER] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_MAX_DOCS, stream=True)
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_HEALTH, stream=True)
                feedback[harvester.name][HCCJC.HEALTH] = response.text

                if feedback[harvester.name][HCCJC.HEALTH] == HCCJC.OK and feedback[harvester.name][HCCJC.STATUS] == 'idling':
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS

                elif feedback[harvester.name][HCCJC.HEALTH] != HCCJC.OK:
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                elif feedback[harvester.name][HCCJC.STATUS].lower() == 'initialization':
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY

                else:
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_PROGRESS, stream=True)
                feedback[harvester.name][HCCJC.PROGRESS] = response.text
                if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR \
                        and response.status_code != status.HTTP_400_BAD_REQUEST:
                    feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = feedback[harvester.name][HCCJC.CACHED_DOCS]
                    if "/" not in response.text:
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = int(response.text)
                    else:
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = int(response.text.split("/")[1])
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                            int((int(response.text.split("/")[0]) / int(response.text.split("/")[1])) * 100)

                response = requests.get(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, stream=True)
                crontab = "Schedules:"
                cron = response.text.find(crontab)
                cronstring = response.text[cron + 11:cron + 11 + 9]
                if cronstring[0] == '-':
                    cronstring = 'no crontab defined yet'
                feedback[harvester.name][HCCJC.CRONTAB] = cronstring

            except ConnectionError:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name][HCCJC.HEALTH] = response.status_text + '. ' + response.data
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

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
            except ConnectionError:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name][HCCJC.HEALTH] = response.status_text + '. ' + response.data
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
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
            except ConnectionError:
                response = Response("A Connection Error. Host probably down. ", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name][HCCJC.HEALTH] = response.status_text + '. ' + response.data
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name : {HCCJC.HEALTH : 'disabled'}}, status=status.HTTP_423_LOCKED)

    def get_harvesterLog(self, harvester):
        return Response({harvester.name : {HCCJC.LOGS : 'not implemented'}}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvesterProgress(self, harvester):
        return Response({harvester.name : {HCCJC.PROGRESS : 'not implemented'}}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_addHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        del_response = requests.delete(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, stream=True)
        response = requests.post(harvester.url + HarvesterApiConstantsV6.PD_HARVEST_CRON \
        + crontab, stream=True)
        feedback[harvester.name][HCCJC.HEALTH] = del_response.text + ', ' + response.text
        return Response(feedback, status=response.status_code)

    def post_deleteHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        if crontab:
            response = requests.delete(harvester.url + HarvesterApiConstantsV6.PD_HARVEST_CRON \
            + crontab, stream=True)
            feedback[harvester.name][HCCJC.HEALTH] = response.text
        else:
            response = requests.delete(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, stream=True)
            feedback[harvester.name][HCCJC.HEALTH] = response.text
        return Response(feedback, status=response.status_code)


class VersionBased7Strategy(Strategy):
    """

    Implement the algorithm for the harvester lib v7.x.x using the Strategy interface.

    """

    def get_harvesterStatus(self, harvester):
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
                    feedback[harvester.name][HCCJC.STATUS] = HCCJC.INIT
                    feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
                elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATUS]
                    feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
                elif response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][HCCJC.HEALTH] = response.status_text
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                else:

                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.HEALTH]
                    # to be legacy (prior lib v7) compatible in html template set the old STATUS to STATE
                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATE].lower()
                    feedback[harvester.name][HCCJC.CACHED_DOCS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.DATA_PROVIDER] = harvester_json[HCCJC.REPO_NAME]

                    if harvester_json[HCCJC.HEALTH] == HCCJC.OK and harvester_json[HCCJC.STATE].lower() == HCCJC.IDLE:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS
                    elif harvester_json[HCCJC.HEALTH] != HCCJC.OK:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    elif harvester_json[HCCJC.STATE].lower() in [HCCJC.HARV]:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY
                    else:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                    if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                        maxDocuments = True
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                    else:
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = HCCJC.N_A

                    if maxDocuments:
                        if int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]) > 0:
                            feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                            int((int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100) / int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
                    else:
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(harvester_json[HCCJC.HARVESTED_COUNT])
                    
                    if HCCJC.LAST_HARVEST_DATE in harvester_json:
                        feedback[harvester.name][HCCJC.LAST_HARVEST_DATE] = harvester_json[HCCJC.LAST_HARVEST_DATE]
                    if HCCJC.REMAIN_HARVEST_TIME in harvester_json:
                        feedback[harvester.name][HCCJC.REMAIN_HARVEST_TIME] = harvester_json[HCCJC.REMAIN_HARVEST_TIME]

                    # schedules
                    response = requests.get(harvester.url + HarvesterApiConstantsV7.G_HARVEST_CRON, stream=True)
                    harvester_json = json.loads(response.text)
                    if not harvester_json[HCCJC.SCHEDULE]:
                        feedback[harvester.name][HCCJC.CRONTAB] = HCCJC.NO_CRONTAB
                    else:
                        feedback[harvester.name][HCCJC.CRONTAB] = harvester_json[HCCJC.SCHEDULE]

            except ConnectionError:
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
        feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
        return Response(feedback, status=response.status_code)

    def get_harvesterLog(self, harvester):
        now = datetime.datetime.now()
        feedback = {}
        feedback[harvester.name] = {}
        response = requests.get(harvester.url + HarvesterApiConstantsV7.G_HARVEST_LOG 
            + now.strftime(HarvesterApiConstantsV7.HARVESTER_LOG_FORMAT), stream=True)
        harvester_response = response.text
        feedback[harvester.name][HCCJC.LOGS] = harvester_response
        return Response(feedback, status=response.status_code)

    def get_harvesterProgress(self, harvester):
        feedback = {}
        feedback[harvester.name] = {}
        maxDocuments = False
        response = requests.get(harvester.url + HarvesterApiConstantsV7.PG_HARVEST, stream=True)
        harvester_json = json.loads(response.text)
        if harvester.enabled:
            feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[HCCJC.HARVESTED_COUNT]
            if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                maxDocuments = True
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                feedback[harvester.name][HCCJC.PROGRESS_MAX] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
            else:
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = HCCJC.N_A
            
            if HCCJC.REMAIN_HARVEST_TIME in harvester_json:
                feedback[harvester.name][HCCJC.REMAIN_HARVEST_TIME] = harvester_json[HCCJC.REMAIN_HARVEST_TIME]
            
            if maxDocuments:
                if int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]) > 0:
                    feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                    int((int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100) / int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
            else:
                feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(harvester_json[HCCJC.HARVESTED_COUNT])

        return Response(feedback, status=response.status_code)

    def post_addHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        response = requests.post(harvester.url + HarvesterApiConstantsV7.P_HARVEST_CRON, \
        json={HCCJC.POSTCRONTAB : crontab}, stream=True)
        harvester_response = response.text
        feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)
    
    def post_deleteHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        if not crontab:
            response = requests.post(harvester.url + HarvesterApiConstantsV7.DALL_HARVEST_CRON, stream=True)
            harvester_response = response.text
            feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        else:
            response = requests.post(harvester.url + HarvesterApiConstantsV7.D_HARVEST_CRON, \
            json={HCCJC.POSTCRONTAB : crontab}, stream=True)
            harvester_response = response.text
            feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)

