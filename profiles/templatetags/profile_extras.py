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


@register.filter(name="initials")
def initials(user):
    """Return the user's initials from first/last name or username.
    Safe for missing fields; returns an uppercase 1–2 character string.
    """
    try:
        first = (getattr(user, 'first_name', '') or '').strip()
        last = (getattr(user, 'last_name', '') or '').strip()
        if first or last:
            return (first[:1] + last[:1]).upper()
        uname = (getattr(user, 'username', '') or '').strip()
        return uname[:2].upper()
    except Exception:
        return ""


@register.filter(name="profile_picture_url")
def profile_picture_url(user):
    """Return profile picture URL for a user if available, else empty string.
    Works with UserProfile model attached as `user.profile`.
    """
    try:
        profile = getattr(user, 'profile', None)
        if profile and getattr(profile, 'profile_picture', None) and getattr(profile.profile_picture, 'url', ''):
            return profile.profile_picture.url
    except Exception:
        pass
    return ""
