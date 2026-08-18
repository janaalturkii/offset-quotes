from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('app/', views.dashboard, name='dashboard'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/pdf/', views.quote_pdf, name='quote_pdf'),
    path('quote/<int:quote_id>/edit/', views.quote_edit, name='quote_edit'),
    path('quote/<int:quote_id>/set-status/<str:new_status>/', views.quote_set_status, name='quote_set_status'),
    path('quote/<int:quote_id>/send-email/', views.quote_send_email, name='quote_send_email'),
    path('settings/vat/', views.vat_settings, name='vat_settings'),

    # API endpoints
    path('api/quotes/', api_views.QuoteListAPIView.as_view(), name='api_quote_list'),
    path('api/quotes/<int:pk>/', api_views.QuoteDetailAPIView.as_view(), name='api_quote_detail'),
    path('api/quotes/generate/', api_views.generate_quote_api, name='api_generate_quote'),
    path('api/quotes/<int:pk>/status/', api_views.update_quote_status_api, name='api_update_status'),
]