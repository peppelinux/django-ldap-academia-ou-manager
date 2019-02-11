from django.conf import settings
from collections import OrderedDict

from . ldap_utils import (format_generalized_time,
                          export_entry_to_ldiff,
                          export_entry_to_json)

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
            if ele.attname in settings.READONLY_FIELDS: continue
            value = getattr(self, ele.attname)
            if not value: continue

            # TODO better code here!
            if isinstance(value, list):
                if encoding:
                    d[ele.attname] = [i.encode(encoding) for i in value]
                else:
                    d[ele.attname] = [i for i in value]
            elif ele.attname in ('schacExpiryDate',):
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

    def ldiff(self):
        d = self.serialize(elements_as_list = True, encoding=settings.FILE_CHARSET)
        del d['dn']
        return export_entry_to_ldiff(self.dn, d)

    def json(self):
        return export_entry_to_json(self.serialize())
