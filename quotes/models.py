from django.db import models


class Quote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
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

    def __str__(self):
        return f"{self.description} - {self.estimated_price} SAR"