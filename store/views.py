from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Course, Product, Cart, CartItem


def home(request):
    featured_courses = Course.objects.filter(is_active=True)[:6]
    featured_products = Product.objects.filter(is_active=True)[:6]
    
    context = {
        'featured_courses': featured_courses,
        'featured_products': featured_products,
    }
    return render(request, 'store/home.html', context)


def course_list(request):
    courses = Course.objects.filter(is_active=True)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__icontains=query)
        )
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
        'query': query,
        'difficulty': difficulty,
    }
    return render(request, 'store/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_active=True)
    lessons = course.lessons.all()
    
    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'store/course_detail.html', context)


def product_list(request):
    products = Product.objects.filter(is_active=True)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'query': query,
        'category': category,
        'categories': Product.CATEGORY_CHOICES,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    context = {
        'product': product,
    }
    return render(request, 'store/product_detail.html', context)


@login_required
def add_to_cart(request, item_type, item_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if item_type == 'course':
        course = get_object_or_404(Course, pk=item_id, is_active=True)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item_type='course',
            course=course,
            defaults={'quantity': 1}
        )
        if not created:
            messages.info(request, 'Course is already in your cart.')
        else:
            messages.success(request, f'{course.title} added to cart!')
            
    elif item_type == 'product':
        product = get_object_or_404(Product, pk=item_id, is_active=True)
        if not product.is_in_stock:
            messages.error(request, 'Product is out of stock.')
            return redirect('store:product_detail', pk=item_id)
            
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item_type='product',
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            if cart_item.quantity < product.stock_quantity:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f'{product.name} quantity updated in cart!')
            else:
                messages.error(request, 'Not enough stock available.')
        else:
            messages.success(request, f'{product.name} added to cart!')
    
    return redirect('store:cart')


@login_required
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart_items = []
        cart = None
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item_name = str(cart_item.get_item())
    cart_item.delete()
    messages.success(request, f'{item_name} removed from cart!')
    return redirect('store:cart')


@login_required
def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if cart_item.item_type == 'product':
            if quantity > cart_item.product.stock_quantity:
                messages.error(request, 'Not enough stock available.')
                return redirect('store:cart')
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated!')
    
    return redirect('store:cart')