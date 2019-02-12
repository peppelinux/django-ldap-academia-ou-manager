import chardet
import copy
import json
import time
import sys, io

import ldap_peoples.ldif as ldif

from datetime import datetime, timedelta
from django.apps import apps
from django.db import connections
from django.conf import settings
from django.utils import timezone
from ldap import modlist
from pprint import pprint


def parse_time(timestr, tformat):
    time_struct = time.strptime(timestr, tformat)
    timestamp = time.mktime(time_struct)
    value = timezone.datetime.fromtimestamp(timestamp)
    utc = timezone.make_aware(value, timezone.pytz.utc)
    return utc.astimezone(timezone.get_default_timezone())


def parse_generalized_time(timestr):
    return parse_time(timestr, settings.LDAP_DATETIME_FORMAT)


def parse_pwdfailure_time(timestr):
    return parse_time(timestr, settings.LDAP_DATETIME_MILLISECONDS_FORMAT)


def format_generalized_time(dt):
    """
    from datetime to zulu timestamp like 20180708095609Z
    """
    return dt.strftime(settings.LDAP_DATETIME_FORMAT)


def export_entries_to_ldif(entries_list):
    if isinstance(entry, list):
        pass


def export_entry_to_json(entry):
    """
    entry is a dict
    """
    out = io.StringIO()
    if isinstance(entry, dict):
        out.write(json.dumps(entry, indent=2))
    out.write('\n')
    out.seek(0)
    return out.read()


def export_entry_to_ldif(dn, entry):
    """
    raw example:
    from ldap_peoples.models import LdapAcademiaUser
    lu = LdapAcademiaUser.objects.filter(cn='peppe').first()

    import sys, ldap_peoples.ldif as ldif
    ldif_writer=ldif.LDIFWriter(sys.stdout)

    entry=lu.serialize(elements_as_list=1, encoding='utf-8')
    dn=entry['dn'][0]
    del entry['dn']
    ldif_writer.unparse(dn,entry)
    """
    out = io.StringIO()
    if isinstance(entry, dict):
        ldif_writer=ldif.LDIFWriter(out)
        ldif_writer.unparse(dn, entry)
    out.seek(0)
    return out.read()


def import_entries_from_ldif(fopen):
    # http://www.python-ldap.org/en/latest/reference/ldif.html#ldif.LDIFRecordList

    # Get a LDIFRecordList object of posix.ldif file
    ldif_rec = ldif.LDIFRecordList(fopen)
    # Read the LDIF file
    ldif_rec.parse()
    # print(fopen.read())

    # for item in ldif_rec.all_records:
        # pprint(item)

    # get the first LDAP router
    ldap_conn = connections['ldap']

    for dn, entry in ldif_rec.all_records:
        add_modlist = modlist.addModlist(entry)
        ldap_conn.add_s(dn, add_modlist)

    # returns False if everithing ok, otherwise return list of failed
    return []


def import_entries_from_json(fopen):
    content = fopen.read()
    encoding = chardet.detect(content)["encoding"]
    obj = json.loads(content.decode(encoding))

    model_name = obj['model']
    app_name = obj['app']
    app_model = apps.get_model(app_label=app_name, model_name=model_name)
    # ALTRA STRATEGIA: porta tutto come ldif?

    #print(json.dumps(obj, indent=2))
    for i in obj['entries']:
        entry = copy.copy(i)
        # try/catch here with messages!
        uid = entry['uid']
        del( entry['objectclass'] )
        fields = i.keys()
        lu = app_model.objects.filter(uid=uid).first()
        # if available 4 update
        if entry.get('schacDateOfBirth'):
            entry['schacDateOfBirth'] = timezone.datetime.strptime(entry['schacDateOfBirth'],
                                                                   settings.SCHAC_DATEOFBIRTH_FORMAT)
        if entry.get('schacExpiryDate'):
            entry['schacExpiryDate'] = parse_generalized_time(entry['schacExpiryDate']) #.encode(settings.DEFAULT_CHARSET)
        if lu:
            # update values
            for key in entry:
                if key in settings.READONLY_FIELDS: continue
                setattr(lu, key, entry[key])
            lu.save()
        else:
            lu = app_model.objects.create(**entry)

    # returns False if everithing ok, otherwise return list of failed
    return []


def get_expiration_date():
  return datetime.now() + timedelta(days=settings.SHAC_EXPIRY_DURATION_DAYS)
