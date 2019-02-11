from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from unical_template.admin import ReadOnlyAdmin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from .admin_actions import *
from .admin_utils import (get_values_as_html_ul,)
from .forms import LdapAcademiaUserAdminForm, LdapGroupAdminMultiValuedForm #, FileImportActionForm
from .hash_functions import encode_secret
from .models import *


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
    list_filter = (
                   # 'pwdChangedTime', 'created', 'modified',
                   ('createTimestamp', DateRangeFilter),
                   ('modifyTimestamp', DateTimeRangeFilter),
                   ('pwdChangedTime', DateTimeRangeFilter),

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

                       'userPassword',
                       'sambaNTPassword',
                       )
    actions = [send_reset_token_email,
               enable_account,
               disable_account,
               lock_account,
               export_as_json,
               export_as_ldif]

    # action_form = FileImportActionForm

    # TODO: aggregate lookup for evaluating min max on records
    #date_hierarchy = 'created'

    fieldsets = (
        (None, { 'fields' : (('uid',
                              'distinguished_name'
                              ),
                             ('cn','sn',),
                            ('givenName', 'displayName', ),
                            ('mail', 'telephoneNumber'),
                            ),
                }),
        ('Password', {
            'classes': ('collapse',),
            'fields': (
                        # ('password_encoding', 'new_passwd'),
                        ('userPassword', 'sambaNTPassword'),
                        ('new_passwd',),
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
        ('Password Policy', {
            'classes': ('collapse',),
            'fields': (
                        (## 'pwdAccountLockedTime',
                         'locked_time',
                        ),
                        ('failure_times',),
                        (
                        ## 'pwd_changed',
                        'pwdChangedTime',
                        )
                        ),
                      }
        ),
        ('Academia eduPerson', {
            ##'classes': ('collapse',),
            'fields': (
                        ('eduPersonPrincipalName', 'eduPersonOrcid',),
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
        obj.save()
        if form.data.get('new_passwd'):
            passw = form.data.get('new_passwd')
            obj.set_password(passw)


@admin.register(LdapGroup)
class LdapGroupAdmin(LdapDbModelAdmin):
    form = LdapGroupAdminMultiValuedForm
