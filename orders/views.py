from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from store.models import Cart
from .models import Order, OrderItem


@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('store:cart')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_price=cart.total_price
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                item_type=cart_item.item_type,
                course=cart_item.course,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.get_item_price()
            )
            
            # Update product stock if it's a product
            if cart_item.item_type == 'product' and cart_item.product:
                product = cart_item.product
                product.stock_quantity -= cart_item.quantity
                product.save()
        
        # Clear cart
        cart.delete()
        
        messages.success(request, f'Order #{order.id} created successfully!')
        return redirect('orders:payment_instructions', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def payment_instructions(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'bank_account': settings.BANK_ACCOUNT_NUMBER,
        'bank_name': settings.BANK_NAME,
        'bank_instructions': settings.BANK_INSTRUCTIONS,
    }
    return render(request, 'orders/payment_instructions.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)