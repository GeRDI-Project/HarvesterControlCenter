"""
This module holds all classes for the harvester API strategy
"""
import abc
import datetime
import json
import logging

import requests
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.response import Response

from api.constants import HarvesterApiConstantsV6, HarvesterApiConstantsV7
from api.constants import HCCJSONConstants as HCCJC

__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"

# Get an instance of a logger
LOGGER = logging.getLogger(__name__)


class Strategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. HarvesterApi
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    Each method must return a Response with a JSON Body (see HCC Constants)
    """

    @abc.abstractmethod
    def get_harvester_status(self, harvester):
        """abstract method for harvester status"""

    @abc.abstractmethod
    def get_harvester_log(self, harvester):
        """abstract method for harvester log"""

    @abc.abstractmethod
    def post_start_harvest(self, harvester):
        """abstract method for harvester start"""

    @abc.abstractmethod
    def post_stop_harvest(self, harvester):
        """abstract method for harvester stop"""

    @abc.abstractmethod
    def post_reset_harvest(self, harvester):
        """abstract method for harvester reset"""

    @abc.abstractmethod
    def post_add_harvester_schedule(self, harvester, crontab):
        """abstract method for adding a harvester schedule"""

    @abc.abstractmethod
    def post_delete_harvester_schedule(self, harvester, crontab):
        """abstract method for deleting a harvester schedule"""

    @abc.abstractmethod
    def get_harvester_progress(self, harvester):
        """abstract method for harvester progress"""

    @abc.abstractmethod
    def get_harvester_config(self, harvester):
        """abstract method for getting harvester configuration data"""

    @abc.abstractmethod
    def set_harvester_config(self, harvester, changes):
        """abstract method for setting harvester configuration"""

    @abc.abstractmethod
    def get_status_history(self, harvester):
        """abstract method for getting the status history"""


class HarvesterApiStrategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, harvester, strategy):
        self._strategy = strategy
        self.harvester = harvester

    def set_strategy(self, strategy):
        """set strategy for a harvester"""
        self._strategy = strategy

    def get_harvester(self):
        """returns the harvester"""
        return self.harvester

    def harvester_status(self):
        """return the status of a harvester"""
        return self._strategy.get_harvester_status(self.harvester)

    def start_harvest(self):
        """start a single harvester"""
        LOGGER.info("%s harvester started by user.", self.harvester.name)
        return self._strategy.post_start_harvest(self.harvester)

    def stop_harvest(self):
        """stop a single harvester"""
        LOGGER.info("%s harvester stopped by user.", self.harvester.name)
        return self._strategy.post_stop_harvest(self.harvester)

    def reset_harvest(self):
        """reset a single harvester"""
        LOGGER.info("%s harvester resetted by user.", self.harvester.name)
        return self._strategy.post_reset_harvest(self.harvester)

    def harvester_log(self):
        """get the harvester logfile of today"""
        return self._strategy.get_harvester_log(self.harvester)

    def add_schedule(self, crontab):
        """set a crontab for a harvester"""
        LOGGER.info("%s harvester schedule added by user.",
                    self.harvester.name)
        return self._strategy.post_add_harvester_schedule(
            self.harvester, crontab)

    def delete_schedule(self, crontab):
        """del all schedules of a harvester"""
        LOGGER.info("%s harvester schedule deleted by user.",
                    self.harvester.name)
        return self._strategy.post_delete_harvester_schedule(
            self.harvester, crontab)

    def harvester_progress(self):
        """get harvesting progress"""
        return self._strategy.get_harvester_progress(self.harvester)

    def get_harvester_config_data(self):
        """get configuration data"""
        return self._strategy.get_harvester_config(self.harvester)

    def save_harvester_config_data(self, changes):
        """set configuration data"""
        return self._strategy.set_harvester_config(self.harvester, changes)

    def status_history(self):
        """get the status history of a harvester"""
        return self._strategy.get_status_history(self.harvester)

    def api_infotext(self):
        """get the api data of a harvester"""
        return self._strategy.get_api_info(self.harvester)


def a_response(harvester_name, url, method):
    """
    A uniform response method to encapsulate requests.
    """
    feedback, harvester_json = {}, {}
    feedback[harvester_name] = {}
    response = None

    try:

        if method == 'Get':
            response = requests.get(url, timeout=5)
        elif method == 'Put':
            response = requests.put(url, timeout=5)
        elif method == 'Post':
            response = requests.post(url, timeout=9)
        elif method == 'Delete':
            response = requests.delete(url, timeout=5)

        try:
            harvester_json = json.loads(response.text)

            if HCCJC.STATUS in harvester_json:
                feedback[harvester_name][HCCJC.STATUS] = harvester_json[
                    HCCJC.STATUS]
                feedback[harvester_name][HCCJC.STATE] = harvester_json[
                    HCCJC.STATUS]
            else:
                feedback[harvester_name][HCCJC.STATUS] = "no status"
                feedback[harvester_name][HCCJC.STATE] = "no status"

            if HCCJC.MESSAGE in harvester_json:
                feedback[harvester_name][HCCJC.HEALTH] = harvester_json[
                    HCCJC.MESSAGE]
            else:
                feedback[harvester_name][HCCJC.HEALTH] = "health unknown"

        except ValueError:
            harvester_json = response.text
            feedback[harvester_name] = harvester_json

    except RequestException as _e:

        feedback[harvester_name][HCCJC.HEALTH] = str(_e)
        feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING
        feedback[harvester_name][HCCJC.STATUS] = "no status"
        feedback[harvester_name][HCCJC.STATE] = "no status"

    return Response(feedback,
                    status=response.status_code if response is not None else
                    status.HTTP_408_REQUEST_TIMEOUT), harvester_json


class BaseStrategy(Strategy):
    """
    Fallback strategy alorithm for basic harvester support.
    Just UP/DOWN information.
    """

    def get_harvester_status(self, harvester):
        feedback = {}
        response = None
        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                response = requests.get(harvester.url, timeout=5)

                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][
                        HCCJC.HEALTH] = 'Authentication required.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name][HCCJC.HEALTH] = \
                        'Resource on server not found. Check URL.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                if response.status_code == status.HTTP_200_OK:
                    feedback[harvester.name][HCCJC.HEALTH] = response.text
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS

                if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
                    feedback[harvester.name][HCCJC.HEALTH] = json.loads(response.text)[
                        "message"]
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                feedback[harvester.name][
                    HCCJC.CRONTAB] = "cron not supported. basic mode."
                feedback[harvester.name][HCCJC.STATUS] = "no status"

            except RequestException as _e:
                feedback[harvester.name][HCCJC.HEALTH] = str(_e)
                feedback[harvester.name][HCCJC.STATUS] = "no status"
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback,
                            status=response.status_code if response is not None
                            else status.HTTP_408_REQUEST_TIMEOUT)

        return Response({harvester.name: 'disabled'},
                        status=status.HTTP_423_LOCKED)

    def post_start_harvest(self, harvester):
        return Response({harvester.name: 'start not supported'},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_reset_harvest(self, harvester):

        return VersionBased7Strategy.post_reset_harvest(self, harvester)

    def post_stop_harvest(self, harvester):
        return Response({harvester.name: 'stop not supported'},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvester_log(self, harvester):
        return Response({harvester.name: {
            HCCJC.LOGS: 'log not supported'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvester_progress(self, harvester):
        return Response(
            {harvester.name: {
                HCCJC.PROGRESS: 'progress not supported'
            }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_add_harvester_schedule(self, harvester, crontab):
        return Response({harvester.name: {
            HCCJC.HEALTH: 'cron not supported'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_delete_harvester_schedule(self, harvester, crontab):
        return Response({harvester.name: {
            HCCJC.HEALTH: 'cron not supported'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvester_config(self, harvester):
        return Response({harvester.name: {
            HCCJC.HEALTH: 'config not supported'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def set_harvester_config(self, harvester, changes):
        return Response({harvester.name: {
            HCCJC.HEALTH: 'config not supported'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_status_history(self, harvester):
        return Response('status history not available',
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_api_info(self, harvester):
        return Response({harvester.name: 'api info not available'},
                        status=status.HTTP_501_NOT_IMPLEMENTED)


class VersionBased6Strategy(Strategy):
    """
    The algorithm implemented using the Strategy interface.
    For old/legacy harvesters prior to library version v7
    """

    def a_response(self, harvester_name, url, method):
        """
        A uniform response method to encapsulate requests.
        """
        feedback = {}
        feedback[harvester_name] = {}
        response = None
        if method == 'Get':
            try:
                feedback[harvester_name] = {}
                response = requests.get(url, timeout=5)
                feedback[harvester_name] = response.text
            except RequestException as _e:
                feedback[harvester_name][HCCJC.HEALTH] = str(_e)
                feedback[harvester_name][HCCJC.STATUS] = "no status"
                feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback,
                            status=response.status_code if response is not None
                            else status.HTTP_408_REQUEST_TIMEOUT)
        if method == 'Put':
            try:
                feedback[harvester_name] = {}
                response = requests.put(url, timeout=5)
                feedback[harvester_name] = response.text
            except RequestException as _e:
                feedback[harvester_name][HCCJC.HEALTH] = str(_e)
                feedback[harvester_name][HCCJC.STATUS] = "no status"
                feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback,
                            status=response.status_code if response is not None
                            else status.HTTP_408_REQUEST_TIMEOUT)
        if method == 'Post':
            try:
                feedback[harvester_name] = {}
                response = requests.post(url, timeout=9)
                feedback[harvester_name] = response.text
            except RequestException as _e:
                feedback[harvester_name][HCCJC.HEALTH] = str(_e)
                feedback[harvester_name][HCCJC.STATUS] = "no status"
                feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback,
                            status=response.status_code if response is not None
                            else status.HTTP_408_REQUEST_TIMEOUT)

        return Response(feedback, status=status.HTTP_400_BAD_REQUEST)

    def get_harvester_status(self, harvester):
        feedback = {}
        response = None
        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                stat_url = harvester.url + HarvesterApiConstantsV6.G_STATUS
                response = requests.get(stat_url, timeout=5)

                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][
                        HCCJC.HEALTH] = 'Authentication required.'
                    feedback[harvester.name][HCCJC.STATUS] = "no status"
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback,
                                    status=status.HTTP_401_UNAUTHORIZED)

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name][HCCJC.HEALTH] = \
                        'Resource on server not found. Check URL.'
                    feedback[harvester.name][HCCJC.STATUS] = "no status"
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_404_NOT_FOUND)

                feedback[harvester.name][HCCJC.STATUS] = response.text
                response = requests.get(
                    harvester.url + HarvesterApiConstantsV6.G_HARVESTED_DOCS,
                    timeout=5)
                feedback[harvester.name][HCCJC.CACHED_DOCS] = response.text

                response = requests.get(
                    harvester.url + HarvesterApiConstantsV6.G_DATA_PROVIDER,
                    timeout=5)
                feedback[harvester.name][HCCJC.DATA_PROVIDER] = response.text

                maxdoc_url = harvester.url + HarvesterApiConstantsV6.G_MAX_DOCS
                response = requests.get(maxdoc_url, timeout=5)
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = response.text

                health_url = harvester.url + HarvesterApiConstantsV6.G_HEALTH
                response = requests.get(health_url, timeout=5)
                feedback[harvester.name][HCCJC.HEALTH] = response.text

                if feedback[harvester.name][
                        HCCJC.HEALTH] == HCCJC.OK and feedback[harvester.name][
                            HCCJC.STATUS] == 'idling':
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS

                elif feedback[harvester.name][HCCJC.HEALTH] != HCCJC.OK:
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                elif feedback[harvester.name][
                        HCCJC.STATUS].lower() == 'initialization':
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY

                else:
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                progress_url = harvester.url + HarvesterApiConstantsV6.G_PROGRESS
                response = requests.get(progress_url, timeout=5)
                feedback[harvester.name][HCCJC.PROGRESS] = response.text
                if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
                    feedback[harvester.name][
                        HCCJC.PROGRESS_CURRENT] = feedback[harvester.name][
                            HCCJC.CACHED_DOCS]
                    if "/" not in response.text:
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = int(
                            response.text)
                    elif "N/A" not in response.text:
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = int(
                            response.text.split("/")[1])
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(
                            (int(response.text.split("/")[0]) /
                             int(response.text.split("/")[1])) * 100)

                cron_url = harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON
                response = requests.get(cron_url, timeout=5)
                crontab = "Schedules:"
                cron = response.text.find(crontab)
                cronstring = response.text[cron + 11:cron + 11 + 9]
                if cronstring[0] == '-':
                    cronstring = 'no crontab defined yet'
                feedback[harvester.name][HCCJC.CRONTAB] = cronstring

            except RequestException as _e:
                feedback[harvester.name][HCCJC.HEALTH] = str(_e)
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback,
                            status=response.status_code if response is not None
                            else status.HTTP_408_REQUEST_TIMEOUT)

        return Response({harvester.name: 'disabled'},
                        status=status.HTTP_423_LOCKED)

    def post_start_harvest(self, harvester):
        if harvester.enabled:
            return self.a_response(
                harvester.name,
                harvester.url + HarvesterApiConstantsV6.P_HARVEST, 'Post')
        return Response({harvester.name: 'disabled'},
                        status=status.HTTP_423_LOCKED)

    def post_reset_harvest(self, harvester):
        if harvester.enabled:
            return self.a_response(
                harvester.name,
                harvester.url + HarvesterApiConstantsV6.P_HARVEST_RESET,
                'Post')
        return Response({harvester.name: 'disabled'},
                        status=status.HTTP_423_LOCKED)

    def post_stop_harvest(self, harvester):
        if harvester.enabled:
            return self.a_response(
                harvester.name,
                harvester.url + HarvesterApiConstantsV6.P_HARVEST_ABORT,
                'Post')
        return Response({harvester.name: {
            HCCJC.HEALTH: 'disabled'
        }},
            status=status.HTTP_423_LOCKED)

    def get_harvester_log(self, harvester):
        return Response({harvester.name: {
            HCCJC.LOGS: 'not implemented'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvester_progress(self, harvester):
        return Response({harvester.name: {
            HCCJC.PROGRESS: 'not implemented'
        }},
            status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_add_harvester_schedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        del_response = requests.delete(harvester.url +
                                       HarvesterApiConstantsV6.GD_HARVEST_CRON,
                                       timeout=5)
        response = requests.post(
            harvester.url + HarvesterApiConstantsV6.PD_HARVEST_CRON + crontab,
            timeout=5)
        feedback[harvester.name][
            HCCJC.HEALTH] = del_response.text + ', ' + response.text
        return Response(feedback, status=response.status_code)

    def post_delete_harvester_schedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        if crontab:
            response = requests.delete(
                harvester.url + HarvesterApiConstantsV6.PD_HARVEST_CRON +
                crontab,
                timeout=5)
            feedback[harvester.name][HCCJC.HEALTH] = response.text
        else:
            response = requests.delete(harvester.url +
                                       HarvesterApiConstantsV6.GD_HARVEST_CRON,
                                       timeout=5)
            feedback[harvester.name][HCCJC.HEALTH] = response.text
        return Response(feedback, status=response.status_code)

    def get_harvester_config(self, harvester):
        get_url = harvester.url + HarvesterApiConstantsV7.G_HARVEST_CONFIG
        response = requests.get(get_url)
        feedback = {}
        feedback[harvester.name] = {}
        if response.status_code == status.HTTP_200_OK:
            feedback[harvester.name][HCCJC.HEALTH] = json.loads(response.text)
        else:
            feedback[harvester.name][HCCJC.HEALTH] = "unable do get configuration data of harvester {}".format(
                harvester.name)
        return Response(feedback, status=response.status_code)

    def set_harvester_config(self, harvester, changes):
        set_url = harvester.url + HarvesterApiConstantsV7.P_HARVEST_CONFIG
        response = requests.post(set_url, json=changes)
        feedback = {}
        feedback[harvester.name] = {}
        if response.status_code == status.HTTP_200_OK:
            feedback[harvester.name][HCCJC.HEALTH] = json.loads(response.text)
        else:
            feedback[harvester.name][HCCJC.HEALTH] = "unable do set configuration data of harvester {}".format(
                harvester.name)
        return Response(feedback, status=response.status_code)

    def get_status_history(self, harvester):
        return Response("status history not supported",
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def get_api_info(self, harvester):
        feedback = {}
        try:
            response = requests.get(
                harvester.url +
                HarvesterApiConstantsV6.PRETTY_FLAG,
                timeout=5)
        except ConnectionError:
            feedback[harvester.name] = "unable do get api info of harvester {}".format(
                harvester.name)
            return Response(
                feedback, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if response.status_code == status.HTTP_200_OK:
            feedback[harvester.name] = {}
            feedback[harvester.name] = response.text
        else:
            feedback[harvester.name] = "unable do get api info of harvester {}".format(
                harvester.name)
        return Response(feedback, status=response.status_code)


class VersionBased7Strategy(Strategy):
    """
    The algorithm/strategy implementation for the harvester
    library v7.x.x and v8.x.x using the strategy interface.
    """

    def get_harvester_status(self, harvester):
        feedback, harvester_json = {}, {}
        feedback[harvester.name] = {}
        max_documents = False
        response = None

        if harvester.enabled:
            try:
                status_url = harvester.url + HarvesterApiConstantsV7.PG_HARVEST
                response, harvester_json = a_response(
                    harvester.name, status_url, 'Get')

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
                elif response.status_code == status.HTTP_408_REQUEST_TIMEOUT:
                    feedback[harvester.name][HCCJC.HEALTH] = response.status_text
                    feedback[harvester.name][HCCJC.MESSAGE] = str(
                        response.data)
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                else:

                    # this line may produce a servererror 500 -> keyerror:
                    # health
                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.HEALTH]
                    # to be legacy (prior lib v7) compatible in html template
                    # set the old STATUS key to STATE
                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATE].lower(
                    )
                    feedback[harvester.name][HCCJC.CACHED_DOCS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.DATA_PROVIDER] = harvester_json[HCCJC.REPO_NAME]

                    # harvester overall status
                    if harvester_json[HCCJC.HEALTH] == HCCJC.OK and harvester_json[HCCJC.STATE].lower(
                    ) == HCCJC.IDLE:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS
                    elif harvester_json[HCCJC.HEALTH] != HCCJC.OK:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    elif harvester_json[HCCJC.STATE].lower() in [HCCJC.HARV]:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY
                    else:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                    # progress
                    if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                        max_documents = True
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = \
                            harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = \
                            harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                    else:
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = HCCJC.N_A

                    if max_documents:
                        if int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]) > 0:
                            feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                                int((int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100)
                                    / int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
                    else:
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                            int(harvester_json[HCCJC.HARVESTED_COUNT])

                    # dates
                    if HCCJC.LAST_HARVEST_DATE in harvester_json:
                        feedback[harvester.name][HCCJC.LAST_HARVEST_DATE] = \
                            harvester_json[HCCJC.LAST_HARVEST_DATE]
                    if HCCJC.NEXT_HARVEST_DATE in harvester_json:
                        feedback[harvester.name][HCCJC.NEXT_HARVEST_DATE] = \
                            harvester_json[HCCJC.NEXT_HARVEST_DATE]
                    if HCCJC.REMAIN_HARVEST_TIME in harvester_json:
                        feedback[harvester.name][HCCJC.REMAIN_HARVEST_TIME] = \
                            harvester_json[HCCJC.REMAIN_HARVEST_TIME]

                    # schedules
                    cron_url = harvester.url + HarvesterApiConstantsV7.G_HARVEST_CRON
                    response, harvester_json = a_response(
                        harvester.name, cron_url, 'Get')

                    tasks = harvester_json.values()
                    cronlist = list(tasks)[0]
                    if not cronlist:
                        feedback[harvester.name][HCCJC.CRONTAB] = HCCJC.NO_CRONTAB
                    else:
                        feedback[harvester.name][HCCJC.CRONTAB] = cronlist

            except RequestException as _e:

                feedback[harvester.name][HCCJC.HEALTH] = str(_e)
                feedback[harvester.name][HCCJC.STATUS] = "no status"
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback,
                            status=response.status_code if response is not None
                            else status.HTTP_408_REQUEST_TIMEOUT)

        return Response({harvester.name: 'disabled'},
                        status=status.HTTP_423_LOCKED)

    def post_start_harvest(self, harvester):
        response, _x = a_response(
            harvester.name, harvester.url + HarvesterApiConstantsV7.PG_HARVEST,
            'Post')
        return response

    def post_reset_harvest(self, harvester):
        response, _x = a_response(
            harvester.name,
            harvester.url + HarvesterApiConstantsV7.P_HARVEST_RESET, 'Post')
        return response

    def post_stop_harvest(self, harvester):
        response, _x = a_response(
            harvester.name,
            harvester.url + HarvesterApiConstantsV7.P_HARVEST_ABORT, 'Post')
        return response

    def get_harvester_log(self, harvester):
        now = datetime.datetime.now()
        feedback = {}
        feedback[harvester.name] = {}
        log_url = harvester.url + HarvesterApiConstantsV7.G_HARVEST_LOG + now.strftime(
            HarvesterApiConstantsV7.HARVESTER_LOG_FORMAT)
        response, hjson = a_response(harvester.name, log_url, 'Get')

        log_txt = str(hjson) if str(
            hjson) != "" else HCCJC.NO_LOGTEXT + ' for today: ' + str(now)
        feedback[harvester.name][HCCJC.LOGS] = log_txt
        return Response(feedback, status=response.status_code)

    def get_harvester_progress(self, harvester):
        feedback = {}
        feedback[harvester.name] = {}
        max_documents = False

        if harvester.enabled:

            response, harvester_json = a_response(
                harvester.name,
                harvester.url + HarvesterApiConstantsV7.PG_HARVEST, 'Get')

            feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[
                HCCJC.HARVESTED_COUNT]
            feedback[harvester.name][HCCJC.STATE] = harvester_json[
                HCCJC.STATE].lower()
            if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                max_documents = True
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = harvester_json[
                    HCCJC.MAX_DOCUMENT_COUNT]
                feedback[harvester.name][HCCJC.PROGRESS_MAX] = harvester_json[
                    HCCJC.MAX_DOCUMENT_COUNT]
            else:
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = HCCJC.N_A

            if HCCJC.REMAIN_HARVEST_TIME in harvester_json:
                feedback[harvester.name][
                    HCCJC.REMAIN_HARVEST_TIME] = harvester_json[
                        HCCJC.REMAIN_HARVEST_TIME]
            else:
                # Get time of the beginning of the harvest, if remaining
                # time is unknown.
                # Call etls instead of harvester_json["lastHarvestDate"],
                # because it is updated faster.
                get_url = harvester.url + HarvesterApiConstantsV7.STATE_HISTORY
                etls = requests.get(get_url, timeout=5)
                if etls.status_code == status.HTTP_200_OK:
                    etls_data = json.loads(etls.text)
                    last = etls_data["overallInfo"]["stateHistory"][-1]
                    if last["value"] == "HARVESTING":
                        feedback[harvester.name][
                            HCCJC.LAST_HARVEST_DATE] = last["timestamp"]
                    elif last["value"] == "QUEUED":
                        feedback[harvester.name][
                            "lastActivated"] = last["timestamp"]

            if max_documents:
                if int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]) > 0:
                    percentage = int(
                        (int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100) /
                        int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
                    feedback[harvester.name][
                        HCCJC.PROGRESS_CURRENT] = percentage
            else:
                feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(
                    harvester_json[HCCJC.HARVESTED_COUNT])

        return Response(feedback, status=response.status_code)

    def post_add_harvester_schedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        post_url = harvester.url + HarvesterApiConstantsV7.P_HARVEST_CRON
        response = requests.post(post_url,
                                 json={HCCJC.POSTCRONTAB: crontab},
                                 timeout=5)
        harvester_response = json.loads(response.text)
        LOGGER.info("created schedule for %s with crontab %s", harvester.name,
                    crontab)
        feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)

    def post_delete_harvester_schedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        if not crontab:
            delall_cron_url = harvester.url + HarvesterApiConstantsV7.DALL_HARVEST_CRON
            response = requests.post(delall_cron_url, timeout=5)
            harvester_response = json.loads(response.text)
            LOGGER.info("deleted all schedules for %s", harvester.name)
            feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        else:
            delcron_url = harvester.url + HarvesterApiConstantsV7.D_HARVEST_CRON
            response = requests.post(delcron_url,
                                     json={HCCJC.POSTCRONTAB: crontab},
                                     timeout=5)
            harvester_response = json.loads(response.text)
            LOGGER.info(
                "deleted cron %s for harvester %s",
                crontab,
                harvester.name)
            feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)

    def get_harvester_config(self, harvester):
        get_url = harvester.url + HarvesterApiConstantsV7.G_HARVEST_CONFIG
        response = requests.get(get_url, timeout=5)
        feedback = {}
        feedback[harvester.name] = {}
        if response.status_code == status.HTTP_200_OK:
            feedback[harvester.name][HCCJC.HEALTH] = json.loads(response.text)
        else:
            feedback[harvester.name][HCCJC.HEALTH] = "unable do get configuration data of harvester {}".format(
                harvester.name)
        return Response(feedback, status=response.status_code)

    def set_harvester_config(self, harvester, changes):
        set_url = harvester.url + HarvesterApiConstantsV7.P_HARVEST_CONFIG
        response = requests.post(set_url, json=changes, timeout=5)
        feedback = {}
        feedback[harvester.name] = {}
        feedback[harvester.name][HCCJC.HEALTH] = json.loads(response.text)
        return Response(feedback, status=response.status_code)

    def get_status_history(self, harvester):
        get_url = harvester.url + HarvesterApiConstantsV7.STATE_HISTORY
        try:
            response = requests.get(get_url, timeout=5)
        except requests.exceptions.ReadTimeout:
            feedback = "server is not responding for harvester {}".format(
                harvester.name)
            return Response(feedback, status=response.status_code)
        response_data = json.loads(response.text).copy()
        feedback = {}
        feedback[harvester.name] = {}
        if response.status_code == status.HTTP_200_OK:
            history_data = ""
            for info in response_data["overallInfo"]["stateHistory"]:
                ms = info["timestamp"]
                time = datetime.datetime.fromtimestamp(ms / 1000.0)
                converted_time = time.strftime("%d-%b-%Y %H:%M:%S")
                history_data += converted_time + ": " + \
                    info["value"].lower() + "<br>"
            feedback = history_data
        else:
            if "message" in response_data:
                feedback = response_data["message"]
            else:
                feedback = "unable do get status history of harvester {}".format(
                    harvester.name)
        return Response(feedback, status=response.status_code)

    def get_api_info(self, harvester):
        feedback = {}
        try:
            get_url = harvester.url + HarvesterApiConstantsV7.PG_HARVEST + \
                HarvesterApiConstantsV7.PRETTY_FLAG
            response = requests.get(get_url, timeout=5)
        except requests.exceptions.ConnectionError:
            feedback[harvester.name] = "unable do get api info of harvester {}".format(
                harvester.name)
            return Response(
                feedback, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if response.status_code == status.HTTP_200_OK:
            feedback[harvester.name] = {}
            feedback[harvester.name] = response.text
        else:
            feedback[harvester.name] = "unable do get api info of harvester {}".format(
                harvester.name)
        return Response(feedback, status=response.status_code)
