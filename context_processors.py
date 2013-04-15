from app_public.models import MenuHeader


def menu_headers(request):
    return {
        'MENU_HEADERS' : MenuHeader.objects.all()
    }