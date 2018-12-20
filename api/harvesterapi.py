# import base64

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HarvesterApiConstantsV6:
    """

     This Class holds a list of Harvester API constants which will be updated accordingly to the Harvester-BaseLibrary.

    """
    P_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    P_HARVEST_SUBMIT = "/submit"
    P_HARVEST_SAVE = "/save"
    PD_HARVEST_CRON = "/schedule?cron="
    GD_HARVEST_CRON = "/schedule"
    G_STATUS = "/status/state"
    G_HEALTH = "/status/health"
    G_PROGRESS = "/status/progress"
    G_MAX_DOCS = "/status/max-documents"
    G_DATA_PROVIDER = "/status/data-provider"
    G_HARVESTED_DOCS = "/status/harvested-documents"
    G_BOOLEAN_OUTDATED_DOCS = "/outdated"

    # HARVESTER_USER = ""
    # HARVESTER_PASS = ""
    # credentials = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)
