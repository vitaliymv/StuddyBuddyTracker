from django import template

register = template.Library()

@register.filter
def time_format(seconds):
    if not seconds:
        return "0s"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    result = []

    if hours:
        result.append(f"{hours}h")

    if minutes:
        result.append(f"{minutes}m")

    result.append(f"{secs}s")

    return " ".join(result)