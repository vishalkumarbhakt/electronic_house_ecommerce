"""
Cart context processor to make cart available in all templates.
"""
from .cart import SessionCart


def cart_context(request):
    """
    Add cart to the template context.
    """
    return {
        'cart': SessionCart(request)
    }
