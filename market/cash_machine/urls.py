from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('cash_machine/', views.make_receipts, name='make_recipes'),
    ]