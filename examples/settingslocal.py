import ldap
import os

APP_NAME = 'APP NAME LDAP'
HOSTNAME = 'your.hostname.eu'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
# you can generate a valid one issuing the command:
#       manage.py generate_secret_key
SECRET_KEY = '7nv@u)8-s!ro*nji2)#moi25tkx^5$=9w_he2hw20rfya)l!j!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [HOSTNAME, 'localhost']

if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# The maximum number of parameters that may be received via GET or POST before a
# SuspiciousOperation (TooManyFields) is raised. You can set this to None to disable the check.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

LDAP_OU = 'people'
LDAP_BASE_DOMAIN = 'testunical.it'
LDAP_BASEDN = 'dc='+',dc='.join(LDAP_BASE_DOMAIN.split('.'))
LDAP_CACERT = os.path.sep.join((BASE_DIR,
                                'certificates',
                                'slapd-cacert.pem'))

# Also interesting is their use as values on ldap.OPT_X_TLS_REQUIRE_CERT (TLS equivalent: TLS_REQCERT)
# demand and hard (default):
    # no certificate provided: quits
    # bad certificate provided: quits
# try
    # no certificate provided: continues
    # bad certificate provided: quits
# allow
    # no certificate provided: continues
    # bad certificate provided: continues
# never
    # no certificate is requested

LDAP_CONNECTION_OPTIONS = {
                            # ldap.OPT_REFERRALS: 0,
                            ldap.OPT_PROTOCOL_VERSION: 3,
                            ldap.OPT_DEBUG_LEVEL: 255,
                            ldap.OPT_X_TLS_CACERTFILE: LDAP_CACERT,
                            
                            # force /etc/ldap.conf configuration. 
                            ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_DEMAND,
                            ldap.OPT_X_TLS: ldap.OPT_X_TLS_DEMAND,
                            ldap.OPT_X_TLS_DEMAND: True,
                            
                            # ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
                            # ldap.OPT_X_TLS: ldap.OPT_X_TLS_NEVER,
                            # ldap.OPT_X_TLS_DEMAND: False,
                          }


DATABASES = {
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        # only in localhost
        #'NAME': 'ldapi:///',
        'NAME': 'ldaps://ldap.{}'.format(HOSTNAME),
        # 'NAME': 'ldaps://127.0.0.1/',
        'USER': 'cn=admin,{}'.format(LDAP_BASEDN),
        'PASSWORD': 'slapdsecret',
        'PORT': 636,
        #'TLS': True,
        'CONNECTION_OPTIONS': LDAP_CONNECTION_OPTIONS
     },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DBNAME',
        'HOST': 'localhost',
        'USER': 'DBUSER',
        'PASSWORD': 'DBPASSWORD',
        'PORT': ''
    }
}

DATABASE_ROUTERS = ['ldapdb.router.Router']

LANGUAGE_CODE = 'it-it'
TIME_ZONE = 'Europe/Rome'

ADMINS = [('Name surname', 'name.surname@{}'.format(HOSTNAME)),]
