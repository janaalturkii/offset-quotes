from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/pdf/', views.quote_pdf, name='quote_pdf'),
]

from . import views, api_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/pdf/', views.quote_pdf, name='quote_pdf'),

    # API endpoints
    path('api/quotes/', api_views.QuoteListAPIView.as_view(), name='api_quote_list'),
    path('api/quotes/<int:pk>/', api_views.QuoteDetailAPIView.as_view(), name='api_quote_detail'),
    path('api/quotes/generate/', api_views.generate_quote_api, name='api_generate_quote'),
]