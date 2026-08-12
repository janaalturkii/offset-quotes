from rest_framework import serializers
from .models import Quote, QuoteLineItem


class QuoteLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteLineItem
        fields = ['id', 'description', 'category', 'estimated_price']


class QuoteSerializer(serializers.ModelSerializer):
    line_items = QuoteLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Quote
        fields = [
            'id', 'client_name', 'client_brief', 'generated_quote_text',
            'status', 'created_at', 'line_items'
        ]


class QuoteCreateSerializer(serializers.Serializer):
    """Used only for the 'generate a new quote' endpoint — just needs the raw brief."""
    client_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    client_brief = serializers.CharField()