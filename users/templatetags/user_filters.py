from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class':css})


@register.filter
def addrows(field, number):
    return field.as_widget(attrs={'rows':number})