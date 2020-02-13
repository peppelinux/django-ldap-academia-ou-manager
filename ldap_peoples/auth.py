import ldap
import logging


from django.conf import settings
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.sessions.models import Session
# from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.db import connections
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . models import LdapAcademiaUser


logger = logging.getLogger(__name__)


class LdapAcademiaAuthBackend(ModelBackend):
    """
        This class logout a user if another session of that user
        will be created

        in settings.py
        AUTHENTICATION_BACKENDS = [ 'django.contrib.auth.backends.ModelBackend',
                                    'ldap_peoples.auth.LdapAcademiaAuthBackend'
                                  ]
    """
    def authenticate(self, request, username=None, password=None):
        ldap_conn = connections['ldap']
        user = None
        lu = LdapAcademiaUser.objects.filter(uid=username).first()
        if not lu:
            return None

        # check if username exists and if it is active
        try:
            ldap_conn.connect()
            ldap_conn.connection.bind_s(lu.distinguished_name(),
                                        password)
            ldap_conn.connection.unbind_s()
        except Exception as e:
            logger.error(e)
            return None

        # if account beign unlocked this will be always false
        if not lu.is_active():
            return None

        scoped_username = '@'.join((lu.uid, settings.LDAP_BASE_DOMAIN))
        try:
            user = get_user_model().objects.get(username=scoped_username)
            # update attrs:
            if user.email != lu.mail[0]:
                user.email = lu.mail[0]
                user.save()
        except Exception as e:
            user = get_user_model().objects.create(dn=lu.dn,
                                                           username=scoped_username,
                                                           email=lu.mail[0],
                                                           first_name=lu.cn,
                                                           last_name=lu.sn)

        # disconnect already created session, only a session per user is allowed
        # get all the active sessions
        if not settings.MULTIPLE_USER_AUTH_SESSIONS:
            for session in Session.objects.all():
                try:
                    if int(session.get_decoded()['_auth_user_id']) == user.pk:
                        session.delete()
                except (KeyError, TypeError, ValueError):
                    pass

        # if access notification email is on
        # works only if this field is active in account model (need to be customized first!)
        if hasattr(user, 'access_notification'):
            if user.access_notification:
                user_agent = ''
                ipaddress = ''
                if request:
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', ' , ')
                    if x_forwarded_for:
                        ipaddress = x_forwarded_for.split(',')[-1].strip()
                    else:
                        ipaddress = request.META.get('REMOTE_ADDR')
                d = {'time': timezone.localtime(),
                     'user': lu.uid,
                     'hostname': settings.HOSTNAME,
                     'user_agent': user_agent,
                     'ipaddress': ipaddress}
                send_mail(_('Access notification'),
                              settings.IDENTITY_MSG_ACCESS.format(**d),
                              settings.DEFAULT_FROM_EMAIL,
                              lu.mail, # it's a list :)
                              fail_silently=True,
                              auth_user=None,
                              auth_password=None,
                              connection=None,
                              html_message=None)

        return user
