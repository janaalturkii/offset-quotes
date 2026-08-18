from decimal import Decimal
from .models import VATSettings


def calculate_totals(line_items):
    """
    Given a list/queryset of QuoteLineItem objects, returns a dict with
    subtotal, vat_rate, vat_amount, and total - respecting whether VAT
    is currently enabled in settings.
    """
    settings_obj = VATSettings.get_settings()
    subtotal = sum((item.estimated_price for item in line_items), Decimal('0'))

    if settings_obj.vat_enabled:
        vat_rate = settings_obj.vat_rate
        vat_amount = (subtotal * vat_rate / Decimal('100')).quantize(Decimal('0.01'))
    else:
        vat_rate = Decimal('0')
        vat_amount = Decimal('0')

    total = subtotal + vat_amount

    return {
        'subtotal': subtotal,
        'vat_rate': vat_rate,
        'vat_amount': vat_amount,
        'total': total,
        'vat_enabled': settings_obj.vat_enabled,
    }