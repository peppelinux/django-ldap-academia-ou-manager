import os

from django.conf import settings

LDAP_DATETIME_FORMAT = '%Y%m%d%H%M%SZ'
LDAP_DATETIME_MILLISECONDS_FORMAT = '%Y%m%d%H%M%S.%fZ'
DEFAULT_EDUPERSON_ENTITLEMENT = ['urn:mace:terena.org:tcs:personal-user',
                                 'urn:mace:terena.org:tcs:escience-user']

# If pwdAccountLockedTime is set to 000001010000Z, the user's account
# has been permanently locked and may only be unlocked by an administrator.
PPOLICY_PERMANENT_LOCKED_TIME = '000001010000Z'
PPOLICY_PASSWD_MIN_LEN = 8
PPOLICY_PASSWD_MAX_LEN = 32

LDAP_PASSWORD_SALT_SIZE = 8
# an account must be renewed every 6 months
SHAC_EXPIRY_DURATION_DAYS = 183

# THIS ONLY USED WITH encode_password_custom()
# if pw-sha2 overlay is present on the server additional passwd type could be used
PWSHA2_OVERLAY = True
PWSHA2_OVERLAY_PASSWD_TYPE = ['SHA256',
                              'SSHA256',
                              'SHA384',
                              'SSHA384',
                              'SHA512',
                              'SSHA512']

DEFAULT_SECRET_TYPE = 'SSHA512'

# additional field to be filled on save password trigger
# key is the model field, value is the Hash used in hash_functions.encode_secret
PASSWD_FIELDS_MAP = {
                       'sambaNTPassword': 'NT',
                    }

# values matches specialized calls in hash_functions.py
SECRET_PASSWD_TYPE = ['Plaintext',
                      'SHA',
                      'SSHA',
                      'MD5',
                      'SMD5',
                      'PKCS5S2',
                      'CRYPT',
                      'CRYPT-MD5',
                      'CRYPT-SHA-256',
                      'CRYPT-SHA-512']

if PWSHA2_OVERLAY:
    SECRET_PASSWD_TYPE.extend(PWSHA2_OVERLAY_PASSWD_TYPE)

# these are too weak
DISABLED_SECRET_TYPES = ['Plaintext',
                         'MD5',
                         'SMD5',
                         'PKCS5S2']
# encode_password_custom end

# Password validation on user web form input field
SECRET_FIELD_VALIDATORS = {'regexp_lowercase': '[a-z]+',
                           'regexp_uppercase': '[A-Z]+',
                           'regexp_number': '[0-9]+',
                           'regexp_special': '[\!\%\-_+=\[\]{\}\:\,\.\?\<\>\(\)\;]+'}

EPPN_VALIDATOR = '[a-zA-Z\.\_\:\-0-9]+@[a-zA-Z\-\.\_]+'

# https://www.internet2.edu/products-services/trust-identity/mace-registries/urnmace-namespace/
SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX = 'urn:schac:personalUniqueCode'

SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX = 'urn:schac:homeOrganizationType'
SCHAC_HOMEORGANIZATIONTYPE_DEFAULT = ['educationInstitution',
                                      'university']

SCHAC_HOMEORGANIZATION_DEFAULT = settings.LDAP_BASE_DOMAIN

SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX = 'urn:schac:personalUniqueID'
SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE = 'IT'
SCHAC_PERSONALUNIQUEID_DEFAULT_DOCUMENT_CODE = 'CF'
SCHAC_PERSONALUNIQUEID_DOCUMENT_CODE = [SCHAC_PERSONALUNIQUEID_DEFAULT_DOCUMENT_CODE,
                                        'ID', 'CI', 'NIF', 'FIC', 'NIN']

RFC3339_DATE_FORMAT = "%Y%m%d"
SCHAC_DATEOFBIRTH_FORMAT = RFC3339_DATE_FORMAT

READONLY_FIELDS = ['memberOf',
                   'creatorsName',
                   'modifiersName',
                   # 'userPassword',
                   # 'sambaNTPassword',
                   'createTimestamp',
                   'modifyTimestamp',
                   'pwdChangedTime',
                   'pwdFailureTime'
                   ]

AFFILIATION = (
                # ('faculty', 'faculty'), deprecated
                ('student', 'student'),
                ('staff', 'staff'),
                ('alum', 'alum'),
                ('member', 'member'),
                ('affiliate', 'affiliate'),
                ('employee', 'employee'),
                ('library-walk-in', 'library-walk-in'),
              )

# this option deactive previous auth sessions when a new LDAP auth occours
MULTIPLE_USER_AUTH_SESSIONS = False
