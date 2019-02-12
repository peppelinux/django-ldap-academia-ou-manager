from django.test import TestCase
from ldap_peoples.models import LdapAcademiaUser
from ldap_peoples.ldap_utils import (import_entries_from_json,
                                     import_entries_from_ldif)


_test_guy = { "uid": "jimmy",
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
              "modifiersName": "cn=admin,dc=testunical,dc=it",
              "pwdChangedTime": "20190211171629Z"}


class LdapAcademiaUserTestCase(TestCase):
    def setUp(self):
        """test user creation"""
        LdapAcademiaUser.objects.create(**_test_guy)

    def test_json_import_export(self):
        d = LdapAcademiaUser.objects.get(uid="jimmy")
        export = d.json()
        print(export)
        d.delete()
        imp = import_entries_from_json(d)
        self.assertIs(imp, False)

    def test_ldif_import_export(self):
        d = LdapAcademiaUser.objects.get(uid="jimmy")
        export = d.ldif()
        print(export)
        d.delete()
        imp = import_entries_from_ldif(d)
        self.assertIs(imp, False)
