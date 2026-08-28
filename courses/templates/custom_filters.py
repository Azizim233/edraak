from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """دىكتاتتىن ئېلېمېنت ئېلىش"""
    if dictionary is None:
        return None
    return dictionary.get(key)