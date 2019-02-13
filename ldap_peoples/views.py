from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse,  HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .serializers import LdapImportExport


@user_passes_test(lambda u: u.is_staff)
def import_file(request):
    file_format = request.POST.get('file_format')
    file_to_import = request.FILES.get('file_to_import')
    # content here
    url = reverse('admin:ldap_peoples_ldapacademiauser_changelist')
    if not file_to_import:
        return HttpResponseRedirect(url)
    if not file_format or not file_to_import:
        # scrivi un messaggio di errore
        pass
    response = False
    if file_format == 'json':
        response = LdapImportExport.import_entries_from_json(file_to_import)
    elif file_format == 'ldif':
        response = LdapImportExport.import_entries_from_ldif(file_to_import)
    return HttpResponseRedirect(url)
