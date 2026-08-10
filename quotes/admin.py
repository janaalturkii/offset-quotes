from django.contrib import admin
from .models import Quote, QuoteLineItem


class QuoteLineItemInline(admin.TabularInline):
    model = QuoteLineItem
    extra = 0


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'status', 'created_at']
    list_filter = ['status']
    inlines = [QuoteLineItemInline]


@admin.register(QuoteLineItem)
class QuoteLineItemAdmin(admin.ModelAdmin):
    list_display = ['quote', 'description', 'category', 'estimated_price']