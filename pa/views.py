from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def main(request):
    return render(request, "pa/index.html")

def pa(request):
    return render(request, "pa/pa.html")