from django import forms
from django.core import validators
from django.utils.translation import ugettext_lazy as _


class ListField(forms.Field):
    def has_changed(self, initial, data):
        """Return True if data differs from initial."""
        # Always return False if the field is disabled since self.bound_data
        # always uses the initial value in this case.
        # print(sorted(initial), sorted(data))
        if self.disabled:
            return False
        try:
            data = self.to_python(data)
            if hasattr(self, '_coerce'):
                return self._coerce(data) != self._coerce(initial)
        except ValidationError:
            return True
        # For purposes of seeing whether something has changed, None is
        # the same as an empty string, if the data or initial value we get
        # is None, replace it with ''.
        initial_value = initial if initial is not None else ''
        data_value = data if data is not None else ''
        return sorted(initial_value) != sorted(data_value)


class EmailListField(ListField):
    pass
    #def validate_email_list(value):
        #print('EXEC')
        #if not isinstance(value, list):
            #raise ValidationError(
                #_('%(value)s is not a list'),
                #params={'value': value},
            #)
        #for item in value:
            #validation = validators.validate_email(item)
            #print(validation, item)
    
    # TODO
    #def validate(self, value):
        #"""Check if value consists only of valid emails."""
        #print(value)
        #super().validate(value)
        #for email in value:
            #validate_email(email)

    #default_validators = [validate_email_list]


class ScopedListField(ListField):
    pass

# TODO
# class TimeStampField(forms.SplitDateTimeField):
    # widget = DateTimeInput
    # input_formats = formats.get_format_lazy('DATETIME_INPUT_FORMATS')
    # default_error_messages = {
        # 'invalid': _('Enter a valid date/time.'),
    # }
    
    # def clean(self, value):
        # value = self.to_python(value)
        # self.validate(value)
        # self.run_validators(value)
        # print(self.__dict__, value)
        # return value
