# custom_filters.py
from django import template

register = template.Library()

@register.filter
def join(value, arg):
    """Joins a list of values with the given separator"""
    return arg.join(value)
