from django.contrib import admin
from .models import *

admin.site.register(PortfolioCategory)
admin.site.register(PortfolioItem)
admin.site.register(WorkCard)
admin.site.register(Catalog_card)
@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "created_at")