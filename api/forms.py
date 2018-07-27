from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons
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
    """
    This class represents a HarvesterRegistration Form.
    It smoothly integrates into bootstrap design via crispy-forms framework.
    The helper property comes from crispy forms and configures thew form.
    """

    class Meta:
        model = Harvester
        fields = ['name', 'repository', 'url']

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'POST'
        helper.form_class = 'form-horizontal'
        helper.form_tag = True  # render form DOM element
        helper.render_unmentioned_fields = True  # render all fields
        helper.label_class = 'col-md-5'
        helper.field_class = 'col-md-10'
        helper.layout = Layout(
            FormActions(
                Submit('hreg-form', 'Register', css_class="btn-primary")
            )
        )
        return helper


class LoginForm(AuthenticationForm):
    """
    This class represents a Login Form used with crispy forms.
    A helper property had to  be called in order to use crispy forms styling.
    """
    username = forms.CharField(label="", required=True)
    password = forms.CharField(label="", required=True, widget=forms.PasswordInput)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'POST'
        helper.form_class = 'form-horizontal'
        helper.layout = Layout(
            PrependedText('username', '<i class="fa fa-user" aria-hidden="true"></i>',
                          css_class='form-control', placeholder='Username'),
            PrependedText('password', '<i class="fa fa-unlock" aria-hidden="true"></i>',
                          css_class='form-control', placeholder='Password'),
            FormActions(
                Submit('login', 'login', css_class="btn-primary")
            )
        )
        return helper


class SchedulerForm(forms.Form):
    """
    This class represents a Scheduling Form used with crispy forms.
    A helper property had to  be called in order to use crispy forms styling.
    """
    schedule = forms.CharField(label="Scheduling Plan:", required=False)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.layout = Layout(
            FieldWithButtons('schedule', Submit('submit_cron', 'set!', css_class="btn-default btn-sm"))
        )
        return helper
