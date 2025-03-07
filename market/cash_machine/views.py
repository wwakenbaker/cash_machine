from django.http import HttpResponse

from rest_framework.decorators import api_view
from .services import make_recipe, get_media_file


@api_view(["POST"])
def make_receipts_view(request):
    """
    Создаёт чек по списку
    На вход подается список с Item.id
    Возвращает HTML шаблон с QR кодом
    """
    items_ids = request.data.get("items", [])
    return HttpResponse(make_recipe(items_ids))


@api_view(["GET"])
def media_file_view(request, file_name):
    """
    Возвращает PDF чек по его имени из /media
    """
    return get_media_file(file_name)
