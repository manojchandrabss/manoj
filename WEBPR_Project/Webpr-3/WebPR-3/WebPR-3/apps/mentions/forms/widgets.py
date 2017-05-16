"""
Custom widgets and fields for form 'Add Merchant'
to provide multi field functionality
"""
from copy import copy
from itertools import repeat
from operator import itemgetter

from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from localflavor.us.forms import USStateSelect


class TextInputMultiWidget(forms.MultiWidget):
    """Widget for multiple CharFields.

    Provides all fields with same template, that includes button for
    removing the fields excludes first field.

    Attributes:
      template (string): The widget template.
      button_template (string): A remove button template.
      widget (int): A default widget. The widget (TextInput) will use in
                    all fields, these will use this multi widget.

    Args:
      count (int): Count of widgets, that will be used for a field width the
                   multiwidget. Default is 1.
      attrs (dict): Attr for Djando`s MultiWidget.

    """
    template = (
        '<div class="form-group sm has-control {0}"'
        'id="alt_name_{1}">{2}{3}</div>'
    )
    button_template = (
        '<button type="button" class="clear-value click-handler" '
        'data-handler="removeField" onclick="return false;">×</button>'
    )
    widget = forms.TextInput

    def __init__(self, count=1, attrs=None):
        """Constructor for MultiWidget.

        Setting up count of widgets (it will use for generation fields and
        widgets) and providing generated widgets list to parent class`s init.

        """
        self.count = count
        widgets = [copy(self.widget) for _ in range(count)]
        super().__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        """Define output for the widget.

        Makes fields template and wrap field widget.

        Args:
          rendered_widgets (list): List of rendered widgets.

        Returns (string): Joined list of widget`s HTML.

        """
        widget_context = []

        for index, widget in enumerate(rendered_widgets):
            template = self.template.format(
                ('hidden' if index and 'value' not in widget else ''), index,
                (self.button_template if index else ''), widget
            )
            widget_context.append(template)

        return ''.join(widget_context)

    def decompress(self, value):
        """Function to decompress valuse from form.

        Args:
          value (string): Comma-separated values string from ArrayField.

        Returns (list): Values list if exist, else empty list.

        """
        if value:
            return value.split(',')
        else:
            return list(repeat('', self.count))


class AltLocationWidget(forms.MultiWidget):
    """Alternative location widget.

    Custom widget for location model field. The model field is TextField and
    stores data as string.

    Attributes:
      template (string): The widget template.

    Args:
      attrs (dict): Attributes dict for Django`s MultiWidget.

    """
    template = (
        '<div class="form-group sm" id="alt_adr">{0}</div>'
        '<div class="col-md-5 pr0 pl0">'
        '<div class="form-group" id="alt_city">{1}</div></div>'
        '<div class="col-md-4 pr0 pl10">'
        '<div class="form-group" id="alt_phone">{2}</div></div>'
        '<div class="col-md-3 pl10 pr0">'
        '<div class="form-group" id="alt_phone">{3}</div></div>'
    )

    def __init__(self, attrs=None):
        """Constructor for MultiWidget.

        Setting up list of widgets and providing this to parent (MultiWidget).

        """
        widgets = [
            forms.TextInput(attrs={'placeholder': 'Address'}),
            forms.TextInput(attrs={'placeholder': 'City'}),
            USStateSelect,
            forms.TextInput(attrs={'placeholder': 'ZIP'})
        ]
        super().__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        """Function to define output format with hide button.

        Returns (string): Final defining result of the widgets rendering.
                          HTML of concatinated of all widgets.

        """
        widget_context = self.template.format(
            *itemgetter(0, 1, 2, 3)(rendered_widgets)
        )
        return widget_context

    def decompress(self, value):
        """"Function to decompress values from form.

        Returns (list): List of decompressed values from string. Used for
                        initial form values.

        """
        if value:
            return value.split(',')
        else:
            return list(repeat('', 4))


class ArrayCheckboxSelectMultiple(CheckboxSelectMultiple):
    """The Widget displays form based on ArrayField values.

    Render ArrayField comma-separated values to form as multiple select with
    checkboxes.

    """

    def value_from_datadict(self, data, files, name):
        return ','.join(data.getlist(name))

    def render(self, name, value, attrs=None, choices=()):
        if value:
            value = value.split(',')
        return super().render(name, value, attrs=attrs, choices=choices)
