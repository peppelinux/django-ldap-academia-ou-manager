from ldap_peoples.models import LdapAcademiaUser
import datetime

d = {'cn': 'pedppe',
     'displayName': 'peppde Rossi',
     'eduPersonAffiliation': ['faculty', 'member'],
     'eduPersonEntitlement': ['urn:mace:terena.org:tcs:escience-user',
      'urn:mace:terena.org:tcs:personal-user'],
     'eduPersonOrcid': '',
     'eduPersonPrincipalName': 'grodsfssi@unical',
     'eduPersonScopedAffiliation': ['member@testunical.it', 'staff@testunical.it'],
     'givenName': 'peppe',
     'mail': ['peppe44.grossi@testunical.it', 'pgros44si@edu.testunical.it'],
     'sambaNTPassword': 'a2137530237ad733fdc26d5d7157d43f',
     'schacHomeOrganization': 'testunical.it',
     'schacHomeOrganizationType': ['educationInstitution', 'university'],
     'schacPersonalUniqueID': ['urn:schac:personalUniqueID:it:CF:CODICEFISCALEpe3245ppe'],
     'schacPlaceOfBirth': '',
     'sn': 'grossi',
     'telephoneNumber': [],
     'uid': 'perrrppe',
     'userPassword': '{SHA512}oMKZtxqeWdXrsHkX5wYBo1cKoQPpmnu2WljngOyQd7GQLR3tsxsUV77aWV/k1x13m2ypytR2JmzAdZDjHYSyBg=='}

u = LdapAcademiaUser.objects.create(**d)
u.delete()


entry = {'givenName': 'Giuseppe', 'cn': 'Giuseppe', 'sn': 'De Marco', 'schacPlaceOfBirth': 'IT,Cosenza',
'schacDateOfBirth': datetime.date(1983, 8, 27), 'displayName': 'Giuseppe De Marco',
'mail': ['ingoalla@testunical.it'], 'telephoneNumber': ['0984496945'], 'uid': 'peppelinux27', 'schacHomeOrganization': 'testunical.it'}
u = LdapAcademiaUser.objects.create(**entry)
