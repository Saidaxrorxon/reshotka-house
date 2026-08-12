from django.contrib import admin
from django.utils.html import format_html

from .models import *


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "item_count")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Фото в категории")
    def item_count(self, category):
        return category.items.count()


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "uid", "category")
    list_filter = ("category",)

    @admin.display(description="Превью")
    def thumbnail(self, item):
        if not item.image:
            return ""
        return format_html(
            '<img src="{}" style="height:48px;width:auto;border-radius:4px;" />',
            item.image.url,
        )


admin.site.register(WorkCard)
admin.site.register(Catalog_card)
@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("name", "text")
    actions = ["approve_reviews"]

    @admin.action(description="Одобрить выбранные отзывы")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)