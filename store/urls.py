from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import add_review_ajax



urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('search/', views.search, name='search'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('ajax/add-to-wishlist/', views.add_to_wishlist_ajax, name='add_to_wishlist_ajax'),
    path('ajax/add-review/', add_review_ajax, name='add_review_ajax'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/<int:quantity>/', views.update_cart, name='update_cart'),
    path('cart/', views.cart_detail, name='cart_detail'), 
    path('admin-panel/add-book/', views.add_book, name='add_book'),
    path('admin-panel/edit-book/<int:pk>/', views.edit_book, name='edit_book'),
    path('admin-panel/delete-book/<int:pk>/', views.delete_book, name='delete_book'),
    
]
