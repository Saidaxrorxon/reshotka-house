# app/views.py
from django.shortcuts import render ,redirect
from .models import *

def home(request):
    categories = PortfolioCategory.objects.all().order_by("name")
    items = PortfolioItem.objects.select_related("category").all()
    work_cards = WorkCard.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        ConsultationRequest.objects.create(
            name=name,
            phone=phone,
            message=message
        )
        return redirect(request.path)  # Перенаправляем обратно на главную

    return render(request, "index.html", {
        "categories": categories,
        "items": items,
        "work_cards": work_cards
    })

def catalog(request):
    catalog_card = Catalog_card.objects.all()
    return render(request, "catalog.html", {
        "catalog_card": catalog_card
    })
    
    
    
def projects(request):
    categories = PortfolioCategory.objects.all().order_by("name")
    items = PortfolioItem.objects.select_related("category").all()
    return render(request, "projects.html", {
        "categories": categories,
        "items": items,
        
    })


def contact(request):
    return render(request, "contact.html")
