from django import template
import json
register = template.Library()

@register.filter
def remove_from_list(value, item_to_remove):
    if isinstance(value, str):
       try:
          value = json.loads(value)
       except:
         return []
    if not isinstance(value, list):
        return value
    if not item_to_remove:
        return value
    return  json.dumps([item for item in value if item != item_to_remove])


# custom_filters.py
from django import template

register = template.Library()

@register.filter
def join(value, arg):
    """Joins a list of values with the given separator"""
    return arg.join(value)