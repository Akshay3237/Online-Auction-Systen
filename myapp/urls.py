from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

urlpatterns = [
    # path('',views.home),
     path('', views.home, name='home'),
     path('home', views.home, name='home'),
     path('item/<int:item_id>/', views.item, name='item'),
     path('profile/', views.profile, name='profile'),
     path('my_auctions/', views.my_auctions, name='my_auctions'),
     path('create_auction/', views.create_auction, name='create_auction'),
     path('add_image/<int:auction_id>/', views.add_image, name='add_image'),
     path('handle_bid/<int:auction_id>/', views.handle_bid, name='handle_bid'),
     path('bid_history/', views.bid_history, name='bid_history'),
     path('edit_profile/', views.edit_profile, name='edit_profile'),
     path('auction/<int:pk>/', views.auction_detail, name='auction_detail'),
     path('see_more', views.see_more, name='see_more'),
     path('auction_reports', views.auction_reports, name='auction_reports'),
     path('search_products', views.search_products, name='search_products'),
    # path('item',views.item),
]