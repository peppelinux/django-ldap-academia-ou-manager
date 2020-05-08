from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.utils.html import mark_safe

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .admin_actions import *
from .admin_filters import TitleListFilter, AffiliationListFilter
from .admin_utils import (get_values_as_html_ul,)
from .forms import (LdapAcademiaUserAdminForm,
                    LdapGroupAdminMultiValuedForm) #, FileImportActionForm
from .hash_functions import encode_secret
from .models import *


class ReadOnlyAdmin(admin.ModelAdmin):
    """
    Disables all editing capabilities
    """
    def __init__(self, *args, **kwargs):
        super(ReadOnlyAdmin, self).__init__(*args, **kwargs)
        self.readonly_fields = [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super(ReadOnlyAdmin, self).get_actions(request)
        if actions.get('delete_selected'):
            del actions["delete_selected"]
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):  # pragma: nocover
        pass

    def delete_model(self, request, obj):  # pragma: nocover
        pass

    def save_related(self, request, form, formsets, change):  # pragma: nocover
        pass

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(ReadOnlyAdmin, self).change_view(request,
                                                      object_id,
                                                      extra_context=extra_context)


@admin.register(LogEntry)
class LogEntryAdmin(ReadOnlyAdmin):
    list_display = (
                    # 'object_id',
                    'repr_action',
                    'object_repr',
                    # 'content',
                    'change_message',
                    'user',
                    'action_time')
    list_filter = ('action_flag',
                    )
    search_fields = ('user__username',
                     'object_repr',)
    readonly_fields = ('repr_action',
                      )

    class Media:
        js = ('js/textarea-autosize.js',)

    def repr_action(self, obj):
        d = {
                1: 'Create',
                2: 'Change',
                3: 'Delete',
            }
        return d[obj.action_flag]
    repr_action.short_description = 'Action'


class LdapDbModelAdmin(admin.ModelAdmin):
    exclude = ['dn', 'objectClass']

    class Media:
        js = ('js/textarea-autosize.js',
              'js/given_display_name_autofill.js')


@admin.register(LdapAcademiaUser)
class LdapAcademiaUserAdmin(LdapDbModelAdmin):
    form = LdapAcademiaUserAdminForm
    list_display = ('uid',
                    'givenName',
                    'get_emails_as_ul',
                    'get_affiliation_as_ul',
                    'get_status',
                    # 'get_membership_as_ul',
                    'createTimestamp',
                    'modifyTimestamp')
    list_filter = (AffiliationListFilter,
                   TitleListFilter,
                   # 'pwdChangedTime', 'created', 'modified',
                   ('createTimestamp', DateRangeFilter),
                   ('modifyTimestamp', DateTimeRangeFilter),
                   ('pwdChangedTime', DateTimeRangeFilter),
                   ('schacExpiryDate', DateTimeRangeFilter),
                  )
    search_fields = ('uid',
                     'givenName',
                     'displayName',
                     'mail', # https://github.com/django-ldapdb/django-ldapdb/issues/104
                     )
    readonly_fields = (
                       'createTimestamp',
                       'modifyTimestamp',
                       'distinguished_name',
                       'creatorsName',
                       'modifiersName',
                       'get_membership_as_ul',
                       'membership',
                       #'pwdAccountLockedTime',
                       'locked_time',
                       'failure_times',
                       'pwdChangedTime',
                       #'pwd_changed'
                       'pwdHistory_repr',
                       'userPassword',
                       'sambaNTPassword',
                       'eduPersonPrincipalName',
                       )
    actions = [send_reset_token_email,
               enable_account,
               disable_account,
               lock_account,
               export_as_json,
               export_as_ldif]

    # action_form = FileImportActionForm

    # TODO: aggregate lookup for evaluating min max on records
    # date_hierarchy = 'created'

    fieldsets = (
        (None, { 'fields' : (('uid',
                              'distinguished_name'
                              ),
                              ('givenName', 'sn', ),
                              ('cn', 'displayName',),
                            ('mail', 'telephoneNumber'),
                            ('title'),
                            ),
                }),
        ('Samba and Azure related', {
            'classes': ('collapse',),
            'fields': (
                        ('sambaSID', 'sambaNTPassword'),
                        ),
                      }
        ),
        ('Password', {
            'classes': ('collapse',),
            'fields': (
                        # ('password_encoding', 'new_passwd'),
                        ('userPassword',),
                        ('new_passwd',),
                        ),
                      }
        ),
        ('Password Policy', {
            'classes': ('collapse',),
            'fields': (
                        (## 'pwdAccountLockedTime',
                         'locked_time',),
                        ('failure_times',),
                        ('pwdChangedTime',),
                        'pwdHistory_repr',
                        ),
                      }
        ),
        ('Additional info', {
            'classes': ('collapse',),
            'fields': (
                        ('createTimestamp', 'creatorsName',),
                        ('modifyTimestamp', 'modifiersName',),
                        ('get_membership_as_ul',
                        ## 'membership',
                        ),
                        ),
                      }
        ),
        ('Academia eduPerson', {
            ##'classes': ('collapse',),
            'fields': (
                        ('eduPersonPrincipalName', 'eduPersonOrcid',),
                        ('eduPersonAssurance',),
                        ('eduPersonAffiliation',
                        'eduPersonScopedAffiliation',),
                        'eduPersonEntitlement',
                        ),
                      }
        ),
        ('Academia Schac)', {
            ##'classes': ('collapse',),
            'fields': (
                        ('schacPlaceOfBirth', 'schacDateOfBirth'),
                        ('schacPersonalUniqueID', 'schacPersonalUniqueCode'),
                        ('schacExpiryDate'),
                       ('schacHomeOrganization',
                        'schacHomeOrganizationType'),
                        ),
                      }
        )
    )

    def pwdHistory_repr(self, obj):
        return mark_safe('<br>'.join(obj.pwdHistory))

    def get_emails_as_ul(self, obj):
        value = get_values_as_html_ul(obj.mail)
        return mark_safe(value)
    get_emails_as_ul.short_description = 'Email'

    def get_affiliation_as_ul(self, obj):
        value = get_values_as_html_ul(obj.eduPersonScopedAffiliation)
        return mark_safe(value)
    get_affiliation_as_ul.short_description = 'Affiliation'

    def get_membership_as_ul(self, obj):
        value = get_values_as_html_ul(obj.membership())
        return mark_safe(value)
    get_membership_as_ul.short_description = 'MemberOf'

    def get_status(self, obj):
        return obj.is_active()
    get_status.boolean = True
    get_status.short_description = _('Status')

    def save_model(self, request, obj, form, change):
        """
        method that trigger password encoding
        """
        if not form.data.get('eduPersonPrincipalName'):
            obj.set_default_eppn(force=True)
        else:
            obj.save()

        obj.update_eduPersonScopedAffiliation()

        if form.data.get('new_passwd'):
            passw = form.data.get('new_passwd')
            obj.set_password(passw)




@admin.register(LdapGroup)
class LdapGroupAdmin(LdapDbModelAdmin):
    form = LdapGroupAdminMultiValuedForm
