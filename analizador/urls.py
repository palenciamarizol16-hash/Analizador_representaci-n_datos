from django.urls import path

from . import views

app_name = "analizador"

urlpatterns = [
    path("", views.index, name="index"),
    path("numero/", views.convertir_numero, name="numero"),
    path("texto/", views.analizar_texto, name="texto"),
]
