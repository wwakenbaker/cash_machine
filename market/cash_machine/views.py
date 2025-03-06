import base64
import random
import io
import socket
from datetime import datetime

import pdfkit
import qrcode
from django.http import HttpResponse
from django.template import engines
from rest_framework.response import Response

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

    """ Путь сохранения PDF """
    pdf_out_path = f"media/{receipt_time[0:10] + '-' +receipt_time[11:16]+ '-' + str(random.randint(100,999))}"

    pdfkit.from_string(smg, pdf_out_path, options=options)

    """ Генерируем local ip """
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    """ Генерируем QR код """
    file_name = pdf_out_path.replace("media/", "")
    qr_url = f"http://{local_ip}:8000/media/{file_name}"

    qr = qrcode.make(qr_url)
    qr_image_io = io.BytesIO()
    qr.save(qr_image_io, format="PNG")
    qr_image_base64 = base64.b64encode(qr_image_io.getvalue()).decode()

    tm = env.get_template("qr.html")
    context_qr = {
        "qr": qr_image_base64,
    }
    rendered_template = tm.render(context=context_qr)
    return HttpResponse(rendered_template)


@api_view(["GET"])
def media_file_view(file_name):
    """
    Возвращает PDF чек по его имени из /media
    """
    file_path = f"media/{file_name}"
    try:
        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/pdf")
            return response
    except FileNotFoundError:
        return Response({"error": f"File {file_name} not found"}, status=404)
