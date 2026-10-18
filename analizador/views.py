from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import NumeroForm, TextoForm


def _render(request, numero_form=None, texto_form=None):
    numero_form = numero_form or NumeroForm()
    texto_form = texto_form or TextoForm()
    contexto = {
        "numero_form": numero_form,
        "texto_form": texto_form,
        "resultado": numero_form.cleaned_data.get("resultado") if numero_form.is_bound and numero_form.is_valid() else None,
        "filas": texto_form.cleaned_data.get("filas") if texto_form.is_bound and texto_form.is_valid() else None,
    }
    return render(request, "analizador/index.html", contexto)


@require_http_methods(["GET"])
def index(request):
    return _render(request)


@require_http_methods(["POST"])
def convertir_numero(request):
    return _render(request, numero_form=NumeroForm(request.POST))


@require_http_methods(["POST"])
def analizar_texto(request):
    return _render(request, texto_form=TextoForm(request.POST))
