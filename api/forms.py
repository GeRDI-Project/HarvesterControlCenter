from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

class HarvesterForm(forms.Form):
    name = forms.CharField(label='Harvester Name', max_length=255, required=True)
    repository = forms.CharField(label='Harvester Repository', max_length=255, required=True)
    url = forms.URLField(initial='https://', label='Harvester URL', max_length=255, required=True)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False # don't render form DOM element
        helper.render_unmentioned_fields = True # render all fields
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-10'
        return helper
