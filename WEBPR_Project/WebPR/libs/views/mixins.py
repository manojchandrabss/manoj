from django.http import JsonResponse, HttpResponseNotAllowed


class AjaxableResponseMixin(object):
    """Mixin to add AJAX support to a form.

    Must be used with an object-based FormView (e.g. CreateView)

    """

    def dispatch(self, *args, **kwargs):
        """Base request dispatch.

        If request is not AJAX - returns HTTP 405 error.

        """
        if not self.request.is_ajax():
            return HttpResponseNotAllowed(['GET', 'POST'])

        return super(AjaxableResponseMixin, self).dispatch(*args, **kwargs)

    def form_invalid(self, form):
        super(AjaxableResponseMixin, self).form_invalid(form)

        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        super(AjaxableResponseMixin, self).form_valid(form)

        data = {
            'pk': self.object.pk,
        }
        return JsonResponse(data)
