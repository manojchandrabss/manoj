from django.utils.safestring import  mark_safe
from django.core.urlresolvers import reverse
from django.utils.html import format_html, conditional_escape
from django import forms
from functools import partial
from django.forms.models import modelform_factory


class ForbidDeleteAdd(object):

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class FkAdminLink(object):
    """
    Link to object in admin
    Example usage:
    class Book(models.Model):
        author = models.ForeignKey('user')
        content = models.TextField()


    class BookAdmin(models.ModelAdmin):
        readonly_fields = ('_author', )

        def _author(self, obj):
            return self._admin_url(obj.author)
            # or
            # return self._admin_url(obj.author,
                    obj.author.last_name + obj.author.first_name[0])
    """

    def _admin_url(self, obj, title=None):
        if not title:
            title = conditional_escape(obj.__str__())

        admin_url_str = 'admin:{}_{}_change'.format(
              obj._meta.app_label,
              obj._meta.object_name.lower()
            )
        admin_url = reverse(admin_url_str, args=[obj.pk])

        return format_html(mark_safe(
            "<a href='{}' target='_blank'>{}</a>".format(admin_url, title)))


class AllFieldsReadOnly(object):
    '''
    Simple mixin if you want to make all fields readonly
    without specifying fields attribute
    '''

    def get_readonly_fields(self, request, obj=None):
        if self.fields:
            return self.fields

        # took this django sources
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistent with the
        # default on modelform_factory
        exclude = exclude or None

        defaults = {
            "form": self.form,
            "fields": forms.ALL_FIELDS,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        form = modelform_factory(self.model, **defaults)
        return list(form.base_fields)
