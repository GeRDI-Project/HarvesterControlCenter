from crispy_forms.bootstrap import FormActions, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from api.models import Harvester

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HarvesterForm(forms.ModelForm):
    class Meta:
        model = Harvester
        fields = ['name', 'repository', 'url']

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False  # don't render form DOM element
        helper.render_unmentioned_fields = True  # render all fields
        helper.label_class = 'col-md-2'
        helper.field_class = 'col-md-10'
        return helper


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="", required=True)
    password = forms.CharField(label="", required=True, widget=forms.PasswordInput)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'POST'
        helper.form_class = 'form-horizontal'
        helper.layout = Layout(
            PrependedText('username', '<i class="fa fa-user" aria-hidden="true"></i>',
                          css_class='form-control-sm', placeholder='Username'),
            PrependedText('password', '<i class="fa fa-unlock" aria-hidden="true"></i>',
                          css_class='form-control-sm', placeholder='Password'),
            FormActions(
                Submit('login', 'login', css_class="btn-primary")
            )
        )
        return helper
