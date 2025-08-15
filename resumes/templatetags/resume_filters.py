import os
import re
from django import template

register = template.Library()

@register.filter
def filename(value):
    return os.path.basename(value.name)

register = template.Library()

_MONTHS = {
    "jan": "Jan", "feb": "Feb", "mar": "Mar", "apr": "Apr", "may": "May", "jun": "Jun",
    "jul": "Jul", "aug": "Aug", "sep": "Sep", "sept": "Sep", "oct": "Oct", "nov": "Nov", "dec": "Dec",
}

@register.filter
def normalize_dates(s: str) -> str:
    if not s:
        return ""
    txt = str(s)

    # Normalize months at word boundaries (aug -> Aug, Sept -> Sep, etc.)
    def repl(m):
        key = m.group(0).lower()
        return _MONTHS.get(key, m.group(0).title())

    txt = re.sub(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b', repl, txt, flags=re.I)

    # Normalize "present"
    txt = re.sub(r'\bpresent\b', 'Present', txt, flags=re.I)

    # Collapse weird spaces around dashes
    txt = re.sub(r'\s*[-–—]\s*', ' – ', txt)

    return txt.strip()