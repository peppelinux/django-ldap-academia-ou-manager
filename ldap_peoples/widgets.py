import copy
import json
import pycountry

from django.conf import settings
from django import get_version, forms
from django import utils
from django.forms import Widget
from django.forms.utils import flatatt


class SplitJSONWidgetBase(forms.Widget):
    css_textfield_class = 'vTextField'
    del_btn = ('<button type="button" class="button"'
               'style="background: #b66064;" '
               'onclick="django.jQuery(this).parent().remove(); return 0" >'
               ' Del'
               '</button>')
    add_btn_tmpl = """
                  <div>
                    <button type="button" class="button" onclick="{}" >Add {}</button>
                  </div>
                  """
    li_row_tmpl = """
                  if (window.js_cnt == undefined) {{
                      window.js_cnt = Math.floor(Math.random()*10000000) + 1;
                     }}
                  window.js_cnt += 1;
                  init_id = '{}';
                  name = '{}';
                  new_li_id = 'li_'+name+'_'+window.js_cnt;
                  name_regexp = /{}\[\d*\]/g;
                  row_li = \'{}\'.replace(init_id, new_li_id).replace(name_regexp, name+'['+ window.js_cnt +']');
                  django.jQuery('#{}').append(row_li);return 0
                  """
    source_label = '<label >Source data:</label> {}'


class SplitJSONWidget(SplitJSONWidgetBase):
    def __init__(self, attrs=None, kwargs=None, debug=True):
        self.debug = debug
        self.id_cnt = 0
        super().__init__(attrs)

    def _embed_js(self, value):
        return value.replace('"', "'").replace("'", "\\'")

    def _get_id_cnt(self):
        self.id_cnt += 1
        return self.id_cnt

    def _get_name_prefix(self, name):
        return 'ul_{}'.format(name)

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        if value:
            attrs['value'] = value
        if name:
            attrs['class'] = "{} input_{}".format(self.css_textfield_class,
                                                  name)
            attrs['name'] = '{}[{}]'.format(name, self._get_id_cnt())
        f = flatatt(attrs)
        return '<input {} />'.format(f)

    def _get_single_fields(self, name, value):
        inputs = []
        if isinstance(value, list):
            for v in sorted(value):
               inputs.append(self._as_text_field(name,
                                                 v))
        elif isinstance(value, (str, int, float)):
            inputs.append(self._as_text_field(name, value))
        elif value is None:
            inputs.append(self._as_text_field(name, ''))
        return inputs

    def _prepare_as_ul(self, name, l):
        ul_id = self._get_name_prefix(name)
        result = '<ul id="{}" >{}</ul>'
        row = ''
        cnt = 0
        for el in l:
            row_id = 'li_{}_{}'.format(name, cnt)
            row += '<li id="{}">{} {}</li>'.format(row_id , el, self.del_btn)
            cnt += 1
        return result.format(ul_id, row)

    def _get_add_btn(self, name):
        # add button render. TODO: get it from a method!
        ul_id = self._get_name_prefix(name)
        input_field = self._as_text_field(name, '')
        del_btn = self.del_btn
        init_id = 'init_id'
        li = """<li id='{}'>{}{}</li>""".format(init_id, input_field, del_btn)
        cleaned_li = self._embed_js(li)
        add_li_js = self.li_row_tmpl.format(init_id,
                                            name, name,
                                            cleaned_li,
                                            ul_id).replace('\n', '').replace(' '*2, ' ')
        add_btn = self.add_btn_tmpl.format(add_li_js, name.title().replace('_', ' '))
        # end add button
        return add_btn

    def render(self, name, value, attrs=None, renderer=None):
        add_btn = self._get_add_btn(name)
        inputs = self._get_single_fields(name, value or {})
        result = self._prepare_as_ul(name, inputs)

        if self.debug:
            # render json as well
            source_data = self.source_label.format(value)
            result = '{}{}'.format(result, source_data)
        result += add_btn
        return utils.safestring.mark_safe(result)


