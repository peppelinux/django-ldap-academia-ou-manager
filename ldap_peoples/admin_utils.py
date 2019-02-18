def get_values_as_html_ul(data):
    if not data: return ''
    value = '<ul>'
    if isinstance(data, str):
        data = data.splitlines()
    for i in data:
        value += '<li>{}</li>'.format(i)
    value += '</ul>'
    return value
