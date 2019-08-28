"""
The forms module.
"""
from crispy_forms.bootstrap import FieldWithButtons, FormActions, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from api.models import Harvester

__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class HarvesterForm(forms.ModelForm):
    """
    This class represents a HarvesterRegistration Form.
    It smoothly integrates into bootstrap design via crispy-forms framework.
    The helper property comes from crispy forms and configures thew form.
    """

    class Meta:
        model = Harvester
        fields = ['name', 'notes', 'url']

    @property
    def helper(self):
        """helper method to configure the form"""
        helper = FormHelper()
        helper.form_method = 'POST'
        helper.form_class = 'form-horizontal'
        helper.form_tag = False  # render form DOM element
        helper.render_unmentioned_fields = True  # render all fields
        helper.label_class = 'col-md-5'
        helper.field_class = 'col-md-10'
        # helper.layout = Layout(
        #    FormActions(
        # Submit('edit-harvester', 'Register', css_class="btn-primary")))
        return helper


class ConfigForm(forms.Form):
    """
    This class represents a dynamic Harvester Configuration Form. It is created every
    time create_config_form is called.
    """
    pass


def create_config_fields(config_data):
    """
    This function validates the input data to data and fields used for
    create_config_form(config_data) to create a ConfigForm
    INPUT:
     - config_data : JSON configuration data
    OUTPUT:
     - fields : dictionary of field names with fields type
     - data : dictionary of field names with current value
    """
    fields = {}
    data = {}

    for key in config_data.keys():
        for field in config_data[key]["parameters"]:
            if field["type"] == "IntegerParameter":
                fields["{}.{}".format(key, field["key"])
                       ] = forms.IntegerField(required=False)
                field_type = "integer"
            elif field["type"] == "StringParameter":
                fields["{}.{}".format(key, field["key"])
                       ] = forms.CharField(required=False)
                field_type = "string"
            elif field["type"] == "BooleanParameter":
                fields["{}.{}".format(key, field["key"])
                       ] = forms.BooleanField(required=False)
                field_type = "boolean"
            elif field["type"] == "PasswordParameter":
                fields["{}.{}".format(key, field["key"])] = forms.CharField(
                    required=False, widget=forms.PasswordInput())
                field_type = "password"
            else:
                fields["{}.{}".format(key, field["key"])
                       ] = forms.CharField(required=False)

            if "value" in field:
                data["{}.{}".format(key, field["key"])] = field["value"]
            else:  # set default values, if value is not set
                if field_type == "integer":
                    data["{}.{}".format(key, field["key"])] = 0
                elif field_type == "string":
                    data["{}.{}".format(key, field["key"])] = ""
                elif field_type == "boolean":
                    data["{}.{}".format(key, field["key"])] = False
                elif field_type == "password":
                    data["{}.{}".format(key, field["key"])] = ""
                else:
                    data["{}.{}".format(key, field["key"])] = None
    return fields, data


def create_config_form(config_data):
    """
    This function creates a ConfigForm: a dynamic Form for Harvester Configuration.
    """
    fields, data = create_config_fields(config_data)
    DynamicConfigForm = type('DynamicConfigForm', (ConfigForm,), fields)
    return DynamicConfigForm(data)


class LoginForm(AuthenticationForm):
    """
    This class represents a Login Form used with crispy forms.
    A helper property had to  be called in order to use crispy forms styling.
    """
    username = forms.CharField(label="", required=True)
    password = forms.CharField(label="",
                               required=True,
                               widget=forms.PasswordInput)

    @property
    def helper(self):
        """helper method to configure the form"""
        helper = FormHelper()
        helper.form_method = 'POST'
        helper.form_class = 'form-horizontal'
        helper.layout = Layout(
            PrependedText('username',
                          '<i class="fa fa-user" aria-hidden="true"></i>',
                          css_class='form-control',
                          placeholder='Username'),
            PrependedText('password',
                          '<i class="fa fa-unlock" aria-hidden="true"></i>',
                          css_class='form-control',
                          placeholder='Password'),
            FormActions(Submit('login', 'login', css_class="btn-primary")))
        return helper


class SchedulerForm(forms.Form):
    """
    This class represents a Scheduling Form used with crispy forms.
    A helper property had to  be called in order to use crispy forms styling.
    """
    cronTab = forms.CharField(label="Scheduling Plan:",
                              max_length=14,
                              required=False)

    @property
    def helper(self):
        """helper to config the form"""
        helper = FormHelper()
        helper.form_tag = False
        helper.layout = Layout(
            FieldWithButtons(
                'cronTab',
                Submit('submit_cron', 'set!', css_class="btn-default btn-sm")))
        return helper

class UploadFileForm(forms.Form):
    """
    This class represents a form for uploading a file for adding 
    several harvesters to the database at a time
    """
    upload_file = forms.FileField(label="File:")