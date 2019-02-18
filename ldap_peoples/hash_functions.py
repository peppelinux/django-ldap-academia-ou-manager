import crypt

from base64 import encodestring
try:
    from django.conf import settings
    _CHARSET = settings.DEFAULT_CHARSET
except:
    _CHARSET = 'utf-8'
from hashlib import (sha1,
                     sha256,
                     sha384,
                     sha512)
from passlib.hash import (ldap_plaintext,
                          lmhash,
                          nthash,
                          ldap_md5,
                          ldap_md5_crypt,
                          ldap_salted_md5,
                          ldap_sha1,
                          ldap_salted_sha1,
                          atlassian_pbkdf2_sha1,
                          ldap_md5_crypt,
                          ldap_sha256_crypt,
                          ldap_sha512_crypt)
from os import urandom

# how many bytes the salt is long
_LDAP_SALT_LENGHT = 8

def encode_secret(enc, new_value=None):
    """
    https://docs.python.org/3.5/library/hashlib.html
    http://passlib.readthedocs.io/en/stable/lib/passlib.hash.ldap_std.html
    """
    password_renewed = None
    if enc == 'Plaintext':
        password_renewed = ldap_plaintext.hash(new_value)
    elif enc == 'NT':
        password_renewed = nthash.hash(new_value)
    elif enc == 'LM':
        password_renewed = lmhash.hash(new_value)
    elif enc == 'MD5':
        password_renewed = ldap_md5.hash(new_value.encode(_CHARSET))
    elif enc == 'SMD5':
        password_renewed = ldap_salted_md5.hash(new_value.encode(_CHARSET))
    elif enc == 'SHA':
        password_renewed = ldap_sha1.hash(new_value.encode(_CHARSET))
    elif enc == 'SSHA':
        salt = urandom(8)
        hash = sha1(new_value.encode(_CHARSET))
        hash.update(salt)
        hash_encoded = encodestring(hash.digest() + salt)
        password_renewed = hash_encoded.decode(_CHARSET)[:-1]
        password_renewed = '{%s}%s' % (enc, password_renewed)
    elif enc == 'SHA256':
        password_renewed = sha256(new_value.encode(_CHARSET)).digest()
        password_renewed = '{%s}%s' % (enc, encodestring(password_renewed).decode(_CHARSET)[:-1])
    elif enc == 'SSHA256':
        salt = urandom(_LDAP_SALT_LENGHT)
        hash = sha256(new_value.encode(_CHARSET))
        hash.update(salt)
        hash_encoded = encodestring(hash.digest() + salt)
        password_renewed = hash_encoded.decode(_CHARSET)[:-1]
        password_renewed = '{%s}%s' % (enc, password_renewed)
    elif enc == 'SHA384':
        password_renewed = sha384(new_value.encode(_CHARSET)).digest()
        password_renewed = '{%s}%s' % (enc, encodestring(password_renewed).decode(_CHARSET)[:-1])
    elif enc == 'SSHA384':
        salt = urandom(_LDAP_SALT_LENGHT)
        hash = sha384(new_value.encode(_CHARSET))
        hash.update(salt)
        hash_encoded = encodestring(hash.digest() + salt)
        password_renewed = hash_encoded.decode(_CHARSET)[:-1]
        password_renewed = '{%s}%s' % (enc, password_renewed)
    elif enc == 'SHA512':
        password_renewed = sha512(new_value.encode(_CHARSET)).digest()
        password_renewed = '{%s}%s' % (enc, encodestring(password_renewed).decode(_CHARSET)[:-1])
    elif enc == 'SSHA512':
        salt = urandom(_LDAP_SALT_LENGHT)
        hash = sha512(new_value.encode(_CHARSET))
        hash.update(salt)
        hash_encoded = encodestring(hash.digest() + salt)
        password_renewed = hash_encoded.decode(_CHARSET)[:-1]
        password_renewed = '{%s}%s' % (enc, password_renewed)
    elif enc == 'PKCS5S2':
        return atlassian_pbkdf2_sha1.encrypt(new_value)
    elif enc == 'CRYPT':
        password_renewed = crypt.crypt(new_value, crypt.mksalt(crypt.METHOD_CRYPT))
        password_renewed = '{%s}%s' % (enc, password_renewed)
    elif enc == 'CRYPT-MD5':
        # this worked too
        # return ldap_md5_crypt.encrypt(new_value)
        password_renewed = crypt.crypt(new_value, crypt.mksalt(crypt.METHOD_MD5))
        password_renewed = '{CRYPT}%s' % (password_renewed)
    elif enc == 'CRYPT-SHA-256':
        password_renewed = crypt.crypt(new_value, crypt.mksalt(crypt.METHOD_SHA256))
        password_renewed = '{CRYPT}%s' % (password_renewed)
    elif enc == 'CRYPT-SHA-512':
        password_renewed = crypt.crypt(new_value, crypt.mksalt(crypt.METHOD_SHA512))
        password_renewed = '{CRYPT}%s' % (password_renewed)
    return password_renewed

def test_encoding_secrets():
    for i in settings.SECRET_PASSWD_TYPE:
        p = encode_secret(i, 'zio')
        print(i, ':', p)
    # additionals
    for i in ['NT', 'LM']:
        p = encode_secret(i, 'zio')
        print(i, ':', p)

if __name__ == '__main__':
    test_encoding_secrets()
