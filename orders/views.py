from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from cart.cart import SessionCart
from .models import Customer, Order, OrderItem, Coupon
from products.models import Product
import json


def checkout(request):
    """Checkout view - Step 1: Shipping information."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    cart_items = cart.get_items_with_products()
    subtotal = cart.get_total_price()
    
    # Calculate shipping
    shipping_cost = 0 if subtotal >= 999 else 49
    total = subtotal + shipping_cost
    
    # Check for coupon in session
    coupon_discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid() and float(subtotal) >= float(coupon.min_order_amount):
                coupon_discount = coupon.calculate_discount(subtotal)
                total = subtotal + shipping_cost - coupon_discount
        except Coupon.DoesNotExist:
            del request.session['coupon_code']
    
    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_code,
        'total': total,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    })


@require_POST
def apply_coupon(request):
    """Apply a coupon code."""
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = SessionCart(request)
    subtotal = cart.get_total_price()
    
    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid():
            return JsonResponse({'success': False, 'error': 'Coupon has expired or is no longer valid.'})
        
        if float(subtotal) < float(coupon.min_order_amount):
            return JsonResponse({
                'success': False, 
                'error': f'Minimum order amount is ₹{coupon.min_order_amount}'
            })
        
        discount = coupon.calculate_discount(subtotal)
        request.session['coupon_code'] = code
        
        return JsonResponse({
            'success': True,
            'discount': discount,
            'message': f'Coupon applied! You save ₹{discount}'
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid coupon code.'})


@require_POST
def remove_coupon(request):
    """Remove applied coupon."""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    return JsonResponse({'success': True})


@require_POST
def create_order(request):
    """Create order and initiate payment."""
    cart = SessionCart(request)
    
    if len(cart) == 0:
        return JsonResponse({'success': False, 'error': 'Cart is empty'})
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    
    # Get or create customer
    customer, created = Customer.objects.get_or_create(
        email=data.get('email'),
        defaults={
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone': data.get('phone'),
            'address_line1': data.get('address_line1'),
            'address_line2': data.get('address_line2', ''),
            'city': data.get('city'),
            'state': data.get('state'),
            'pincode': data.get('pincode'),
        }
    )
    if request.user.is_authenticated:
        customer.user = request.user
        customer.save()
    
    # Calculate totals
    cart_items = cart.get_items_with_products()
    subtotal = cart.get_total_price()
    shipping_cost = 0 if subtotal >= 999 else 49
    
    # Apply coupon
    discount_amount = 0
    coupon_code = request.session.get('coupon_code', '')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount_amount = coupon.calculate_discount(subtotal)
                coupon.used_count += 1
                coupon.save()
        except Coupon.DoesNotExist:
            pass
    
    total = float(subtotal) + shipping_cost - discount_amount
    
    # Create order
    order = Order.objects.create(
        customer=customer,
        user=request.user if request.user.is_authenticated else None,
        billing_first_name=data.get('first_name'),
        billing_last_name=data.get('last_name'),
        billing_email=data.get('email'),
        billing_phone=data.get('phone'),
        billing_address=f"{data.get('address_line1')}, {data.get('address_line2', '')}".strip(', '),
        shipping_first_name=data.get('first_name'),
        shipping_last_name=data.get('last_name'),
        shipping_phone=data.get('phone'),
        shipping_address=f"{data.get('address_line1')}, {data.get('address_line2', '')}".strip(', '),
        shipping_city=data.get('city'),
        shipping_state=data.get('state'),
        shipping_pincode=data.get('pincode'),
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        total=total,
        payment_method=data.get('payment_method', 'razorpay'),
        coupon_code=coupon_code,
        customer_notes=data.get('notes', ''),
    )
    
    # Create order items
    for item in cart_items:
        product = item['product']
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            product_price=product.price,
            product_specs=product.specs,
            product_image=product.main_image.url if product.main_image else '',
            quantity=item['quantity'],
            total=item['total_price'],
            warranty_months=product.warranty_months,
        )
        
        # Update stock
        if product.track_inventory:
            product.stock -= item['quantity']
            product.save()
    
    # For COD, mark as confirmed
    if data.get('payment_method') == 'cod':
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()
        
        # Clear cart and coupon
        cart.clear()
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': f'/orders/success/{order.order_number}/'
        })
    
    # For online payment, create Razorpay order
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        razorpay_order = client.order.create({
            'amount': int(total * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order.order_number,
        })
        
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'order_number': order.order_number,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(total * 100),
            'currency': 'INR',
            'key': settings.RAZORPAY_KEY_ID,
        })
    
    # Fallback for no payment gateway configured
    return JsonResponse({
        'success': True,
        'order_number': order.order_number,
        'redirect_url': f'/orders/success/{order.order_number}/'
    })


@require_POST
def verify_payment(request):
    """Verify Razorpay payment."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    
    try:
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'})
    
    # Verify signature
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
        except razorpay.errors.SignatureVerificationError:
            order.payment_status = 'failed'
            order.save()
            return JsonResponse({'success': False, 'error': 'Payment verification failed'})
    
    # Update order
    order.razorpay_payment_id = razorpay_payment_id
    order.razorpay_signature = razorpay_signature
    order.payment_status = 'paid'
    order.payment_id = razorpay_payment_id
    order.status = 'confirmed'
    order.confirmed_at = timezone.now()
    order.save()
    
    # Clear cart and coupon
    cart = SessionCart(request)
    cart.clear()
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    
    return JsonResponse({
        'success': True,
        'redirect_url': f'/orders/success/{order.order_number}/'
    })


def order_success(request, order_number):
    """Order success/confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    
    return render(request, 'orders/success.html', {
        'order': order,
    })


def order_detail(request, order_number):
    """Order detail view."""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Simple auth check - user must be logged in and own the order
    # or have the order number (for guest checkout)
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
    })


def order_history(request):
    """Order history for logged in users."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to view your orders.')
        return redirect('users:login')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'orders/order_history.html', {
        'orders': orders,
    })
