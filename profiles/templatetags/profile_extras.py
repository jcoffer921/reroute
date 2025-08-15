from django import template

register = template.Library()

@register.filter
def split_by_comma(value):
    """
    Accepts either a comma-separated string OR a ManyToMany queryset
    and returns a list of stripped skill names.
    """
    if not value:
        return []

    # Handle ManyToMany fields or related managers
    if hasattr(value, 'all'):
        return [str(s).strip() for s in value.all()]

    # Handle comma-separated strings
    if isinstance(value, str):
        return [s.strip() for s in value.split(',')]

    return []
