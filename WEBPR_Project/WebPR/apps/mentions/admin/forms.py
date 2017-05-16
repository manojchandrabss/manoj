from io import TextIOWrapper

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field, HTML

from .utils import parse_merchants_csv


class ImportMerchantsForm(forms.Form):
    """Form for importing merchants from .csv file.

    Call util for parsing .csv file for validating incoming csv file
    """
    csv_file = forms.FileField(label='.csv file')
    # delete_others = forms.BooleanField(label='Delete other merchants',
    #                                    initial=False, required=False)
    # assign_to = forms.ModelChoiceField(
    #     queryset=Account.objects.filter(type=Account.ISO),
    #     label='Assign to ISO')

    def __init__(self, *args, **kwargs):
        """Adding Crispy form helper to the form.
        """
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_action = 'mentions:bulk_import'
        self.helper.form_id = 'bulk_merchant_import'
        self.helper.layout = Layout(
            Fieldset(
                None,
                HTML("<h2>Import merchants</h2>"),
                HTML('<a href="/download_sample">Download sample .csv</a>'),
                Div(Field('csv_file'), css_class='form-row'),
                css_class='module aligned'),
            Submit('submit', 'Submit', css_class='pull-right')
        )

    def clean(self):
        """Validating that incoming .csv file can be parsed and saving parsed
        data to self.merchants
        """
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        # try:
        self.merchants, self.validation_errors = parse_merchants_csv(
            opened_file=TextIOWrapper(cleaned_data['csv_file'].file)
        )
        # except Exception as e:
        #     raise ValidationError({'csv_file': '{}'.format(e)})
