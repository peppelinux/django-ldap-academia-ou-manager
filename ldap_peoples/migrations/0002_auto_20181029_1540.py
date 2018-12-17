# Generated by Django 2.0.7 on 2018-10-29 15:40

from django.db import migrations
import ldapdb.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ldap_peoples', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ldapacademiauser',
            name='dn',
            field=ldapdb.models.fields.CharField(default='1', max_length=200, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ldapgroup',
            name='dn',
            field=ldapdb.models.fields.CharField(default='1', max_length=200, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
