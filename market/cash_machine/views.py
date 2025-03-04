from datetime import datetime

from rest_framework.response import Response
from django.shortcuts import render
from rest_framework.decorators import api_view
from jinja2 import Template

from .models import Item
from .serializers import ItemSerializer


@api_view(['POST'])
def make_receipts(request):
    items_ids = request.data.get('items', [])
    items = []
    quantity = {}

    for item_id in items_ids:
        item = Item.objects.filter(id=item_id).first()
        if item:
            items.append(item)
            quantity[item.id] = quantity.get(item.id, 0) + 1

    serializer = ItemSerializer(items, many=True)

    if not serializer.data:
        return Response({'error': 'No items found'}, status=400)

    total_price = sum(float(item['price']) for item in serializer.data)
    receipt_time = datetime.now().strftime("%d-%m-%Y %H:%M")

    context = {
        'items': serializer.data,
        'total_price': total_price,
        'receipt_time': receipt_time,
        'quantity': quantity,
    }
    return render(request, 'receipt.html', context)