import chardet
import copy
import io
import json
import ldap_peoples.ldif as ldif

from django.apps import apps
from django.conf import settings
from django.db import connections
from django.utils import timezone
from collections import OrderedDict
from ldap import modlist

from . ldap_utils import (format_generalized_time,
                          parse_generalized_time)


class LdapImportExport(object):
    @staticmethod
    def clean_entry_dict(d):
        entry = {}
        for k,v in d.items():
            if k not in settings.READONLY_FIELDS:
                entry[k] = v
        return entry

    @staticmethod
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
        else:
            raise Exception('dict required')

    @staticmethod
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
            entry = LdapImportExport.clean_entry_dict(entry)
            ldif_writer=ldif.LDIFWriter(out)
            ldif_writer.unparse(dn, entry)
            out.seek(0)
            return out.read()
        else:
            raise Exception('dict required')

    @staticmethod
    def import_entries_from_ldif(fopen):
        # http://www.python-ldap.org/en/latest/reference/ldif.html#ldif.LDIFRecordList
        # Get a LDIFRecordList object of posix.ldif file
        ldif_rec = ldif.LDIFRecordList(fopen)
        # Read the LDIF file
        ldif_rec.parse()
        # get the first LDAP router
        ldap_conn = connections['ldap']
        for dn, entry in ldif_rec.all_records:
            add_modlist = modlist.addModlist(entry)
            ldap_conn.add_s(dn, add_modlist)
        return True

    @staticmethod
    def import_entries_from_json(fopen):
        content = fopen.read()
        if isinstance(content, bytes):
            encoding = chardet.detect(content)["encoding"]
            obj = json.loads(content.decode(encoding))
        else:
            obj = json.loads(content)

        model_name = obj['model']
        app_name = obj['app']
        app_model = apps.get_model(app_label=app_name,
                                   model_name=model_name)
        for i in obj['entries']:
            entry = LdapImportExport.clean_entry_dict(i)
            del(entry['objectclass'])
            # try/catch here with messages!
            uid = entry['uid']
            fields = i.keys()
            lu = app_model.objects.filter(uid=uid).first()
            # if available 4 update
            if entry.get('schacDateOfBirth'):
                entry['schacDateOfBirth'] = timezone.datetime.strptime(entry['schacDateOfBirth'],
                                                                       settings.SCHAC_DATEOFBIRTH_FORMAT)
            if entry.get('schacExpiryDate'):
                entry['schacExpiryDate'] = parse_generalized_time(entry['schacExpiryDate'])
            if lu:
                # update values
                for k,v in entry.items():
                    setattr(lu, k, v)
                lu.save()
            else:
                lu = app_model.objects.create(**entry)
        return True


class LdapSerializer(object):
    def serialize(self, elements_as_list = False, encoding=None):
        d = OrderedDict()
        if self.object_classes:
            d['objectclass'] = []
            for i in self.object_classes:
                if encoding:
                    d['objectclass'].append(i.encode(encoding))
                else:
                    d['objectclass'].append(i)
        for ele in self._meta.get_fields():
            #if ele in settings.READONLY_FIELDS: continue
            value = getattr(self, ele.attname)
            if not value: continue

            # TODO better code here!
            if isinstance(value, list):
                if encoding:
                    d[ele.attname] = [i.encode(encoding) for i in value]
                else:
                    d[ele.attname] = [i for i in value]
            elif ele.attname in ('schacExpiryDate', 'pwdChangedTime',
                                 'createTimestamp', 'modifyTimestamp'):
                d[ele.attname] = format_generalized_time(value)
                if encoding:
                    d[ele.attname] = d[ele.attname].encode(encoding)
            elif ele.attname in ('schacDateOfBirth',):
                d[ele.attname] = value.strftime(settings.SCHAC_DATEOFBIRTH_FORMAT)
                if encoding:
                    d[ele.attname] = d[ele.attname].encode(encoding)
            else:
                if encoding:
                    d[ele.attname] = ele.value_to_string(self).encode(encoding)
                else:
                    d[ele.attname] = ele.value_to_string(self)

            if elements_as_list and not isinstance(value, list):
                d[ele.attname] = [d[ele.attname]]
        return d

    def ldif(self):
        d = self.serialize(elements_as_list = True,
                           encoding=settings.FILE_CHARSET)
        del d['dn']
        return LdapImportExport.export_entry_to_ldif(self.dn, d)

    def json(self):
        return LdapImportExport.export_entry_to_json(self.serialize())

    def json_ext(self):
        """
        add app and model definition to a single json entry
        """
        d = {'app': self._meta.app_label,
             'model': self._meta.model_name,
             'entries': [self.serialize()]}
        return json.dumps(d)
