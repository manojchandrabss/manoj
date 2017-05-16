from django import forms
from django.utils.timezone import now

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, HTML, Div
from localflavor.us.forms import (USStateField, USZipCodeField,
                                  USStateSelect, USPhoneNumberField)

from apps.mentions.forms.fields import (MerchantCategoryModelChoiceField,
                                        AltLocationField,
                                        CustomMultiValueField)
from apps.mentions.forms.layouts import merchant_layout
from apps.mentions.forms.widgets import ArrayCheckboxSelectMultiple
from apps.mentions.models import Category, Merchant, Tracker, ToDo
from apps.users.models import AppUser


class TrackerModelForm(forms.ModelForm):
    """Form for adding Tracker to display on trackers page.

    Define common fields:
      merchant, social_networks, search_terms.

    """
    class Meta:
        model = Tracker
        fields = ('merchant', 'social_networks')

    def __init__(self, *args, **kwargs):
        """Adding Crispy form helper to the form.
        """
        super().__init__(*args, **kwargs)

        self.fields['social_networks'].choices = Tracker.SOCIAL_CHOICES
        self.fields['social_networks'].widget = ArrayCheckboxSelectMultiple()
        self.helper = FormHelper()
        self.helper.form_id = 'tracker_add_id'
        self.helper.form_class = 'form'
        self.form_show_labels = True
        self.helper.layout = Layout(
            Field('merchant'),
            Div('social_networks', css_class='checkboxes-inline'),
            # Field('search_terms', rows=3),
            HTML('<button type="submit" class="btn btn-white btn-block mb10" '
                 'id="submit-id-save" onclick="Tracker.save(this); '
                 'return false;">SAVE</button>'),
            HTML('<a href="" onclick="Tracker.remove(this); return false;" '
                 'class="btn btn-white btn-block mb10">REMOVE COLUMN</a>'),
            HTML('<div class="text-center mt10"><a href="" '
                 'class="btn btn-link btn-dark" '
                 'onclick="Tracker.closeSettings(); '
                 'return false;">Cancel</a></div>'),
        )


class AddToDoModelForm(forms.ModelForm):
    """Form for model to add to-do for certain mentions.

    Create to-do in DB and show it in the list of to-do.

    Attributes:
      user (int): User ID
      priority (str): A choice from to-do's priority choices list.

    """
    user = forms.ModelChoiceField(queryset=AppUser.objects.all(),
                                  required=True, label='Assign to')
    priority = forms.ChoiceField(choices=ToDo._PRIORITY, required=True,
                                 label='Priority')
    due_date = forms.DateTimeField(error_messages={'invalid': 'error'})

    class Meta:
        model = ToDo
        fields = ('user', 'comment', 'priority', 'due_date')

    def __init__(self, *args, **kwargs):
        user_qs = kwargs.pop('user_qs', [])
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = user_qs

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < now():
            raise forms.ValidationError(message='This date is from past',
                                        code='invalid')
        return due_date


class MerchantModelForm(forms.ModelForm):
    """Form form Merchant model.

    Attributes:
      official_name (str): Business name.
      short_name (array of str): Array for short name.
      category (Category): FK to Category.
      web_page (array of URLs): Array for company urls.
      address (str): Adress of headquarter.
      city (str): City.
      state (USStateField): State of US.
      zip_code (USZipCodeField): Zip code.
      phone (array of PhoneNumberField): Phone numbers.
      product (array of str): Names of products which could identify
        a merchant.
      start_date (datetime): Date which we start search from, usually
        date of merchant creation.
      dda (str): Some number to identify client (waiting for PM/client
        comments).
      chargeback_total (int): Count of chargebacks.
      chargeback_prevented (int): Count of prevented chargebacks.
      last_search_date (datetime): Date of last search.
      mentions_found (int): Count of merchant.
      ceo (str): CEO name.
      email (str): Business email.
    """
    official_name = forms.CharField(max_length=255, label='Business Name')
    phone = CustomMultiValueField(field=USPhoneNumberField(), count=3,
                                  required=False, label='Phone Number(s)')
    short_name = CustomMultiValueField(count=3, required=False,
                                       label='Alt Business Name (optional)')
    product = CustomMultiValueField(count=3, required=False,
                                    label='Product Name(s)')
    address = forms.CharField(max_length=255, required=False,
                              label='Business Address 1')
    web_page = CustomMultiValueField(count=5, required=False,
                                     label='Business URL(s)')
    city = forms.CharField(max_length=255, required=False, label='')
    state = USStateField(required=False, label='', widget=USStateSelect())
    zip_code = USZipCodeField(required=False, label='')
    dda = forms.CharField(max_length=255, label='DDA (Descriptor)',
                          required=False)
    ceo = CustomMultiValueField(count=3, required=False,
                                label='Key Personnel')
    category = MerchantCategoryModelChoiceField(
      queryset=Category.objects.order_by('name', 'code'), required=False,
      label='Industry')
    contact_info = forms.CharField(max_length=255, required=False,
                                   label='Contact Info')
    location = AltLocationField(required=False, label='Business Address 2')

    def __init__(self,  *args, **kwargs):
        """Add crispy form helper to this form.

        Set class and layout for the form.

        """
        super().__init__(*args, **kwargs)

        self.fields['sources'].choices = Tracker.SOCIAL_CHOICES
        self.fields['sources'].widget = ArrayCheckboxSelectMultiple()
        self.helper = FormHelper()
        self.helper.field_class = 'sm'
        self.helper.layout = merchant_layout

    class Meta:
        model = Merchant
        fields = ['official_name', 'short_name', 'address', 'city', 'state',
                  'zip_code', 'phone', 'product', 'web_page', 'ceo', 'dda',
                  'category', 'contact_info', 'location', 'exclude_words',
                  'search_settings', 'sources']
        widgets = {
            'exclude_words': forms.Textarea(attrs={'rows': 3}),
            'search_settings': forms.Textarea(attrs={'rows': 5})
        }


class AddMerchantForm(MerchantModelForm):
    """Form to add Merchant by ISO dashboard.

    Redefining a 'save' method for provides 'request'.

    """

    def save(self, request):
        """Save merchant and set it into current account.

        Args:
          request: Request.

        Returns:
          merchant (object): Instance of Merchant.

        """
        merchant = Merchant(**self.cleaned_data)
        merchant.save()
        merchant.account_set.add(request.user.account)
        return merchant
