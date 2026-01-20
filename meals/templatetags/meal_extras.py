from django import template

register = template.Library()

@register.filter
@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field"""
    return field.as_widget(attrs={'class': css_class})