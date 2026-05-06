from .models import SiteSettings


def site_settings(request) -> dict:
    return {"site_settings": SiteSettings.load()}
