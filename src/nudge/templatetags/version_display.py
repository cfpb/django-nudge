from django import template
register = template.Library()

from reversion.models import VERSION_TYPE_CHOICES

VERSION_TYPE_LOOKUP=dict(VERSION_TYPE_CHOICES)

@register.filter(name='change_type')
def change_type(value):
    return VERSION_TYPE_LOOKUP[int(value)]