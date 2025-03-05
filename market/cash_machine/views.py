import random
from datetime import datetime

import pdfkit
from django.template import engines
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework.decorators import api_view

from .models import Item
from .serializers import ItemSerializer


@api_view(["POST"])
def make_receipts(request):
    """
    Создаёт чек по списку
    На вход подается список с Item.id
    """
    items_ids = request.data.get("items", [])
    items = []  # list of items
    quantity = {}  # quantity of items

    """ Наполняется quantity от items_ids """
    for item_id in items_ids:
        item = Item.objects.filter(id=item_id).first()
        if item:
            items.append(item)
            quantity[item.id] = quantity.get(item.id, 0) + 1

    """ Вычисляется общая стоимость """
    total_price = sum(float(item.price) for item in items)

    """ Умножает цену на количество """
    for item in items:
        item.price = item.price * quantity.get(item.id)

    """ Получаем текущее время чека и сериализуем данные """
    receipt_time = datetime.now().strftime("%d-%m-%Y %H:%M")
    serializer = ItemSerializer(set(items), many=True)

    """ Если нет ни одного товара, возвращаем ошибку """
    if not serializer.data:
        return Response({"error": "No items found"}, status=400)

    """ Генерируем PDF чек
     и сохраняем его в /media"""
    context = {
        "items": serializer.data,
        "total_price": total_price,
        "receipt_time": receipt_time,
        "quantity": quantity,
    }

    env = engines["django"]
    tm = env.get_template("receipt.html")
    smg = tm.render(context=context)
    options = {
        "page-size": "Letter",
        "margin-top": "0.75in",
        "margin-right": "1.75in",
        "margin-bottom": "0.75in",
        "margin-left": "1.75in",
    }

    pdfkit.from_string(
        smg,
        f"media/{receipt_time + '-' +str(random.randint(100,999))}",
        options=options,
    )

    template = render(request, "receipt.html", context)
    return template
