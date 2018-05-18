# import base64

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HarvesterApi:
    """

     This Class holds a list of Harvester API constants which will be updated accordingly to the Harvester-BaseLibrary.

    """
    P_HARVEST = "/harvest"
    P_HARVEST_ABORT = "/harvest/abort"
    P_HARVEST_RESET = "/harvest/reset"
    P_HARVEST_SUBMIT = "/harvest/submit"
    P_HARVEST_SAVE = "/harvest/save"
    P_HARVEST_CRON = "/harvest/schedule?cron="
    G_HARVEST_CRON = "/harvest/schedule"
    G_STATUS = "/harvest/status/state"
    G_HEALTH = "/harvest/status/health"
    G_PROGRESS = "/harvest/status/progress"
    G_MAX_DOCS = "/harvest/status/max-documents"
    G_DATA_PROVIDER = "/harvest/status/data-provider"
    G_HARVESTED_DOCS = "/harvest/status/harvested-documents"
    G_BOOLEAN_OUTDATED_DOCS = "/harvest/outdated"
    D_HARVEST_CRON = "/harvest/schedule?cron="
    D_HARVEST_ALLCRONS = "/harvest/schedule"

    # HARVESTER_USER = ""
    # HARVESTER_PASS = ""
    # credentials = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)
