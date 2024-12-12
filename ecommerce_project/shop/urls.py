from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('products/', views.products_page, name='products'),
    path('cart/', views.cart_page, name='cart_page'),
    path('thankyou/', views.thank_you_page, name='thankyou'),
    #path('update_products/', views.update_products_page, name='update_products'),
    path('logout/', views.logout_user, name='logout'),
    path('products/?sort_by', views.sortby, name='sortby'),
    path('store-selection/', views.store_selection, name='store_selection'), 
    path('search/', views.search, name='search'),
    path('cart/delete/', views.delete_from_cart, name='delete_from_cart'),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    path('delete-from-cart/', views.delete_from_cart, name='delete_from_cart'),
    # path('display-selection/', views.display_selection, name='display_selection')
]
