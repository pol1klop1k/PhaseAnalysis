from django.urls import path, include
from . import views

app_name = "pa"

urlpatterns = [
    path('', views.PhaseAnalysis.as_view(), name="pa"),
]