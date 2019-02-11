import ldap
import ldapdb.models
import os

from collections import OrderedDict
from django.conf import settings
from django.db import connections
from django.db.models import fields
from django.utils import timezone

from django.db import models
from django.utils.translation import gettext as _
from ldapdb.models.fields import (CharField,
                                  DateField,
                                  DateTimeField,
                                  TimestampField,
                                  ImageField,
                                  IntegerField)
from .hash_functions import encode_secret
from . ldap_utils import (parse_generalized_time,
                          parse_pwdfailure_time,
                          export_entry_to_ldiff,
                          export_entry_to_json,
                          format_generalized_time,
                          get_expiration_date)
from . model_fields import (TimeStampField,
                            MultiValueField,
                            ListField,
                            EmailListField,
                            SchacPersonalUniqueIdListField,
                            SchacPersonalUniqueCodeListField,
                            ScopedListField,
                            eduPersonAffiliationListField,
                            eduPersonScopedAffiliationListField,
                            SchacHomeOrganizationTypeListField)


class LdapGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.
    This is a memberOf bind
    http://www.openldap.org/software/man.cgi?query=slapo-memberof&sektion=5&apropos=0&manpath=OpenLDAP+2.4-Release
    """
    # LDAP meta-data
    base_dn = "ou=groups,{}".format(settings.LDAP_BASEDN)
    object_classes = [
                      # 'posixGroup',
                      'groupOfNames']

    # posixGroup attributes for future forks
    # gid = IntegerField(db_column='gidNumber', unique=True)
    # name = CharField(db_column='cn', max_length=200, primary_key=True)
    # usernames = MultiValueField(db_column='memberUid')

    cn = CharField(db_column='cn',
                   primary_key=True)
    member = ListField(db_column='member', default=[])


    class Meta:
        verbose_name = _('LDAP MemberOf Group')
        verbose_name_plural = _('LDAP MemberOf Groups')

    def add_member(self, member_dn_obj):
        members = self.member.split(os.linesep)
        if not member_dn_obj in members:
            members.append(member_dn_obj.dn.strip())
        self.member = os.linesep.join(members)
        self.save()

    def remove_member(self, member_dn_obj):
        members = self.member.split(os.linesep)
        if member_dn_obj.dn in members:
            members = [i for i in members if i != member_dn_obj.dn ]
        self.member = os.linesep.join(members)
        self.save()

    def __str__(self):
        return self.cn


class LdapAcademiaUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = "ou={},{}".format(settings.LDAP_OU,
                                settings.LDAP_BASEDN)

    object_classes = ['inetOrgPerson',
                      'organizationalPerson',
                      'person',
                      # WARNING: only who have these OC will be filtered
                      'userSecurityInformation',
                      'eduPerson',
                      'radiusprofile',
                      'sambaSamAccount',
                      'schacContactLocation',
                      'schacEmployeeInfo',
                      'schacEntryConfidentiality',
                      'schacEntryMetadata',
                      'schacExperimentalOC',
                      'schacGroupMembership',
                      'schacLinkageIdentifiers',
                      'schacPersonalCharacteristics',
                      'schacUserEntitlements']

    # inetOrgPerson
    uid = CharField(db_column='uid',
                    verbose_name="User ID",
                    help_text="uid",
                    primary_key=True)
    cn = CharField(db_column='cn',
                     verbose_name=_("Name"),
                     help_text='cn',
                     blank=False)
    givenName = CharField(db_column='givenName',
                          help_text="givenName",
                          verbose_name=_("First Name"),
                          blank=True, null=True)
    sn = CharField("Final name", db_column='sn',
                   help_text='sn',
                   blank=False)
    displayName = CharField(db_column='displayName',
                            help_text='displayName',
                            blank=True, null=True)
    telephoneNumber = ListField(db_column='telephoneNumber',
                                blank=True)
    mail = EmailListField(db_column='mail',
                          default='',
                          blank=True, null=True)
    userPassword = CharField(db_column='userPassword',
                             verbose_name="LDAP Password",
                             blank=True, null=True,
                             editable=False)
    sambaNTPassword = CharField(db_column='sambaNTPassword',
                                help_text=_("SAMBA NT Password (freeRadius PEAP)"),
                                blank=True, null=True, editable=False)
    # academia
    eduPersonPrincipalName = CharField(db_column='eduPersonPrincipalName',
                                       help_text=_("A scoped identifier for a person"),
                                       verbose_name='ePPN, Eduperson PrincipalName',
                                       blank=True, null=True)
    eduPersonAffiliation = eduPersonAffiliationListField(db_column='eduPersonAffiliation',
                                     help_text=_("Membership and "
                                                 "affiliation organization"),
                                     verbose_name='Eduperson Affiliation',
                                     blank=True, null=True)
    eduPersonScopedAffiliation = eduPersonScopedAffiliationListField(db_column='eduPersonScopedAffiliation',
                                                 help_text=_("Membership and scoped"
                                                             "affiliation organization."
                                                             "Es: affliation@istitution"),
                                                 verbose_name='ScopedAffiliation',
                                                 blank=True, null=True)
    eduPersonEntitlement = ListField(db_column='eduPersonEntitlement',
                                     help_text=("eduPersonEntitlement"),
                                     verbose_name='eduPersonEntitlement',
                                     default=settings.DEFAULT_EDUPERSON_ENTITLEMENT,
                                     blank=True, null=True)
    eduPersonOrcid = CharField(db_column='eduPersonOrcid',
                               verbose_name='EduPerson Orcid',
                               help_text=_("ORCID user identifier released and managed by orcid.org"),
                               blank=True, null=True)
    schacHomeOrganization = CharField(db_column='schacHomeOrganization',
                                      help_text=_(("The persons home organization "
                                                   "using the domain of the organization.")),
                                      default=settings.SCHAC_HOMEORGANIZATION_DEFAULT,
                                      verbose_name='schacHomeOrganization',
                                      blank=True, null=True)
    schacHomeOrganizationType = SchacHomeOrganizationTypeListField(db_column='schacHomeOrganizationType',
                                             help_text=_("Type of a Home Organization"),
                                             blank=True, null=True)
    schacPersonalUniqueID = SchacPersonalUniqueIdListField(db_column='schacPersonalUniqueID',
                                      verbose_name="schacPersonalUniqueID",
                                      help_text=_(("Unique Legal Identifier of "
                                                   "a person, es: codice fiscale")),
                                      blank=True, null=True, )
    schacPersonalUniqueCode = SchacPersonalUniqueCodeListField(db_column='schacPersonalUniqueCode',
                                  verbose_name="schacPersonalUniqueCode",
                                  help_text=_(('Specifies a "unique code" '
                                               'for the subject it is associated with')),
                                  blank=True, null=True)
    schacDateOfBirth = DateField(db_column='schacDateOfBirth',
                                 format="%Y%m%d", # from_ldap format
                                 help_text=_("OID 1.3.6.1.4.1.1466.115.121.1.36"),
                                 verbose_name='schacDateOfBirth',
                                 blank=True, null=True)
    schacPlaceOfBirth = CharField(db_column='schacPlaceOfBirth',
                                  help_text=_("OID: 1.3.6.1.4.1.1466.115.121.1.15"),
                                  verbose_name='schacPlaceOfBirth',
                                  blank=True, null=True)
    schacExpiryDate = TimeStampField(db_column='schacExpiryDate',
                                     help_text=_(('Date from which the set of '
                                                  'data is to be considered invalid')),
                                     default=get_expiration_date,
                                     blank=False, null=True)
    # readonly
    memberOf = MultiValueField(db_column='memberOf', editable=False, null=True)
    createTimestamp =  DateTimeField(db_column='createTimestamp', editable=False, null=True)
    modifyTimestamp =  DateTimeField(db_column='modifyTimestamp', editable=False, null=True)
    creatorsName = CharField(db_column='creatorsName', editable=False, null=True)
    modifiersName = CharField(db_column='modifiersName', editable=False, null=True)

    # If pwdAccountLockedTime is set to 000001010000Z, the user's account has been permanently locked and may only be unlocked by an administrator.
    # Note that account locking only takes effect when the pwdLockout password policy attribute is set to "TRUE".
    pwdAccountLockedTime = CharField(db_column='pwdAccountLockedTime')
    pwdFailureTime = MultiValueField(db_column='pwdFailureTime', editable=False)
    pwdChangedTime = TimeStampField(db_column='pwdChangedTime', editable=False)


    class Meta:
        verbose_name = _('LDAP Academia User')
        verbose_name_plural = _('LDAP Academia Users')

    def distinguished_name(self):
        return 'uid={},{}'.format(self.uid, self.base_dn)

    def pwd_changed(self):
        if self.pwdChangedTime:
            return parse_generalized_time(self.pwdChangedTime)

    def is_active(self):
        if self.pwdAccountLockedTime: return False
        if self.schacExpiryDate:
            if self.schacExpiryDate < timezone.localtime(): return False
        return True

    def is_renewable(self):
        return self.pwdAccountLockedTime != settings.PPOLICY_PERMANENT_LOCKED_TIME

    def lock(self):
        self.pwdAccountLockedTime = settings.PPOLICY_PERMANENT_LOCKED_TIME
        self.save()
        return self.pwdAccountLockedTime

    def disable(self):
        self.pwdAccountLockedTime = format_generalized_time(timezone.localtime())
        self.save()
        return self.pwdAccountLockedTime

    def enable(self):
        self.pwdAccountLockedTime = None
        self.save()

    def locked_time(self):
        if self.pwdAccountLockedTime == settings.PPOLICY_PERMANENT_LOCKED_TIME:
            return '{}: locked by admin'.format(settings.PPOLICY_PERMANENT_LOCKED_TIME)
        elif self.pwdAccountLockedTime:
            return parse_generalized_time(self.pwdAccountLockedTime)

    def failure_times(self):
        if not self.pwdFailureTime: return
        times = self.pwdFailureTime.split(os.linesep)
        failures = [parse_pwdfailure_time(i).strftime(settings.DATETIME_FORMAT) for i in times]
        parsed =  os.linesep.join(failures)
        return parsed

    def get_schacPersonalUniqueID_prefix(self):
        if settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX not in self.schacPersonalUniqueID:
            self.schacPersonalUniqueID = '{}{}'.format(settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX,
                                                       self.schacPersonalUniqueID)
        return self.schacPersonalUniqueID

    def set_schacPersonalUniqueID(self, value,
                                  doc_type=settings.SCHAC_PERSONALUNIQUEID_DEFAULT_DOCUMENT_CODE,
                                  country_code=settings.SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE):

        if settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX not in value:
            unique_id = ':'.join((settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX,
                                  country_code,
                                  doc_type, value))
        if self.schacPersonalUniqueID:
            if unique_id not in self.schacPersonalUniqueID:
                self.schacPersonalUniqueID.append(unique_id)
        else:
            self.schacPersonalUniqueID = [unique_id]
        self.save()

    def set_schacHomeOrganizationType(self, value,
                                      country_code=settings.SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE):

        if settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX not in value:
            unique_id = ':'.join((settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX,
                                  country_code,
                                  value))
        if self.schacHomeOrganizationType:
            if unique_id not in self.schacHomeOrganizationType:
                self.schacHomeOrganizationType.append(unique_id)
        else:
            self.schacHomeOrganizationType = [unique_id]
        self.save()

    def set_default_eppn(self, force=False):
        if self.eduPersonPrincipalName and not force:
            return self.eduPersonPrincipalName
        self.eduPersonPrincipalName = '@'.join((self.uid, settings.LDAP_BASE_DOMAIN))
        self.save()
        return self.eduPersonPrincipalName

    def membership(self):
        if self.memberOf: return self.memberOf
        # memberOf fill fields in people entries only if a change/write happens in its definitions
        membership = LdapGroup.objects.filter(member__contains=self.dn)
        if membership:
            # return os.linesep.join([m.dn for m in membership])
            return [i.cn for i in membership]

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

    def set_password(self, password, old_password=None):
        ldap_conn = connections['ldap']
        ldap_conn.connect()
        ldap_conn.connection.passwd_s(user = self.dn,
                                      oldpw = old_password,
                                      newpw = password.encode(settings.FILE_CHARSET))
        ldap_conn.connection.unbind_s()
        return True

    def set_password_custom(self, password, hashtype=settings.DEFAULT_SECRET_TYPE):
        """
        EXPERIMENTAL - do not use in production
        encode the password, this could not works on some LDAP servers
        """
        # password encoding
        if password:
            self.userPassword = encode_secret(hashtype, password)
        # additional password fields encoding
        enc_map = settings.PASSWD_FIELDS_MAP
        for field in enc_map:
            if not hasattr(self, field):
                continue
            enc_value = encode_secret(enc_map[field], password)
            setattr(self, field, enc_value)
        self.save()
        return self.userPassword

    def reset_schacExpiryDate(self):
        self.schaExpiryDate = timezone.localtime()+\
                              timezone.timedelta(days=settings.SHAC_EXPIRY_DURATION_DAYS)
        self.save()
        return self.schaExpiryDate

    def save(self, *args, **kwargs):
        for field in settings.READONLY_FIELDS:
            if hasattr(self, field):
                try:
                    del self.__dict__[field]
                except:
                    print('error on deletion {} readonly field'.format(field))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.dn
