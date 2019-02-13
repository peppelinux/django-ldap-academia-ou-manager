import io

from django.conf import settings
from django.test import TestCase
from ldap_peoples.models import LdapAcademiaUser
from ldap_peoples.serializers import LdapImportExport

_test_uid = 'jimmy89234_yWHO!'
_test_guy = { "uid": "jimmy89234_yWHO!",
              "cn": "jimmy",
              "givenName": "jimmy",
              "sn": "grossi",
              "displayName": "jimmy Rossi",
              "mail": [
                "jimmy.grossi@testunical.it",
                "jgrossi@edu.testunical.it"
              ],
              "userPassword": "{SSHA512}Z9jkoG3nyFzVzZy/8sVNLEFhUhPTeI15n0VHoMuA1bKwqbvxnm9IzU4ftErYtBkB20GcjGR+cihWs6s7jW1Mfq4v9pLFjlqg",
              "sambaNTPassword": "448075d48c550dca6937175e16df1dc6",
              "eduPersonPrincipalName": "grossi@unical",
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
                "urn:schac:homeOrganizationType:IT:educationInstitution",
                "urn:schac:homeOrganizationType:IT:university"
              ],
              "schacPersonalUniqueID": [
                "urn:schac:personalUniqueID:IT:CF:CODICEFISCALEjimmy"
              ],
              "schacDateOfBirth": "20190213",
              "schacExpiryDate": "20190814021605Z",
              "createTimestamp": "20190211161620Z",
              "modifyTimestamp": "20190211161629Z",
              "creatorsName": "cn=admin,dc=testunical,dc=it",
              "modifiersName": "cn=admin,dc=testunical,dc=it"}


class LdapAcademiaUserTestCase(TestCase):
    def setUp(self):
        """test user creation"""
        d = LdapAcademiaUser.objects.filter(uid=_test_uid).first()
        if d:
            d.delete()
        LdapAcademiaUser.objects.create(**_test_guy)

    def test_ldif_import_export(self):
        d = LdapAcademiaUser.objects.get(uid=_test_uid)
        out = io.StringIO()
        out.write(d.ldif())
        out.seek(0)
        d.delete()
        imp = LdapImportExport.import_entries_from_ldif(out)
        self.assertIs(imp, True)

    def test_json_import_export(self):
        d = LdapAcademiaUser.objects.get(uid=_test_uid)
        out = io.StringIO()
        out.write(d.json_ext())
        out.seek(0)
        d.delete()
        imp = LdapImportExport.import_entries_from_json(out)
        self.assertIs(imp, True)

    def test_clean(self):
        d = LdapAcademiaUser.objects.filter(uid=_test_uid).first()
        if d: d.delete()
