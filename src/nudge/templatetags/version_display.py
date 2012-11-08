from django import template
from nudge.utils import VERSION_TYPE_LOOKUP

register = template.Library()


@register.filter
def change_type(value):
    return VERSION_TYPE_LOOKUP[int(value)]
