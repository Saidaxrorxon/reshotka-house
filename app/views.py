# app/views.py
from django.http import HttpResponse
from django.shortcuts import render ,redirect
from django.urls import reverse
from .forms import ConsultationRequestForm, ReviewForm
from .models import *

def home(request):
    categories = PortfolioCategory.objects.all().order_by("name")
    items = PortfolioItem.objects.select_related("category").all()
    work_cards = WorkCard.objects.all()
    reviews = Review.objects.filter(is_approved=True)

    form = ConsultationRequestForm()
    review_form = ReviewForm()

    if request.method == "POST":
        if request.POST.get("form_type") == "review":
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                return redirect(f"{request.path}?review=sent#reviews")
        else:
            form = ConsultationRequestForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(request.path)  # Перенаправляем обратно на главную

    return render(request, "index.html", {
        "categories": categories,
        "items": items,
        "work_cards": work_cards,
        "form": form,
        "review_form": review_form,
        "reviews": reviews,
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


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap_xml'))}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    urls = [
        request.build_absolute_uri(reverse(name))
        for name in ("home", "catalog", "projects", "contact")
    ]
    entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}"
        "</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")
