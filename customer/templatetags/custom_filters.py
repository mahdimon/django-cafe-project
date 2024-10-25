from django import template
from django.utils import timezone

register = template.Library()
@register.filter
def dictitem(dictionary, key):
    return dictionary.get(key)