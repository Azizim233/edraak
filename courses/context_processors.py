from .models import SiteSettings


def site_settings(request):
    """ھەممە template غا توربەت تەڭشەكلىرىنى بېرىدۇ"""
    return {
        'settings': SiteSettings.get_settings()
    }