import re
import datetime

from copy import copy
from django import forms
from django.conf import settings
from django.contrib.admin.helpers import ActionForm
from django.core import validators
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from . form_fields import ListField, EmailListField, ScopedListField
from . models import LdapAcademiaUser
from . widgets import (SplitJSONWidget,
                       SchacPersonalUniqueIdWidget,
                       SchacPersonalUniqueCodeWidget,
                       eduPersonAffiliationWidget,
                       eduPersonScopedAffiliationWidget,
                       SchacHomeOrganizationTypeWidget)
from pprint import pprint

#from django.utils.dateparse import (
    #parse_date, parse_datetime, parse_duration, parse_time,
#)

class LdapMultiValuedForm(forms.ModelForm):
    
    def clean_schacExpiryDate(self):
        """
        This kind of field need a better generalization
        
        The clean_<field> hooks in the forms API are for doing additional validation. 
        It is called after the field calls its clean method. 
        If the field does not consider the input valid then the clean_<field> is not called. 
        This is noted in the custom validation docs:
        https://docs.djangoproject.com/en/2.1/ref/forms/validation/ 
        """
        datestr = ' '.join((self.data['schacExpiryDate_0'], self.data['schacExpiryDate_1']))
        value = None
        for date_format in settings.DATETIME_INPUT_FORMATS:
            try:
                value = datetime.datetime.strptime(datestr, date_format)
            except Exception as e:
                print(e)
                pass
        if not value: return
        value = timezone.make_aware(value, timezone.pytz.utc)
        self.cleaned_data['schacExpiryDate'] = value
        return self.cleaned_data['schacExpiryDate']

    def clean_MultiValueWidget(self, field, data, 
                               default_prefix, count,
                               sep=':'):
        # print(field)
        regexp = '{}_(?P<order>\d+)_\[(?P<key>\d+)\]'.format(field)
        value_list = []
        field_dict = {}
        for key in data:
            reg_test = re.match(regexp, key)
            if reg_test:
                order_id = int(reg_test.groupdict()['order'])
                key_id = int(reg_test.groupdict()['key'])
                if not isinstance(field_dict.get(key_id), dict):
                    field_dict[key_id] = {}
                field_dict[key_id][order_id] = self.data[key]
        for row_dict in field_dict.values():
            field_group = [default_prefix,] if default_prefix else []
            cnt = 0
            for item in sorted(row_dict.keys()):
                if not row_dict[item]: continue
                cnt += 1
                if cnt < count:
                    field_group.append(row_dict[item])
                    continue
    
                field_group.append(row_dict[item])
                new_value = sep.join(field_group)
                value_list.append(new_value)
                cnt = 0
                field_group = [default_prefix,] if default_prefix else []
                field_group.append(row_dict[item])
                # print(field_dict[item], cnt, field_group, value_list)
        return value_list

    def clean_eduPersonAffiliation_custom(self, field, data):
        # print(field, data)
        regexp = '{}_(?P<order>\d+)_\[(?P<key>\d+)\]'.format(field)
        value_list = []
        field_dict = {}
        for key in data:
            reg_test = re.match(regexp, key)
            # print(reg_test, key)
            if reg_test:
                order_id = int(reg_test.groupdict()['order'])
                key_id = int(reg_test.groupdict()['key'])
                if not isinstance(field_dict.get(key_id), dict):
                    field_dict[key_id] = {}
                field_dict[key_id][order_id] = self.data[key]
        # print(field_dict)
        for row_dict in field_dict.values():
            field_group = []
            cnt = 0
            for item in sorted(row_dict.keys()):
                if not row_dict[item]: continue
                cnt += 1
                # print(row_dict)
                # print(row_dict[item], cnt, field_group)
                if cnt < 1:
                    field_group.append(row_dict[item])
                    continue
    
                field_group.append(row_dict[item])
                new_value = ''.join(field_group)
                value_list.append(new_value)
                cnt = 0
                field_group = []
                field_group.append(row_dict[item])
                # print(field_dict[item], cnt, field_group, value_list)
        return value_list

    def clean_ListField(self, field, data):
        # TODO run regexp validator here or add validators=[] in model field
        regexp = '{}\[\d+\]'.format(field)
        value_list = []
        for key in data:
            if re.match(regexp, key):
                value_list.append(self.data[key])
                if isinstance(self.fields[field], EmailListField):
                    try:
                        validators.validate_email(self.data[key])
                    except:
                        # TODO: sarebbe meglio fare to_python eppoi...
                        # print("Manage exception here: {} {}".format(field, self.data[key]))
                        msg = _('{} is not a valid email format!')
                        self.add_error(field,  msg.format(self.data[key]))
                elif isinstance(self.fields[field], ScopedListField):
                    if not re.match('[a-zA-Z]+@[a-zA-Z]+', self.data[key]):
                        msg = _('{} is not valid: please use "value@scope"')
                        self.add_error(field,  msg.format(self.data[key]))
        return value_list

    def clean(self):
        """
        Auto Detect for any ListField widget
        """
        #super().clean()
        # pprint(self.__dict__)
        data = copy(self.data)
        for field in self.fields:
            if isinstance(self.fields[field].widget, SchacPersonalUniqueCodeWidget):
                data[field] = self.clean_MultiValueWidget(field, data,
                                                          settings.SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX,
                                                          2)
            elif isinstance(self.fields[field].widget, SchacHomeOrganizationTypeWidget):
                data[field] = self.clean_MultiValueWidget(field, data,
                                                          settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX,
                                                          2)
            elif isinstance(self.fields[field].widget, eduPersonScopedAffiliationWidget):
                data[field] = self.clean_MultiValueWidget(field, data,
                                                          None, 2, sep='')
            elif isinstance(self.fields[field].widget, eduPersonAffiliationWidget):
                data[field] = self.clean_MultiValueWidget(field, data,
                                                          None, 1)
            elif isinstance(self.fields[field].widget, SchacPersonalUniqueIdWidget):
                data[field] = self.clean_MultiValueWidget(field, data,
                                                          settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX,
                                                          3)
                # clean error manually
                if self._errors.get(field):
                    del(self._errors[field])
            elif isinstance(self.fields[field].widget, SplitJSONWidget):
                data[field] = self.clean_ListField(field, data)
            elif field == 'schacDateOfBirth':
                # per generalizzare questo agire nel metodo to_python del field
                if not data[field]:
                    data[field] = None
                    continue
                for date_format in settings.DATE_INPUT_FORMATS:
                    date_in = None
                    try:
                        date_in = datetime.datetime.strptime(data[field], date_format)
                    except Exception as e: 
                        # print(date_format, e)
                        pass
                    if date_in:
                        data[field] = date_in
                        break
                    # print(data[field])
            
            elif field == 'schacExpiryDate':
                data[field] = self.clean_schacExpiryDate()
            elif field == 'eduPersonPrincipalName':
                if not re.match(settings.EEPN_VALIDATOR, data[field]):
                    msg = _('{} is not valid: please use "value@scope"')
                    self.add_error(field,  msg.format(data[field]))

        self.data = data
        return data

    @cached_property
    def changed_data(self):
        data = []
        for name, field in self.fields.items():
            prefixed_name = self.add_prefix(name)
            data_value = field.widget.value_from_datadict(self.data, self.files, prefixed_name)
            if not field.show_hidden_initial:
                # Use the BoundField's initial as this is the value passed to
                # the widget.
                initial_value = self[name].initial
            else:
                initial_prefixed_name = self.add_initial_prefix(name)
                hidden_widget = field.hidden_widget()
                try:
                    initial_value = field.to_python(hidden_widget.value_from_datadict(
                                                    self.data, self.files, initial_prefixed_name))
                except ValidationError:
                    # Always assume data has changed if validation fails.
                    data.append(name)
                    continue
            if field.has_changed(initial_value, data_value):
                data.append(name)
        return data


