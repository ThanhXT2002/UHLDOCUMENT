# context_processors.py

from .menu_config import MENU_CONFIG, MENU_CONFIG_2

def menu_config(request):
    if request.user.is_staff:
        return {'MENU_CONFIG': MENU_CONFIG}
    else:
        return {'MENU_CONFIG': MENU_CONFIG_2}
