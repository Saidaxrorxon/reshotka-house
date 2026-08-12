from django.contrib import admin
from .models import *

admin.site.register(PortfolioCategory)
admin.site.register(PortfolioItem)
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