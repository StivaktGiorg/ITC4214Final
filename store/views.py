from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import JsonResponse , HttpResponseForbidden
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout,login,authenticate
from .forms import UserProfileForm
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_POST

from .models import Book, Category, Review, ViewedItem, WishlistItem, UserProfile, Product, Cart, CartItem
from .forms import ReviewForm, CustomUserRegistrationForm, BookForm
from decimal import Decimal



def home(request):
    featured_books = Book.objects.order_by('-created_at')[:8]
    return render(request, 'store/home.html', {'featured_books': featured_books})


def book_list(request):
    books = Book.objects.all()
    category_id = request.GET.get('category')
    format_filter = request.GET.get('format')
    language = request.GET.get('language')
    price_min = request.GET.get('min_price')
    price_max = request.GET.get('max_price')

    if category_id:
        books = books.filter(category_id=category_id)
    if format_filter:
        books = books.filter(format=format_filter)
    if language:
        books = books.filter(language__icontains=language)
    if price_min and price_max:
        books = books.filter(price__gte=price_min, price__lte=price_max)

    categories = Category.objects.filter(parent=None)
    return render(request, 'store/book_list.html', {'books': books, 'categories': categories})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.select_related('user').order_by('-created_at')

    review_form = None
    has_reviewed = False

    if request.user.is_authenticated:
        ViewedItem.objects.create(user=request.user, book=book)

        has_reviewed = Review.objects.filter(user=request.user, book=book).exists()

        if not has_reviewed:
            if request.method == 'POST':
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = request.user
                    review.book = book
                    review.save()
                    messages.success(request, "Your review has been submitted.")
                    return redirect('book_detail', pk=book.pk)
            else:
                review_form = ReviewForm()

    return render(request, 'store/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'review_form': review_form,
        'has_reviewed': has_reviewed,
    })

def search(request):
    query = request.GET.get('q')
    results = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    return render(request, 'store/search_results.html', {'results': results, 'query': query})


def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'store/profile.html', {'profile': profile})


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    books = Book.objects.all()
    return render(request, 'store/admin_dashboard.html', {'books': books})


@login_required
def dashboard(request):
    viewed_books = ViewedItem.objects.filter(user=request.user).order_by('-viewed_at')[:5]
    wishlist_items = WishlistItem.objects.filter(user=request.user)

    return render(request, 'store/dashboard.html', {
        'viewed_books': viewed_books,
        'wishlist_items': wishlist_items,
    })


@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    WishlistItem.objects.get_or_create(user=request.user, book=book)
    return redirect('book_detail', pk=book.id)

@login_required
def add_to_wishlist_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        book_id = data.get('book_id')
        book = get_object_or_404(Book, id=book_id)
        _, created = WishlistItem.objects.get_or_create(user=request.user, book=book)

        if created:
            return JsonResponse({'message': 'Book added to your wishlist!'})
        else:
            return JsonResponse({'message': 'Book is already in your wishlist.'})
        

@csrf_exempt
@login_required
def add_review_ajax(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            rating = data.get('rating')
            comment = data.get('comment')
            book_id = data.get('book_id')
        else:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            book_id = request.POST.get('book_id')

        print(f"Rating: {rating}, Comment: {comment}, Book ID: {book_id}")

        if not rating or not comment or not book_id:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return JsonResponse({"error": "Book not found"}, status=404)

        review, created = Review.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'rating': rating, 'comment': comment}
        )

        if not created:
            review.rating = rating
            review.comment = comment
            review.save()

        return JsonResponse({"message": "Review added successfully"})

    return JsonResponse({"error": "Invalid request method"}, status=400)
@login_required
def profile(request):
    return render(request, 'store/profile.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')  
    else:
        return HttpResponseForbidden("Invalid request method")
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def my_wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('book')
    return render(request, 'store/my_wishlist.html', {'wishlist_items': wishlist_items})


def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'store/edit_profile.html', {'form': form})


def dashboard(request):
    return render(request, 'store/dashboard.html')


def get_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key, is_active=True).first()

    if not cart:
        if request.user.is_authenticated:
            cart = Cart.objects.create(user=request.user, is_active=True)
        else:
            cart = Cart.objects.create(session_key=request.session.session_key, is_active=True)

    return cart



def create_product_for_book(book):
    if not hasattr(book, 'product'):
        Product.objects.create(
            name=f"Product for {book.title}",
            price=Decimal('19.99'),
            description=f"Default product for {book.title}",
            book=book
        )

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    product = get_object_or_404(Product, book=book)
    quantity = int(request.POST.get('quantity', 1))

    cart = get_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart_detail')


@login_required
def remove_from_cart(request, product_id):
    try:
        cart = Cart.objects.get(user=request.user, is_active=True)
        
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        
        cart_item.delete()

        return redirect('cart_detail')

    except Cart.DoesNotExist:
        return redirect('cart_detail')
    
    except CartItem.DoesNotExist:
        return redirect('cart_detail') 

@require_POST
@csrf_exempt 
@login_required
def update_cart(request, product_id, quantity=None):
    try:
        data = json.loads(request.body)
        quantity = data.get('quantity', quantity)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    cart = get_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.quantity = quantity
    cart_item.save()

    total = sum(item.total_price for item in cart.cartitem_set.all())

    return JsonResponse({'message': 'Quantity updated', 'total': float(total)})


@login_required
def cart_detail(request):
    cart = get_cart(request) 
    total = cart.total_price
    return render(request, 'store/cart_detail.html', {'cart': cart, 'total': total})


def book_list(request):
    books = Book.objects.all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')
    book_format = request.GET.get('format')

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    if category_id:
        books = books.filter(category_id=category_id)

    if book_format:
        books = books.filter(format=book_format)

    return render(request, 'store/book_list.html', {
        'books': books,
        'categories': categories
    })


@login_required
@user_passes_test(is_admin)
def add_book(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'store/book_form.html', {'form': form, 'title': 'Add Book'})


@login_required
@user_passes_test(is_admin)
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'store/book_form.html', {'form': form, 'title': 'Edit Book'})


@login_required
@user_passes_test(is_admin)
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('admin_dashboard')
    return render(request, 'store/confirm_delete.html', {'book': book})