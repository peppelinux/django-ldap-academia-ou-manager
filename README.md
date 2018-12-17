LDAP django admin manager for Academia OU
-----------------------------------------
A custom way to manage Academia User according to eduPerson schema and
SCHAC (SCHema for ACademia).

References
----------

- [eduPerson Schema  ] (https://software.internet2.edu/eduperson/internet2-mace-dir-eduperson-201602.html)
- [SCHAC] (https://wiki.refeds.org/display/STAN/SCHAC)

Preview
-------

![Alt text](img/preview.png)

Setup examples
--------------

#### Create environment dir and activate it
````
apt install python3-dev python3-pip python3-setuptools
pip3 install virtualenv

export dest_dir=django-ldap-academia-ou-manager.env
virtualenv -p python3 $dest_dir
source $dest_dir/bin/activate
pip install django
````

#### Create a project
````
PROJ_NAME=django-ldap-academia-ou-manager
django-admin startproject $PROJ_NAME
cd $PROJ_NAME
````

#### Install the app
Illustrates a quite raw approach for dev users.
Soon as possibile there will be a setup.py for automated install.
````
git clone https://github.com/peppelinux/django-ldap-academia-ou-manager.git
ln -s django-ldap-academia-ou-manager/ldap_peoples .
pip install -r django-ldap-academia-ou-manager/requirements
````

#### Edit settings with DB
View settings.py and settingslocal.py in example folder.
After setting up the Django projhect with an SQL DB, apply the
fakes migrations for LDAP:
````
./manage.py migrate ldap_peoples 0006 --fake
````

Using the Object Relation Mapper
--------------------------------
One of the advantage of using the ORM is the possibility to make these kind of queries
to a LDAP database.

#### User update attributes
````
from ldap_peoples.models import LdapAcademiaUser
lu = LdapAcademiaUser.objects.get(uid='mario')

# as multivalue
lu.eduPersonAffiliation.append('alumn')
````

#### User creation example
````
# user creation
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
     'schacPersonalUniqueID': ['urn:schac:personalUniqueID:IT:CF:CODICEFISCALEpe3245ppe'],
     'schacPlaceOfBirth': '',
     'sn': 'grossi',
     'telephoneNumber': [],
     'uid': 'perrrppe',
     'userPassword': '{SHA512}oMKZtxqeWdXrsHkX5wYBo1cKoQPpmnu2WljngOyQd7GQLR3tsxsUV77aWV/k1x13m2ypytR2JmzAdZDjHYSyBg=='}

u = LdapAcademiaUser.objects.create(**d)
u.delete()
````
