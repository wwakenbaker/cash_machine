from django.urls import path
from . import views

app_name = "cash_machine"

urlpatterns = [
    path("cash_machine/", views.make_receipts_view, name="make_recipes"),
    path("media/<str:file_name>", views.media_file_view, name="media-file"),
]
