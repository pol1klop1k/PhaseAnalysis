from django import forms

class PhaseAnalysisForm(forms.Form):

    file = forms.FileField(label="Загрузите файл", widget=forms.widgets.FileInput(attrs={"id": "fileInput"}))