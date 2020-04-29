from django.conf import settings
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter


class TitleListFilter(MultipleChoiceListFilter):
    title = 'Title'
    parameter_name = 'title'

    def lookups(self, request, model_admin):
        return [(k, v) for k,v in sorted(settings.LDAP_PEOPLES_TITLES)]

    def queryset(self, request, queryset):
        pk_list = []
        if request.GET.get(self.parameter_name):
            for value in request.GET[self.parameter_name].split(','):
                kwargs = {self.parameter_name: value}
                q = queryset.filter(**kwargs)
                for dip in q.values_list('pk'):
                    pk_list.append(dip[0])
            return queryset.filter(pk__in=pk_list)


class AffiliationListFilter(MultipleChoiceListFilter):
    title = 'Affiliation'
    parameter_name = 'eduPersonAffiliation'

    def lookups(self, request, model_admin):
        l = [(k, v) for k,v in sorted(settings.AFFILIATION)]
        l.append(('no-affiliation', ''))
        return l
    def queryset(self, request, queryset):
        pk_list = []
        if request.GET.get(self.parameter_name):
            for value in request.GET[self.parameter_name].split(','):
                kwargs = {self.parameter_name: value}
                q = queryset.filter(**kwargs)
                for dip in q.values_list('pk'):
                    pk_list.append(dip[0])
            return queryset.filter(pk__in=pk_list)
