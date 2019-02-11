import ast
import datetime
import os
import time

from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.conf import settings
from django.db.models import fields, lookups
from django.utils import timezone
from ldapdb.models.fields import (ExactLookup,
                                  GteLookup,
                                  ListContainsLookup,
                                  IContainsLookup,
                                  LteLookup,
                                  LdapLookup,
                                  LdapFieldMixin,
                                  TimestampField,
                                  CharField,
                                  DateTimeField)
from . form_fields  import (ListField as FormListField,
                            # TimeStampField as FormTimeStampField,
                            EmailListField as FormEmailListField,
                            ScopedListField as FormScopedListField)
from . widgets import (SplitJSONWidget,
                       SchacPersonalUniqueIdWidget,
                       SchacPersonalUniqueCodeWidget,
                       eduPersonAffiliationWidget,
                       eduPersonScopedAffiliationWidget,
                       SchacHomeOrganizationTypeWidget)


class TimeStampField(fields.DateTimeField):
    """
    Parse zulu timestamps from PPolicy fields
    """

    def __init__(self, *args, **kwargs):
        if 'format' in kwargs:
            self._date_format = kwargs.pop('format')
        else:
            self._date_format = settings.LDAP_DATETIME_FORMAT
        super(TimeStampField, self).__init__(*args, **kwargs)

    def from_ldap(self, value, connection):
        if not value:
            return None
        else:
            if b'.' in value[0]:
                time_struct = time.strptime(value[0].decode(connection.charset),
                                                            settings.LDAP_DATETIME_MILLISECONDS_FORMAT)
            else:
                time_struct = time.strptime(value[0].decode(connection.charset),
                                                            settings.LDAP_DATETIME_FORMAT)
            timestamp = time.mktime(time_struct)
            value = timezone.datetime.fromtimestamp(timestamp)
            if settings.USE_TZ:
                default_timezone = timezone.get_default_timezone()
                value = timezone.make_aware(value, timezone.pytz.utc)
                value = value.astimezone(default_timezone)
            return value

    def get_db_prep_save(self, value, connection):
        if not value:
            return None
        if type(value) == bytes:
            value = value.decode(connection.charset)
        if not isinstance(value, datetime.date) \
                and not isinstance(value, datetime.datetime):
                try:
                    return datetime.datetime.strptime(value,
                                                      self._date_format).date()
                except:
                    raise ValueError(
                        'DateField can be only set to a datetime.date instance')
        timestamps_value = value.strftime(self._date_format).encode(connection.charset)
        return [timestamps_value]


