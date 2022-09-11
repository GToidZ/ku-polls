from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return None


@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None
