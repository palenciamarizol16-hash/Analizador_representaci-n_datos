from django import forms

from . import servicios

OPCIONES_BASE = [(2, "2 – Binario"), (8, "8 – Octal"), (10, "10 – Decimal"), (16, "16 – Hexadecimal")]


class NumeroForm(forms.Form):
    numero = forms.CharField(label="Número", required=False, widget=forms.TextInput(attrs={
        "autocomplete": "off", "spellcheck": "false", "placeholder": "Ej.: 255 o FF"}))
    base = forms.TypedChoiceField(label="Base de origen", choices=OPCIONES_BASE, coerce=int,
                                  initial=10, error_messages={
                                      "invalid_choice": "La base seleccionada no es válida. Elija 2, 8, 10 o 16.",
                                      "required": "Seleccione una base de origen."})

    def clean(self):
        datos = super().clean()
        if self.errors:
            return datos
        try:
            datos["resultado"] = servicios.convertir_numero(datos.get("numero", ""), datos["base"])
        except servicios.ErrorValidacion as exc:
            self.add_error("numero", str(exc))
        return datos


class TextoForm(forms.Form):
    texto = forms.CharField(label="Texto (máx. 20 caracteres)", required=False, strip=False,
                            widget=forms.TextInput(attrs={
                                "autocomplete": "off", "spellcheck": "false", "placeholder": "Ej.: año"}))

    def clean(self):
        datos = super().clean()
        try:
            datos["filas"] = servicios.analizar_texto(datos.get("texto", ""))
        except servicios.ErrorValidacion as exc:
            self.add_error("texto", str(exc))
        return datos
