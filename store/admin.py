from django.contrib import admin
from .models import Category, Book, UserProfile, Review, ViewedItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'format', 'stock')
    list_filter = ('category', 'format', 'language')
    search_fields = ('title', 'author', 'description')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(ViewedItem)
class ViewedItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'viewed_at')
    ordering = ('-viewed_at',)