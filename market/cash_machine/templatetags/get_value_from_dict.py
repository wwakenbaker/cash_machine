from django import template

register = template.Library()

@register.filter
def get_value_from_dict(dict_data, key):
    return dict_data.get(key)