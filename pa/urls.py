from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main),
    path('PhaseAnalysis/', views.pa, name="pa")
]