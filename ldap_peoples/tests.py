import datetime
import io
import random
import string

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from ldap_peoples.models import LdapAcademiaUser
from ldap_peoples.serializers import LdapImportExport

from . settings import LDAP_DATETIME_FORMAT


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def get_test_guy():
    _test_uid = 'unit_test_user_{}'.format(randomString())
    _test_guy = { "uid": _test_uid,
                  "cn": _test_uid,
                  "givenName": _test_uid,
                  "sn": _test_uid,
                  "displayName": _test_uid,
                  "mail": [
                    "{}@testunical.it".format(_test_uid),
                    "{}@edu.testunical.it".format(_test_uid)
                  ],
                  "userPassword": "{SSHA512}Z9jkoG3nyFzVzZy/8sVNLEFhUhPTeI15n0VHoMuA1bKwqbvxnm9IzU4ftErYtBkB20GcjGR+cihWs6s7jW1Mfq4v9pLFjlqg",
                  "sambaNTPassword": "448075d48c550dca6937175e16df1dc6",
                  "eduPersonPrincipalName": "{}@unical".format(_test_uid),
                  "eduPersonAffiliation": [
                    "faculty",
                    "member"
                  ],
                  "eduPersonScopedAffiliation": [
                    "member@testunical.it",
                    "staff@testunical.it"
                  ],
                  "eduPersonEntitlement": [
                    "urn:mace:terena.org:tcs:escience-user",
                    "urn:mace:terena.org:tcs:personal-user"
                  ],
                  "schacHomeOrganization": "testunical.it",
                  "schacHomeOrganizationType": [
                    "urn:schac:homeOrganizationType:it:university"
                  ],
                  "schacPersonalUniqueID": [
                    "urn:schac:personalUniqueID:it:CF:{}".format(_test_uid)
                  ],
                  "schacDateOfBirth": "20190213",
                  "schacExpiryDate": (timezone.localtime()+datetime.timedelta(minutes=60)).strftime(LDAP_DATETIME_FORMAT),
                  "createTimestamp": "20190211161620Z",
                  "modifyTimestamp": "20190211161629Z",
                  "creatorsName": "cn=admin,dc=testunical,dc=it",
                  "modifiersName": "cn=admin,dc=testunical,dc=it"}
    return _test_guy


LAST_GUY = None
TEST_GUYS = []
for i in range(1):
    LAST_GUY = get_test_guy()
    LAST_UID = LAST_GUY['uid']
    print(i, LAST_UID)
    TEST_GUYS.append(LAST_UID)
    LdapAcademiaUser.objects.create(**LAST_GUY)


class LdapAcademiaUserTestCase(TestCase):
    databases = ["default", "ldap"]

    def setUp(self):
        """test user creation"""
        self.test_uid = LAST_UID

    def test_ldif_import_export(self):
        d = LdapAcademiaUser.objects.get(uid=self.test_uid)
        out = io.StringIO()
        out.write(d.ldif())
        out.seek(0)
        d.delete()
        imp = LdapImportExport.import_entries_from_ldif(out)
        self.assertIs(imp, True)

    def test_json_import_export(self):
        d = LdapAcademiaUser.objects.get(uid=self.test_uid)
        out = io.StringIO()
        out.write(d.json_ext())
        out.seek(0)
        d.delete()
        imp = LdapImportExport.import_entries_from_json(out)
        self.assertIs(imp, True)

    # def tearDown(self):
        # d = LdapAcademiaUser.objects.filter(uid=self.test_uid).first()
        # if d: d.delete()
