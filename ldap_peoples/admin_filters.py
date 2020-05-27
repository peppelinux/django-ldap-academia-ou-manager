from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter


class GenericSearch(admin.SimpleListFilter):
    title = 'Custom Search'
    parameter_name = 'custom_search'
    template = 'filters/custom_search.html'

    def lookups(self, request, model_admin):
        """ it can be overloaded as follows
            return (('uid', 'uid'),
                ('mail', 'mail'),
                ('sn', 'sn'),
                ('schacPersonalUniqueID','schacPersonalUniqueID'),
                ('schacPersonalUniqueCode','schacPersonalUniqueCode'),
                )
        """
        l = []
        for i in model_admin.model._meta.fields:
            l.append((i.name, i.name))
        return l

    def queryset(self, request, queryset):
        """?custom_search=filter,mail__exact,peppelinux%40yahoo.it||
        """
        if request.GET.get(self.parameter_name):
            post = dict(request.GET)[self.parameter_name][0]
            search_list = []
            search_list = post.split('||')
            for se in search_list:
                sple = se.split(',')
                se_dict = {'{}__{}'.format(sple[0], sple[2]): sple[3]}
                try:
                    queryset = getattr(queryset, sple[1])(**se_dict)
                except Exception as e:
                    messages.add_message(request, messages.ERROR,
                                         'Search filter {} failed: {}'.format(se, e))
            return queryset


    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }


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
        l.append((None, 'no-affiliation'))
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