class SchacPersonalUniqueIdWidget(SplitJSONWidget, forms.Widget):
    """
    urn:schac:personalUniqueID:it:CF:
    """
    li_row_tmpl = """
                  if (window.js_cnt == undefined) {{
                      window.js_cnt = Math.floor(Math.random()*10000000) + 1;
                     }}
                  window.js_cnt += 1;
                  init_id = '{}';
                  name = '{}';
                  new_li_id = 'li_'+name+'_'+window.js_cnt;
                  name_regexp = /\[(\d*)\]/g;
                  row_li = \'{}\';
                  row_li_changed = row_li.replace(init_id, new_li_id).replace(name_regexp, '['+ window.js_cnt +']');
                  django.jQuery('#{}').append(row_li_changed);return 0
                  """

    def _get_add_btn(self, name):
        # add button render. TODO: get it from a method!
        ul_id = self._get_name_prefix(name)
        input_field = self._as_text_field(name, '')
        del_btn = self.del_btn
        init_id = 'init_id'
        li = """<li id='{}'>{}{}</li>""".format(init_id, input_field, del_btn)
        cleaned_li = self._embed_js(li)
        add_li_js = self.li_row_tmpl.format(init_id,
                                            name,
                                            cleaned_li,
                                            ul_id).replace('\n', '').replace(' '*2, ' ')
        add_btn = self.add_btn_tmpl.format(add_li_js, name.title().replace('_', ' '))
        # end add button
        return add_btn

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        l_value = [settings.SCHAC_PERSONALUNIQUEID_DEFAULT_PREFIX,
                   settings.SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE,
                   settings.SCHAC_PERSONALUNIQUEID_DOCUMENT_CODE[0]]
        if value:
            sv = value.split(':')
            if len(sv) > 4:
                l_value.append(sv[-1])
                l_value[1] = sv[-3]
                l_value[2] = sv[-2]
                value = l_value[3]
        else:
            value = ''
        row_id = self._get_id_cnt()
        static_prefix = "<input style='width: 170px;' class='vTextField' value='{}' name='{}_1_[{}]' disabled>".format(l_value[0],
                                                                                                                   name,
                                                                                                                   row_id)
        select_1_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_1_tmpl = """<option value="{}">{}</option>
                        """
        select_1_options_list = ['<option value="{}" selected>{}</option>'.format(l_value[1],
                                                                                  l_value[1]),]

        fout_countries = [e for e in pycountry.countries if e != settings.SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE]
        select_1_options_list.extend([option_1_tmpl.format(i.alpha_2, i.alpha_2) for i in fout_countries])
        select_1_options_list.extend([option_1_tmpl.format(ele, ele) for ele in ('EU', 'INT')])
        select_1 = select_1_tmpl.format('{}_2_[{}]'.format(name, row_id), '', ''.join(select_1_options_list))

        select_2_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_2_tmpl = """<option value="{}">{}</option>
                        """
        select_2_options_list = ['<option value="{}" selected>{}</option>'.format(l_value[2],
                                                                                  l_value[2]),]
        select_2_options_list.extend([option_2_tmpl.format(i, i) for i in settings.SCHAC_PERSONALUNIQUEID_DOCUMENT_CODE[1:]])
        select_2 = select_2_tmpl.format('{}_3_[{}]'.format(name, row_id), '', ''.join(select_2_options_list))

        input_suffix = "<input style='width: 170px;' class='vTextField' value='{}' name='{}_4_[{}]'>".format(value,
                                                                                                             name,
                                                                                                             row_id)
        return static_prefix+select_1+select_2+input_suffix

    def _get_single_fields(self, name, value):
        inputs = []
        if isinstance(value, list):
            for v in sorted(value):
               inputs.append(self._as_text_field(name,
                                                 v))
        elif isinstance(value, (str, int, float)):
            inputs.append(self._as_text_field(name, value))
        elif value is None:
            inputs.append(self._as_text_field(name, ''))
        return inputs

    def render(self, name, value, attrs=None, renderer=None):
        add_btn = self._get_add_btn(name)
        inputs = self._get_single_fields(name, value or {})
        result = self._prepare_as_ul(name, inputs)

        if self.debug:
            # render json as well
            source_data = self.source_label.format(value)
            result = '{}{}'.format(result, source_data)
        result += add_btn
        return utils.safestring.mark_safe(result)


class SchacPersonalUniqueCodeWidget(SchacPersonalUniqueIdWidget):
    """
    # Example: schacPersonalUniqueCode: urn:mace:terena.org:schac:personalUniqueCode:fi:tut.fi:student:165934
    #          schacPersonalUniqueCode: urn:mace:terena.org:schac:personalUniqueCode:es:uma:estudiante:a3b123c12
    #          schacPersonalUniqueCode: urn:mace:terena.org:schac:personalUniqueCode:se:LIN:87654321
    """

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        l_value = [settings.SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX,
                   settings.SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE,
                   ]

        value = value.replace(settings.SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX, '')[1:]
        sv = value.split(':')
        if len(sv) > 2:
            if len(sv) > 2:
                l_value.append(sv[-1])
                l_value[1] = sv[0]
                value = ':'.join(sv[1:])
                l_value[2] = value
        else:
            value = ''

        row_id = self._get_id_cnt()
        static_prefix = "<input style='width: 285px;' class='vTextField' value='{}' name='{}_1_[{}]' disabled>".format(l_value[0],
                                                                                                                       name,
                                                                                                                       row_id)
        select_1_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_1_tmpl = """<option value="{}">{}</option>
                        """
        select_1_options_list = ['<option value="{}" selected>{}</option>'.format(l_value[1],
                                                                                  l_value[1]),]

        fout_countries = [e for e in pycountry.countries if e != settings.SCHAC_PERSONALUNIQUECODE_DEFAULT_PREFIX ]
        select_1_options_list.extend([option_1_tmpl.format(i.alpha_2, i.alpha_2) for i in fout_countries])
        select_1_options_list.extend([option_1_tmpl.format(ele, ele) for ele in ('EU', 'INT')])
        select_1 = select_1_tmpl.format('{}_2_[{}]'.format(name, row_id), '', ''.join(select_1_options_list))

        input_suffix = "<input style='width: 170px;' class='vTextField' value='{}' name='{}_4_[{}]'>".format(value,
                                                                                                             name,
                                                                                                             row_id)
        return static_prefix+select_1+input_suffix


