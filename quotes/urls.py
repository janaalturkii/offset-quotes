from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/pdf/', views.quote_pdf, name='quote_pdf'),
]