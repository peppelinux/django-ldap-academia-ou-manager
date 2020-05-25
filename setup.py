from glob import glob
from setuptools import find_packages, setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='django-ldap-academia-ou-manager',
      version='v0.9.0',
      description=('Django Admin manager for Academia Users '
                   'with eduPerson schema and '
                   'SCHAC (SCHema for ACademia).'),
      long_description=readme(),
      classifiers=[
                  'Development Status :: 5 - Production/Stable',
                  'License :: OSI Approved :: BSD License',
                  'Programming Language :: Python :: 3 :: Only',
                  'Operating System :: POSIX :: Linux'
                  ],
      url='https://github.com/peppelinux/django-ldap-academia-ou-manager',
      author='Giuseppe De Marco',
      author_email='giuseppe.demarco@unical.it',
      license='BSD',
      packages=find_packages(),
      package_data={'': ['*.html']},
      data_files=[
        ('', glob('ldap_peoples/templates/*/*/*.html')),
      ],
      include_package_data=True,
      dependency_links=['https://github.com/peppelinux/django-ldapdb/tarball/master#egg=peppelinux_django_ldapdb-1.0',],
      install_requires=[
                      'bcrypt>=3.1.4',
                      'Django>=2.0.7',
                      'django-admin-rangefilter>=0.3.9',
                      'passlib>=1.7.1',
                      'chardet',
                  ],
     )
