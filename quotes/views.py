from django.shortcuts import render, redirect, get_object_or_404
from .models import Quote, QuoteLineItem
from .generator import generate_quote
from django.http import HttpResponse
from .pdf_export import generate_quote_pdf

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


def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    line_items = quote.line_items.all()
    return render(request, "quotes/quote_detail.html", {"quote": quote, "line_items": line_items})


def quote_list(request):
    quotes = Quote.objects.all()
    return render(request, "quotes/quote_list.html", {"quotes": quotes})

def quote_pdf(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    line_items = quote.line_items.all()
    pdf_buffer = generate_quote_pdf(quote, line_items)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="offset-events-quote-{quote.id}.pdf"'
    return response

def quote_edit(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)

    if request.method == "POST":
        # Update existing line items
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

        # Add a new line item, if the "add new" fields were filled in
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

        quote.save()
        return redirect("quote_detail", quote_id=quote.id)

    line_items = quote.line_items.all()
    return render(request, "quotes/quote_edit.html", {"quote": quote, "line_items": line_items})