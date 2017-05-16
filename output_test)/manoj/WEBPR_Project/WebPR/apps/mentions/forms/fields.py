from copy import copy

from django import forms

from localflavor.us.forms import USStateField, USZipCodeField

from apps.mentions.forms.widgets import (TextInputMultiWidget,
                                         AltLocationWidget)


class CustomMultiValueField(forms.MultiValueField):
    """Custom form multi value field for ArrayFields.

    Args:
      field (object): A django form`s field object, default CharField.
      count (int): A fields count. The count uses during generation fields
                   list for Django`s MultiValueField.

    """

    def __init__(self, field=None, count=1, *args, **kwargs):
        """Constructor for CustomMultiValueField.

        Setting up count of fields (it will use for generation fields and
        widgets) and providing fields list to parent`s init.

        """
        field = field or forms.CharField(max_length=255)
        list_fields = [copy(field) for _ in range(count)]
        self.widget = TextInputMultiWidget(count=count)
        super().__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return [value for value in values if value.strip()]


class AltLocationField(forms.MultiValueField):
    """Alternative location field.

    The widget decompressed string value from a textarea and present it as
    separated fields.

    """
    widget = AltLocationWidget

    def __init__(self, *args, **kwargs):
        """Constructor for AltLocationField.

        Setting up and providing fields list to parent`s init.

        """
        list_fields = [
            forms.CharField(max_length=255),
            forms.CharField(max_length=255),
            USStateField(),
            USZipCodeField()
        ]
        super().__init__(list_fields, *args, **kwargs)

    def compress(self, values):
        return ','.join(values or [])


class MerchantCategoryModelChoiceField(forms.ModelChoiceField):
    """Custom field for Category choices.

    The field uses for AddMerchantForm for merchant's industry select. But the
    select has to looks like this: `0123 (Some category title)`.

    """

    def label_from_instance(self, obj):
        return '{0} - {1}'.format(obj.code, obj.name)
