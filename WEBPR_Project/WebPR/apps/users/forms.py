from django import forms
from allauth.account.utils import get_adapter, setup_user_email
from allauth.utils import email_address_exists
from apps.users.models import AppUser, Account
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout
from apps.mentions.models import Merchant


class UserCreationForm(forms.ModelForm):
    """Form for adding user to merchant account.
    Define common fields:
        username, first_name, last_name, email, avatar.
    Used in `users.views.CreateUserForMerchant` view.
    """
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    merchant = forms.ModelChoiceField(queryset=Merchant.objects.all())

    class Meta:
        model = AppUser
        fields = ('avatar', 'username', 'first_name', 'last_name', 'email', )

    def __init__(self, merchants, *args, **kwargs):
        """Add crispy form helper to this form with predefined layout.

        Also define `queryset` attribute of merchant field. Merchants depends
        on requested user (ISO can add user to any of it's merchants account,
        merchants can add users just to it's account. This logic is inside
        views)

        Args:
            merchants (QuerySet): list of merchants avaible
        """
        super().__init__(*args, **kwargs)
        self.fields['merchant'].queryset = merchants
        self.helper = FormHelper()
        self.helper.form_action = 'users:create_user'
        self.helper.form_show_labels = False
        self.helper.field_class = 'sm'
        self.helper.form_id = 'id-create-user'
        self.helper.layout = Layout(
            Field('avatar', style="display: none"),
            Field('username', placeholder='Username'),
            Field('first_name', placeholder='First name'),
            Field('last_name', placeholder='Last name'),
            Field('email', placeholder='Email'),
            Field('merchant', type='hidden'),
            HTML('<button type="submit" class="btn btn-lg btn-blue btn-block" '
                 'data-handler="save">Save</button>')
        )

    def clean_email(self):
        """Check that email address is unique.

        Returns:
            str: cleaned email
        Raises:
            Validation error if email is nit unique
        """
        value = self.cleaned_data["email"]
        value = get_adapter().clean_email(value)
        if value and email_address_exists(value):
            raise forms.ValidationError("A user is already registered"
                                        " with this e-mail address.")
        return value

    def save(self, request):
        """Save new user with data from form. Used functions from allauth
        adapter and custom actions, like setting up user role and avatar.

        Returns:
            new user
        """
        adapter = get_adapter()
        user = AppUser()
        user = adapter.save_user(request, user, self, commit=False)
        avatar = request.FILES.get('avatar')
        if avatar:
            user.avatar.save(avatar.name, avatar)
        user.role = AppUser.USER_ROLE

        # set account for new user
        # users can be added just to merchant's account
        merchant = self.cleaned_data['merchant']
        account, _ = merchant.account_set.get_or_create(type=Account.MERCHANT)
        user.account = account
        user.save()
        setup_user_email(request, user, [])
        return user