class LdapUserAdminPasswordBaseForm(forms.Form):
    _min_len_help_text = 'The secret must at least {} digits, '.format(settings.PPOLICY_PASSWD_MIN_LEN)
    _extended_help_text = ('contains lowercase'
                           ' and uppercase characters, '
                           ' number and at least one of these symbols:'
                           '! % - _ + = [ ] { } : , . ? < > ( ) ; ')
    _secret_help_text = _min_len_help_text + _extended_help_text

    # custom field not backed by database
    new_passwd = forms.CharField(label=_('New password'),
                                required=False,
                                min_length=settings.PPOLICY_PASSWD_MIN_LEN,
                                max_length=settings.PPOLICY_PASSWD_MAX_LEN,
                                widget=forms.PasswordInput(),
                                help_text=_secret_help_text)

    def clean_new_passwd(self):
        if not self.data['new_passwd']:
            return None
        for regexp in settings.SECRET_FIELD_VALIDATORS.values():
            found = re.findall(regexp, self.data['new_passwd'])
            if not found:
                raise ValidationError(self._secret_help_text)
        return self.cleaned_data['new_passwd']


class LdapUserAdminPasswordForm(LdapUserAdminPasswordBaseForm):
    password_encoding = forms.ChoiceField(choices=[(i,i) for i in settings.SECRET_PASSWD_TYPE\
                                                   if i not in settings.DISABLED_SECRET_TYPES],
                                          required=False,
                                          initial=settings.DEFAULT_SECRET_TYPE)

    def clean_attribute(self):
        if self.data['attribute'] not in settings.DISABLED_SECRET_TYPES:
            return self.cleaned_data['attribute']


class LdapAcademiaUserAdminForm(LdapMultiValuedForm, LdapUserAdminPasswordBaseForm):
    # define your customization here
    # schacPersonalUniqueID = forms.CharField(required=False, widget=SchacPersonalUniqueIdWidget)
    pass


class LdapGroupAdminMultiValuedForm(LdapMultiValuedForm):
    # define your customization here
    pass
