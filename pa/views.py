from django.shortcuts import render
from django.http import HttpResponse
from . import forms
from django.views.generic.edit import FormView
from .analysis.main import process

# Create your views here.

class PhaseAnalysis(FormView):
    template_name = "pa/pa.html"
    form_class = forms.PhaseAnalysisForm

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        res = process(file)
        return HttpResponse(res, headers={
            "Content-Type": "application/excel",
            "Content-Disposition": 'attachment; filename="res.xlsx"'
        })