class ListField(LdapFieldMixin, fields.Field):
    binary_field = False
    multi_valued_field = True

    def from_ldap(self, value, connection):
        v = sorted([x.decode(connection.charset) for x in value])
        return v

    def formfield(self, **kwargs):
        defaults = {'form_class': FormListField,
                    'widget': SplitJSONWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


ListField.register_lookup(ListContainsLookup)
ListField.register_lookup(ExactLookup)
ListField.register_lookup(IContainsLookup)


class EmailListField(ListField):
    pass

    def formfield(self, **kwargs):
        defaults = {'form_class': FormEmailListField,
                    'widget': SplitJSONWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    ## 'validators': [FormEmailListField.validate_email_list],
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


EmailListField.register_lookup(ListContainsLookup)
EmailListField.register_lookup(ExactLookup)
EmailListField.register_lookup(IContainsLookup)


class ScopedListField(ListField):
    pass

    def formfield(self, **kwargs):
        defaults = {'form_class': FormScopedListField,
                    'widget': SplitJSONWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    ## 'validators': [FormEmailListField.validate_email_list],
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


ScopedListField.register_lookup(ListContainsLookup)
ScopedListField.register_lookup(ExactLookup)
ScopedListField.register_lookup(IContainsLookup)


class SchacPersonalUniqueIdListField(ListField):

    def formfield(self, **kwargs):
        defaults = {'form_class': FormListField,
                    'widget': SchacPersonalUniqueIdWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


SchacPersonalUniqueIdListField.register_lookup(ListContainsLookup)
SchacPersonalUniqueIdListField.register_lookup(ExactLookup)
SchacPersonalUniqueIdListField.register_lookup(IContainsLookup)


class SchacPersonalUniqueCodeListField(ListField):

    def formfield(self, **kwargs):
        defaults = {'form_class': FormListField,
                    'widget': SchacPersonalUniqueCodeWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


SchacPersonalUniqueCodeListField.register_lookup(ListContainsLookup)
SchacPersonalUniqueCodeListField.register_lookup(ExactLookup)
SchacPersonalUniqueCodeListField.register_lookup(IContainsLookup)


class SchacHomeOrganizationTypeListField(ListField):

    def formfield(self, **kwargs):
        defaults = {'form_class': FormListField,
                    'widget': SchacHomeOrganizationTypeWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


SchacHomeOrganizationTypeListField.register_lookup(ListContainsLookup)
SchacHomeOrganizationTypeListField.register_lookup(ExactLookup)
SchacHomeOrganizationTypeListField.register_lookup(IContainsLookup)


class eduPersonAffiliationListField(ListField):

    def formfield(self, **kwargs):
        defaults = {'form_class': FormListField,
                    'widget': eduPersonAffiliationWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


eduPersonAffiliationListField.register_lookup(ListContainsLookup)
eduPersonAffiliationListField.register_lookup(ExactLookup)
eduPersonAffiliationListField.register_lookup(IContainsLookup)


class eduPersonScopedAffiliationListField(ListField):

    def formfield(self, **kwargs):
        defaults = {'form_class': FormListField,
                    'widget': eduPersonScopedAffiliationWidget,
                    'help_text': self.help_text,
                    'label': self.verbose_name.title(),
                    }
        defaults.update(kwargs)
        return super().formfield(**defaults)


eduPersonScopedAffiliationListField.register_lookup(ListContainsLookup)
eduPersonScopedAffiliationListField.register_lookup(ExactLookup)
eduPersonScopedAffiliationListField.register_lookup(IContainsLookup)

class MultiValueField(LdapFieldMixin, fields.TextField):

    multi_valued_field = True

    def _cast(self, value, strip_value = ' '):
        if isinstance(value, str):
            return [i.strip(strip_value).encode(settings.FILE_CHARSET) for i in value.split(os.linesep)]
        #print('_cast', type(value), value)
        return [v.encode(settings.FILE_CHARSET) for v in value]

    def from_ldap(self, value, connection):
        a = [x.decode(connection.charset) for x in value]
        return os.linesep.join(a)

    def get_db_prep_save(self, value, connection):
        if not value:
            return None
        # print('get_db_prep_save', type(value))
        value = self._cast(value)
        return value

    def from_db_value(self, value, expression, connection, context):
        """Convert from the database format.

        This should be the inverse of self.get_prep_value()
        """
        # return self.to_python(value)
        return os.linesep.join(value)

    def to_python(self, value):
        # print('to_python', value)
        if not value:
            return []
        return self._cast(value)


MultiValueField.register_lookup(ListContainsLookup)
MultiValueField.register_lookup(IContainsLookup)


class AbstractTimeStampLookup(LdapLookup):

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        if isinstance(rhs_params[0], datetime.datetime):
            rhs_params = [rhs_params[0].strftime(settings.LDAP_DATETIME_FORMAT)]
        params = lhs_params + rhs_params
        return self._as_ldap(lhs, rhs), params

    def process_rhs(self, compiler, connection):
        for i in compiler.where.children:
            if isinstance(i.rhs, datetime.datetime):
                i.rhs = i.rhs.strftime(settings.LDAP_DATETIME_FORMAT)
            if isinstance(self.rhs, datetime.datetime):
                self.rhs = self.rhs.strftime(settings.LDAP_DATETIME_FORMAT)
        value = self.rhs
        if self.bilateral_transforms:
            if self.rhs_is_direct_value():
                # Do not call get_db_prep_lookup here as the value will be
                # transformed before being used for lookup
                value = Value(value, output_field=self.lhs.output_field)
            value = self.apply_bilateral_transforms(value)
            value = value.resolve_expression(compiler.query)
        if hasattr(value, 'as_sql'):
            sql, params = compiler.compile(value)
            return '(' + sql + ')', params
        else:
            return self.get_db_prep_lookup(value, connection)


class TimeStampFieldGteLookup(AbstractTimeStampLookup):
    lookup_name = 'gte'

    def _as_ldap(self, lhs, rhs):
        return '%s>=%s' % (lhs, rhs)


class TimeStampFieldGtLookup(AbstractTimeStampLookup):
    lookup_name = 'gt'

    def _as_ldap(self, lhs, rhs):
        return '%s>=%s' % (lhs, rhs)


class TimeStampFieldLteLookup(AbstractTimeStampLookup):
    lookup_name = 'lte'

    def _as_ldap(self, lhs, rhs):
        return '%s<=%s' % (lhs, rhs)


class TimeStampFieldLtLookup(AbstractTimeStampLookup):
    lookup_name = 'lt'

    def _as_ldap(self, lhs, rhs):
        return '%s<=%s' % (lhs, rhs)


TimeStampField.register_lookup(ExactLookup)
TimeStampField.register_lookup(TimeStampFieldGteLookup)
TimeStampField.register_lookup(TimeStampFieldGtLookup)
TimeStampField.register_lookup(TimeStampFieldLteLookup)
TimeStampField.register_lookup(TimeStampFieldLtLookup)
