from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from libs.admin.mixins import FkAdminLink
from .models import (AppUser, Account, APIKey)


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    """
    Class to manage system users
    """
    list_display = ('username', 'email', 'account', 'first_name', 'last_name',
                    'is_staff', 'last_login')
    list_display_links = ('username',)
    list_select_related = ('account',)
    fieldsets = (

        (None, {'fields': ('username', 'password')}),
        (None, {'fields': ('account', 'role')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                        'avatar')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class AppUserInlineAdmin(FkAdminLink, admin.TabularInline):
    """Inline for viewing users related to this Account
    """
    model = AppUser
    fields = ['_username', 'role', 'full_name']
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def _username(self, obj):
        return self._admin_url(obj, title=obj.username)
    _username.short_description = "Username"


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Tool to create and manage system accounts
    """
    list_display = ('company_name', 'type',)
    list_display_links = ('company_name',)
    fields = ['company_name', 'type', 'plan', 'merchants', 'is_active']
    inlines = [AppUserInlineAdmin]


# Option to manage API keys from different services
admin.site.register(APIKey)
