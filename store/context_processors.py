from .models import Cart


def cart_counter(request):
    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.total_items
        except Cart.DoesNotExist:
            pass
    
    return {'cart_items_count': cart_items_count}