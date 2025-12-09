"""
Session-based cart implementation for Electronic House.
"""
from decimal import Decimal
from django.conf import settings
from products.models import Product


class SessionCart:
    """
    A session-based shopping cart implementation.
    """
    
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'name': product.name,
            }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        # Update price in case it changed
        self.cart[product_id]['price'] = str(product.price)
        self.cart[product_id]['name'] = product.name
        
        self.save()
    
    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def save(self):
        """
        Mark the session as modified to make sure it gets saved.
        """
        self.session.modified = True
    
    def clear(self):
        """
        Remove the cart from the session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
    
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """
        Calculate the total cost of the cart.
        """
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )
    
    def get_item_count(self):
        """
        Get total number of items in cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_items_with_products(self):
        """
        Get cart items with full product objects.
        """
        product_ids = list(self.cart.keys())
        if not product_ids:
            return []
        
        products = {
            str(p.id): p 
            for p in Product.objects.filter(id__in=product_ids, is_active=True)
        }
        
        items = []
        for product_id, item_data in self.cart.items():
            product = products.get(product_id)
            if product:
                items.append({
                    'product': product,
                    'quantity': item_data['quantity'],
                    'price': product.price,
                    'total_price': product.price * item_data['quantity'],
                })
        
        return items
    
    def update_quantity(self, product_id, quantity):
        """
        Update the quantity of a specific product.
        """
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            self.save()
            return True
        return False
    
    def has_product(self, product_id):
        """
        Check if a product is in the cart.
        """
        return str(product_id) in self.cart
    
    def get_product_quantity(self, product_id):
        """
        Get the quantity of a specific product in the cart.
        """
        product_id = str(product_id)
        if product_id in self.cart:
            return self.cart[product_id]['quantity']
        return 0
