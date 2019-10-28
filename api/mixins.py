from django.http import JsonResponse

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form.
    FormMixin must be inherited in the class to use AjaxableResponseMixin.
    For examples see views_v2.py#ConfigHarvesterView or ScheduleHarvesterView
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        """
        We make sure to call the parent's form_valid() method because
        it might do some processing (in the case of CreateView, it will
        call form.save() for example).
        """
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response
