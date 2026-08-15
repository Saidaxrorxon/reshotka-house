# app/views.py
from django.http import HttpResponse
from django.shortcuts import render ,redirect
from django.urls import reverse
from .forms import ConsultationRequestForm, ReviewForm
from .models import *

# Short blurb shown in the hero slider for each portfolio category.
CATEGORY_HERO_TEXT = {
    "grilles": "Производим металлические решётки, заборы и ограждения любой сложности для частных домов, офисов и предприятий в Ташкенте.",
    "gates": "Надёжные металлические ворота и калитки под заказ — современный дизайн, качественная сварка и установка под ключ.",
    "canopies": "Изготавливаем прочные и стильные навесы в Ташкенте — для дома, двора, парковки и коммерческих объектов.",
    "railings": "Кованые перила и ограждения — надёжность и эстетика для лестниц, балконов и террас.",
    "fences": "Заборы из металла любой сложности — прочные, стильные, с установкой под ключ.",
    "hangars": "Каркасные ангары — быстровозводимые металлоконструкции под ключ для складов и производств.",
}

# Presentable stock photos for the hero slider (Pexels, free for commercial
# use, no attribution required) — used instead of the raw uploaded portfolio
# photos, which are real project shots but not always camera-ready for the
# homepage hero. Welder-at-work shots, to match "изготовление металлоконструкций".
CATEGORY_HERO_IMAGES = {
    "grilles": "https://images.pexels.com/photos/29976478/pexels-photo-29976478.jpeg?auto=compress&cs=tinysrgb&w=1600",
    "gates": "https://images.pexels.com/photos/2760343/pexels-photo-2760343.jpeg?auto=compress&cs=tinysrgb&w=1600",
    "canopies": "https://images.pexels.com/photos/1098402/pexels-photo-1098402.jpeg?auto=compress&cs=tinysrgb&w=1600",
    "railings": "https://images.pexels.com/photos/29976478/pexels-photo-29976478.jpeg?auto=compress&cs=tinysrgb&w=1600",
    "fences": "https://images.pexels.com/photos/2760343/pexels-photo-2760343.jpeg?auto=compress&cs=tinysrgb&w=1600",
    "hangars": "https://images.pexels.com/photos/1098402/pexels-photo-1098402.jpeg?auto=compress&cs=tinysrgb&w=1600",
}


def home(request):
    reviews = Review.objects.filter(is_approved=True)
    hero_slides = [
        {
            "title": item.category.name,
            "text": CATEGORY_HERO_TEXT.get(item.category.slug, ""),
            "image": CATEGORY_HERO_IMAGES.get(item.category.slug, item.image.url),
        }
        for item in PortfolioItem.objects.select_related("category").order_by("-uid")[:3]
    ]

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
        "form": form,
        "review_form": review_form,
        "reviews": reviews,
        "hero_slides": hero_slides,
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
        for name in ("home", "projects", "contact")
    ]
    entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{entries}"
        "</urlset>"
    )
    return HttpResponse(xml, content_type="application/xml")
