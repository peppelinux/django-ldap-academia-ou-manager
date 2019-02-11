import json

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
# from django.core import serializers
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import *


def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/force-download")
    fname = 'ldapuser_export_{}.json'.format(timezone.localtime().isoformat())
    response['Content-Disposition'] = 'attachment; filename={}'.format(fname)
    # serializers.serialize("json", queryset, stream=response, indent=2)
    app_name = queryset.model._meta.app_label
    model_name = queryset.model.__name__
    d = {'app': app_name, 'model': model_name, 'entries': []}
    for i in queryset:
        d['entries'].append(i.serialize())
    response.content = json.dumps(d, indent=2)
    return response
export_as_json.short_description = _("Export as JSON")


def export_as_ldif(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/ldif")
    attach_str = 'attachment; filename="ldapuser_export_{}.ldif"'
    t = timezone.localtime().isoformat()
    if settings.USE_TZ:
        response['Content-Disposition'] = attach_str.format(t)
    else:
        response['Content-Disposition'] = attach_str.format(t)
    for i in queryset:
        response.content += i.ldiff().encode(settings.FILE_CHARSET)
    return response
export_as_ldif.short_description = _("Export as LDIF")


def send_reset_token_email(modeladmin, request, queryset):
    num_sync = 0
    for i in queryset:
        num_sync += 1
        msg = _('{}, email sent').format(i.__str__())
        ch_msg = _('Password reset token sent {}').format(i.__str__())
        messages.add_message(request, messages.INFO, msg)
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(i).pk,
            object_id       = i.pk,
            object_repr     = i.__str__(),
            action_flag     = ADDITION,
            change_message  = ch_msg)
    if num_sync:
        messages.add_message(request, messages.INFO, _('{} Token sent via E-Mail').format(num_sync))
send_reset_token_email.short_description = _("Send reset Password Token via E-Mail")


def lock_account(modeladmin, request, queryset):
    num_sync = 0
    for i in queryset:
        num_sync += 1
        i.lock()
        messages.add_message(request, messages.WARNING, _('{}, disabled').format(i.__str__()))
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(i).pk,
            object_id       = i.pk,
            object_repr     = i.__str__(),
            action_flag     = CHANGE,
            change_message  = _('Locked User (pwdAccountLockedTime)')
            )
    if num_sync:
        messages.add_message(request, messages.INFO, _('{} Accounts disabled').format(num_sync))
lock_account.short_description = _("Lock Account with pwdAccountLockedTime: {}").format(settings.PPOLICY_PERMANENT_LOCKED_TIME)


def disable_account(modeladmin, request, queryset):
    num_sync = 0
    for i in queryset:
        num_sync += 1
        i.disable()
        messages.add_message(request, messages.WARNING, _('{}, disabled').format(i.__str__()))
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(i).pk,
            object_id       = i.pk,
            object_repr     = i.__str__(),
            action_flag     = CHANGE,
            change_message  = _('Disabled User (pwdAccountLockedTime)')
            )
    if num_sync:
        messages.add_message(request, messages.INFO, _('{} Accounts disabled').format(num_sync))
disable_account.short_description = _("Disable Account (expire password)")



def enable_account(modeladmin, request, queryset):
    num_sync = 0
    for i in queryset:
        num_sync += 1
        i.enable()
        messages.add_message(request, messages.INFO, _('{}, enabled').format(i.__str__()))
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(i).pk,
            object_id       = i.pk,
            object_repr     = i.__str__(),
            action_flag     = CHANGE,
            change_message  = _('Enabled User (pwdAccountLockedTime)')
            )
    if num_sync:
        messages.add_message(request, messages.INFO, _('{} Accounts enabled').format(num_sync))
enable_account.short_description = _("Enable Account - Clean pwdAccountLockedTime")