class SchacHomeOrganizationTypeWidget(SchacPersonalUniqueIdWidget):
    """
    urn:schac:homeOrganizationType:<country-code>:university (SCHAC) - SWITCHaai(CH)
    """

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        l_value = [settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX,
                   settings.SCHAC_PERSONALUNIQUEID_DEFAULT_COUNTRYCODE,
                   ]

        if value:
            sv = value.replace(settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX, '').split(':')[1:]
            if len(sv) > 1:
                l_value.append(sv[-1])
                l_value[1] = sv[0]
                value = sv[1]
        else:
            value = ''

        row_id = self._get_id_cnt()
        static_prefix = "<input style='width: 285px;' class='vTextField' value='{}' name='{}_1_[{}]' disabled>".format(l_value[0],
                                                                                                                       name,
                                                                                                                       row_id)
        select_1_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_1_tmpl = """<option value="{}">{}</option>
                        """
        select_1_options_list = ['<option value="{}" selected>{}</option>'.format(l_value[1],
                                                                                  l_value[1]),]

        fout_countries = [e for e in pycountry.countries if e != settings.SCHAC_HOMEORGANIZATIONTYPE_DEFAULT_PREFIX ]
        select_1_options_list.extend([option_1_tmpl.format(i.alpha_2, i.alpha_2) for i in fout_countries])
        select_1_options_list.extend([option_1_tmpl.format(ele, ele) for ele in ('EU', 'INT')])
        select_1 = select_1_tmpl.format('{}_2_[{}]'.format(name, row_id), '', ''.join(select_1_options_list))

        input_suffix = "<input style='width: 170px;' class='vTextField' value='{}' name='{}_4_[{}]'>".format(value,
                                                                                                             name,
                                                                                                             row_id)
        return static_prefix+select_1+input_suffix


class eduPersonAffiliationWidget(SchacPersonalUniqueIdWidget):
    """
    faculty, student, staff, alum, member, affiliate, employee, library-walk-in
    """

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        l_value = []
        if not value:
            value = ''
        row_id = self._get_id_cnt()
        select_1_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_1_tmpl = """<option value="{}">{}</option>
                        """
        select_1_options_list = ['<option value="{}" selected>{}</option>'.format(value, value)]
        select_1_options_list.extend([option_1_tmpl.format(i[0], i[0]) for i in settings.AFFILIATION])
        select_1 = select_1_tmpl.format('{}_1_[{}]'.format(name, row_id), '', ''.join(select_1_options_list))
        return select_1


class eduPersonScopedAffiliationWidget(SchacPersonalUniqueIdWidget):
    """
    faculty, student, staff, alum, member, affiliate, employee, library-walk-in
    """
    scoped_symbol = '@'
    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        if value:
            l_value = value.split(self.scoped_symbol)
            rendered_value = self.scoped_symbol.join((l_value[0], l_value[1]))
            select_1_options_list = ['<option value="{}" selected>{}</option>'\
            .format(l_value[0]+self.scoped_symbol, l_value[0]+self.scoped_symbol)]
        else:
            l_value = ['', '']
            rendered_value = ''
            select_1_options_list = ['<option value="{}" selected>{}</option>'\
            .format(l_value[0], l_value[0])]

        row_id = self._get_id_cnt()
        select_1_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_1_tmpl = """<option value="{}">{}</option>
                        """

        select_1_options_list.extend([option_1_tmpl.format(i[0]+self.scoped_symbol, i[0]+self.scoped_symbol) for i in settings.AFFILIATION])
        select_1 = select_1_tmpl.format('{}_1_[{}]'.format(name, row_id), '', ''.join(select_1_options_list))

        input_suffix = "<input style='width: 170px;' class='vTextField' value='{}' name='{}_2_[{}]'>".format(l_value[1],
                                                                                                             name,
                                                                                                             row_id)
        return select_1+input_suffix


class TitleWidget(SchacPersonalUniqueIdWidget):
    """
    one of settings.LDAP_PEOPLES_TITLES
    """

    def _as_text_field(self, name, value):
        attrs = self.build_attrs(self.attrs)
        l_value = []
        if not value:
            value = ''
        row_id = self._get_id_cnt()
        select_1_tmpl = """<select name={} {}>
                               {}
                           </select>"""
        option_1_tmpl = """<option value="{}">{}</option>
                        """
        select_1_options_list = ['<option value="{}" selected>{}</option>'.format(value, value)]
        select_1_options_list.extend([option_1_tmpl.format(i[0], i[0]) for i in settings.LDAP_PEOPLES_TITLES])
        select_1 = select_1_tmpl.format('{}_1_[{}]'.format(name, row_id), '', ''.join(select_1_options_list))
        return select_1
