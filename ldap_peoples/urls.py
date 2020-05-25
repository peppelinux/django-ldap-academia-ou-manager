from django.urls import path
from .views import *

app_name="ldap_peoples"

urlpatterns = [
    path('{}/import'.format(app_name),
         import_file, name='import_file'),
]
