from .models import Category


def categories_menu(request):
    return {
        "menu_categories": Category.objects.filter(
            is_active=True, level=0
        ).prefetch_related("children__children"),
    }
