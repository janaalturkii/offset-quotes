from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Quote, QuoteLineItem
from .generator import generate_quote
from .pdf_export import generate_quote_pdf
from .models import VATSettings
from .vat_utils import calculate_totals

@login_required
def dashboard(request):
    if request.method == "POST":
        client_name = request.POST.get("client_name", "").strip()
        client_brief = request.POST.get("client_brief", "").strip()

        quote = Quote.objects.create(
            client_name=client_name,
            client_brief=client_brief,
            status='draft',
        )

        try:
            result = generate_quote(client_brief)

            summary = result.get("client_summary", "")
            notes = result.get("notes", "")
            line_items = result.get("line_items", [])

            quote_text_parts = [f"Summary: {summary}", ""]
            for item in line_items:
                QuoteLineItem.objects.create(
                    quote=quote,
                    description=item.get("description", ""),
                    category=item.get("category", ""),
                    estimated_price=item.get("estimated_price", 0),
                )
                quote_text_parts.append(
                    f"- {item.get('description')} ({item.get('category')}): {item.get('estimated_price')} SAR"
                )
            quote_text_parts.append(f"\nNotes: {notes}")

            quote.generated_quote_text = "\n".join(quote_text_parts)
            quote.save()

        except Exception as e:
            quote.generated_quote_text = f"Error generating quote: {e}"
            quote.save()

        return redirect("quote_detail", quote_id=quote.id)

    recent_quotes = Quote.objects.all()[:5]
    return render(request, "quotes/dashboard.html", {"recent_quotes": recent_quotes})

def landing(request):
    return render(request, "quotes/landing.html")

@login_required
def quote_list(request):
    quotes = Quote.objects.all()
    return render(request, "quotes/quote_list.html", {"quotes": quotes})


@login_required
def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    line_items = quote.line_items.all()
    totals = calculate_totals(line_items)
    return render(request, "quotes/quote_detail.html", {"quote": quote, "line_items": line_items, "totals": totals})


@login_required
def quote_pdf(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    line_items = quote.line_items.all()
    pdf_buffer = generate_quote_pdf(quote, line_items)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="offset-events-quote-{quote.id}.pdf"'
    return response


@login_required
def quote_edit(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    if request.method == "POST":
        quote.client_name = request.POST.get("client_name", quote.client_name).strip()
        quote.client_brief = request.POST.get("client_brief", quote.client_brief).strip()

        for item in quote.line_items.all():
            desc_key = f"description_{item.id}"
            cat_key = f"category_{item.id}"
            price_key = f"price_{item.id}"
            delete_key = f"delete_{item.id}"

            if delete_key in request.POST:
                item.delete()
                continue

            item.description = request.POST.get(desc_key, item.description)
            item.category = request.POST.get(cat_key, item.category)
            item.estimated_price = request.POST.get(price_key, item.estimated_price)
            item.save()

        new_desc = request.POST.get("new_description", "").strip()
        if new_desc:
            QuoteLineItem.objects.create(
                quote=quote,
                description=new_desc,
                category=request.POST.get("new_category", "").strip(),
                estimated_price=request.POST.get("new_price", 0) or 0,
            )

        if "finalize" in request.POST:
            quote.status = "finalized"
        else:
            quote.status = "revised"

        # Rebuild the generated_quote_text so it reflects the current, edited line items
        current_items = quote.line_items.all()
        totals = calculate_totals(current_items)
        text_parts = [f"Client: {quote.client_name}", f"Brief: {quote.client_brief}", ""]
        for item in current_items:
            text_parts.append(f"- {item.description} ({item.category}): {item.estimated_price} SAR")
        text_parts.append(f"\nSubtotal: {totals['subtotal']} SAR")
        if totals['vat_enabled']:
            text_parts.append(f"VAT ({totals['vat_rate']}%): {totals['vat_amount']} SAR")
        text_parts.append(f"Total: {totals['total']} SAR")

        quote.generated_quote_text = "\n".join(text_parts)
        quote.save()

        return redirect("quote_detail", quote_id=quote.id)

    line_items = quote.line_items.all()
    return render(request, "quotes/quote_edit.html", {"quote": quote, "line_items": line_items})

@login_required
def quote_set_status(request, quote_id, new_status):
    quote = get_object_or_404(Quote, id=quote_id)
    valid_statuses = [choice[0] for choice in Quote.STATUS_CHOICES]
    if new_status in valid_statuses:
        quote.status = new_status
        quote.save()
    return redirect(request.META.get('HTTP_REFERER', 'quote_list'))

@login_required
def vat_settings(request):
    settings_obj = VATSettings.get_settings()

    if request.method == "POST":
        settings_obj.vat_rate = request.POST.get("vat_rate", settings_obj.vat_rate)
        settings_obj.vat_enabled = "vat_enabled" in request.POST
        settings_obj.save()
        return redirect("vat_settings")

    return render(request, "quotes/vat_settings.html", {"settings": settings_obj})