"""
Management command to populate sample data for Electronic House.
"""
from django.core.management.base import BaseCommand
from products.models import Category, Brand, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate the database with sample electronics data'

    def handle(self, *args, **options):
        self.stdout.write('Creating categories...')
        
        # Create categories
        categories_data = [
            {'name': 'Mobiles', 'slug': 'mobiles', 'description': 'Latest smartphones from top brands', 'display_order': 1},
            {'name': 'Laptops', 'slug': 'laptops', 'description': 'Powerful laptops for work and gaming', 'display_order': 2},
            {'name': 'Accessories', 'slug': 'accessories', 'description': 'Earphones, chargers, cases and more', 'display_order': 3},
            {'name': 'TVs', 'slug': 'tvs', 'description': 'Smart TVs and LED displays', 'display_order': 4},
            {'name': 'Appliances', 'slug': 'appliances', 'description': 'Home appliances and gadgets', 'display_order': 5},
            {'name': 'Gaming', 'slug': 'gaming', 'description': 'Gaming consoles and accessories', 'display_order': 6},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'  Created category: {category.name}')
        
        self.stdout.write('Creating brands...')
        
        # Create brands
        brands_data = [
            {'name': 'Apple', 'slug': 'apple', 'is_featured': True},
            {'name': 'Samsung', 'slug': 'samsung', 'is_featured': True},
            {'name': 'OnePlus', 'slug': 'oneplus', 'is_featured': True},
            {'name': 'Dell', 'slug': 'dell', 'is_featured': True},
            {'name': 'HP', 'slug': 'hp'},
            {'name': 'Lenovo', 'slug': 'lenovo'},
            {'name': 'Sony', 'slug': 'sony', 'is_featured': True},
            {'name': 'LG', 'slug': 'lg'},
            {'name': 'Xiaomi', 'slug': 'xiaomi'},
            {'name': 'boAt', 'slug': 'boat'},
        ]
        
        brands = {}
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                slug=brand_data['slug'],
                defaults=brand_data
            )
            brands[brand_data['slug']] = brand
            if created:
                self.stdout.write(f'  Created brand: {brand.name}')
        
        self.stdout.write('Creating products...')
        
        # Create sample products
        products_data = [
            # Mobiles
            {
                'name': 'iPhone 15 Pro Max 256GB',
                'category': 'mobiles',
                'brand': 'apple',
                'price': Decimal('159900'),
                'compare_price': Decimal('179900'),
                'specs': {
                    'display': '6.7" Super Retina XDR',
                    'processor': 'A17 Pro',
                    'ram': '8GB',
                    'storage': '256GB',
                    'camera': '48MP + 12MP + 12MP',
                    'battery': '4422 mAh',
                    'os': 'iOS 17',
                },
                'stock': 25,
                'is_featured': True,
                'is_bestseller': True,
                'warranty_months': 12,
                'emi_available': True,
                'no_cost_emi': True,
            },
            {
                'name': 'Samsung Galaxy S24 Ultra 512GB',
                'category': 'mobiles',
                'brand': 'samsung',
                'price': Decimal('134999'),
                'compare_price': Decimal('149999'),
                'specs': {
                    'display': '6.8" Dynamic AMOLED 2X',
                    'processor': 'Snapdragon 8 Gen 3',
                    'ram': '12GB',
                    'storage': '512GB',
                    'camera': '200MP + 50MP + 12MP + 10MP',
                    'battery': '5000 mAh',
                    'os': 'Android 14',
                },
                'stock': 18,
                'is_featured': True,
                'warranty_months': 12,
                'emi_available': True,
            },
            {
                'name': 'OnePlus 12 256GB',
                'category': 'mobiles',
                'brand': 'oneplus',
                'price': Decimal('64999'),
                'compare_price': Decimal('69999'),
                'specs': {
                    'display': '6.82" LTPO AMOLED',
                    'processor': 'Snapdragon 8 Gen 3',
                    'ram': '12GB',
                    'storage': '256GB',
                    'camera': '50MP + 48MP + 64MP',
                    'battery': '5400 mAh',
                    'os': 'OxygenOS 14',
                },
                'stock': 30,
                'is_new_arrival': True,
                'warranty_months': 12,
                'emi_available': True,
            },
            # Laptops
            {
                'name': 'MacBook Pro 14" M3 Pro',
                'category': 'laptops',
                'brand': 'apple',
                'price': Decimal('199900'),
                'compare_price': Decimal('219900'),
                'specs': {
                    'display': '14.2" Liquid Retina XDR',
                    'processor': 'Apple M3 Pro',
                    'ram': '18GB',
                    'storage': '512GB SSD',
                    'graphics': 'Apple M3 Pro GPU',
                    'battery': '17 hours',
                    'os': 'macOS Sonoma',
                },
                'stock': 12,
                'is_featured': True,
                'is_bestseller': True,
                'warranty_months': 12,
                'emi_available': True,
                'no_cost_emi': True,
            },
            {
                'name': 'Dell XPS 15 i7 32GB',
                'category': 'laptops',
                'brand': 'dell',
                'price': Decimal('159990'),
                'specs': {
                    'display': '15.6" OLED 3.5K',
                    'processor': 'Intel Core i7-13700H',
                    'ram': '32GB DDR5',
                    'storage': '1TB SSD',
                    'graphics': 'NVIDIA RTX 4060',
                    'battery': '13 hours',
                    'os': 'Windows 11 Pro',
                },
                'stock': 8,
                'is_featured': True,
                'warranty_months': 24,
                'emi_available': True,
            },
            # Accessories
            {
                'name': 'AirPods Pro (2nd Gen)',
                'category': 'accessories',
                'brand': 'apple',
                'price': Decimal('24900'),
                'compare_price': Decimal('26900'),
                'specs': {
                    'type': 'True Wireless',
                    'driver': 'Custom Apple H2',
                    'anc': 'Active Noise Cancellation',
                    'battery': '6 hours',
                    'case_battery': '30 hours',
                },
                'stock': 50,
                'is_bestseller': True,
                'warranty_months': 12,
            },
            {
                'name': 'boAt Rockerz 550 Headphones',
                'category': 'accessories',
                'brand': 'boat',
                'price': Decimal('1799'),
                'compare_price': Decimal('2990'),
                'specs': {
                    'type': 'Over-Ear Wireless',
                    'driver': '50mm',
                    'battery': '20 hours',
                    'connectivity': 'Bluetooth 5.0',
                },
                'stock': 100,
                'is_new_arrival': True,
                'warranty_months': 12,
            },
            # TVs
            {
                'name': 'Sony Bravia 55" 4K OLED',
                'category': 'tvs',
                'brand': 'sony',
                'price': Decimal('129900'),
                'compare_price': Decimal('149900'),
                'specs': {
                    'screen_size': '55 inch',
                    'display': 'OLED',
                    'resolution': '4K Ultra HD',
                    'smart_tv': 'Google TV',
                    'hdmi': '4 ports',
                    'refresh_rate': '120Hz',
                },
                'stock': 6,
                'is_featured': True,
                'warranty_months': 24,
                'emi_available': True,
            },
            # Gaming
            {
                'name': 'PlayStation 5 Console',
                'category': 'gaming',
                'brand': 'sony',
                'price': Decimal('49990'),
                'specs': {
                    'storage': '825GB SSD',
                    'processor': 'AMD Zen 2',
                    'graphics': 'AMD RDNA 2',
                    'resolution': '4K 120fps',
                    'ray_tracing': 'Yes',
                },
                'stock': 15,
                'is_featured': True,
                'is_bestseller': True,
                'warranty_months': 12,
            },
        ]
        
        for prod_data in products_data:
            category_slug = prod_data.pop('category')
            brand_slug = prod_data.pop('brand')
            
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    **prod_data,
                    'category': categories[category_slug],
                    'brand': brands[brand_slug],
                    'description': f"Premium {prod_data['name']} from {brands[brand_slug].name}. " +
                                   "Experience top-notch quality and performance. " +
                                   "Comes with manufacturer warranty and Electronic House guarantee.",
                    'short_description': f"Latest {prod_data['name']} with amazing features and performance.",
                }
            )
            if created:
                self.stdout.write(f'  Created product: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   Categories: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Brands: {Brand.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Products: {Product.objects.count()}'))
