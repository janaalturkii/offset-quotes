from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Quote, QuoteLineItem
from .serializers import QuoteSerializer, QuoteCreateSerializer
from .generator import generate_quote


class QuoteListAPIView(generics.ListAPIView):
    """GET /api/quotes/ - list all quotes"""
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer


class QuoteDetailAPIView(generics.RetrieveAPIView):
    """GET /api/quotes/<id>/ - get one quote with its line items"""
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer


@api_view(['POST'])
def generate_quote_api(request):
    """
    POST /api/quotes/generate/
    Body: {"client_name": "...", "client_brief": "..."}
    Generates a new quote using Claude, saves it, and returns the full quote.
    """
    input_serializer = QuoteCreateSerializer(data=request.data)
    input_serializer.is_valid(raise_exception=True)

    client_name = input_serializer.validated_data.get('client_name', '')
    client_brief = input_serializer.validated_data['client_brief']

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
        quote.status = 'draft'
        quote.save()

    except Exception as e:
        quote.generated_quote_text = f"Error generating quote: {e}"
        quote.save()
        return Response(
            {"error": str(e), "quote_id": quote.id},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    serializer = QuoteSerializer(quote)
    return Response(serializer.data, status=status.HTTP_201_CREATED)