from django.contrib import admin
from django.urls import path,include
from shop import views

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('product_page/', views.products_page, name='product_page'),
    path('', include('shop.urls')), 
]