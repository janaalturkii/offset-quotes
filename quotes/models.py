from django.db import models


class Quote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('revised', 'Revised'),
        ('finalized', 'Finalized'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    client_name = models.CharField(max_length=200, blank=True)
    client_brief = models.TextField(help_text="The raw client message describing what they need")
    generated_quote_text = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Quote for {self.client_name or 'Unnamed client'} ({self.status})"


class QuoteLineItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=300)
    category = models.CharField(max_length=100, blank=True)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class VATSettings(models.Model):
    """
    Singleton-style model: only one row should ever exist.
    Holds the VAT rate and whether VAT is currently applied to quotes.
    """
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, help_text="VAT rate as a percentage, e.g. 15.00 for 15%")
    vat_enabled = models.BooleanField(default=True, help_text="If off, quotes are generated and shown without VAT")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VAT: {self.vat_rate}% ({'enabled' if self.vat_enabled else 'disabled'})"

    @classmethod
    def get_settings(cls):
        """Always returns the single settings row, creating it with defaults if it doesn't exist yet."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return f"{self.description} - {self.estimated_price} SAR"

   