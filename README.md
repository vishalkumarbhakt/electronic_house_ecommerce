# Electronic House E-Commerce Platform

A complete Django 5.0 e-commerce platform for electronics, featuring a modern responsive frontend, comprehensive admin panel, and full e-commerce functionality.

## 🚀 Features

### Frontend
- 📱 **Mobile-First Design** - Optimized for 65%+ mobile traffic
- ⚡ **HTMX Integration** - Live search, AJAX cart updates, dynamic filtering
- 🎨 **Tailwind CSS** - Modern, responsive UI with custom theme
- 🔍 **Advanced Search & Filters** - Category, brand, price range, stock status

### E-Commerce
- 🛒 **Session-Based Cart** - Persistent cart with quantity management
- 💳 **Razorpay Integration** - UPI, Cards, Net Banking, Wallets
- 📦 **Order Management** - Complete order lifecycle tracking
- 🏷️ **Coupon System** - Percentage and fixed amount discounts
- 💰 **EMI Calculator** - No-cost and standard EMI options
- 📊 **Product Comparison** - Compare up to 4 products

### Admin Panel
- 📈 **Dashboard** - Revenue stats, order tracking, low stock alerts
- 📝 **Product Management** - JSON specs editor, bulk upload, image management
- 📦 **Order Processing** - Status updates, tracking, refunds
- 📊 **Reports** - Sales analytics, inventory valuation

### Technical
- 🔒 **Security** - CSRF protection, secure sessions, production hardening
- 🚀 **Performance** - WhiteNoise static files, caching ready
- 🐳 **Docker Ready** - Complete containerization with PostgreSQL, Redis
- 📧 **Email Ready** - Order confirmations, notifications

## 🛠️ Tech Stack

- **Backend**: Django 5.0, Python 3.12
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTMX, Alpine.js, Tailwind CSS (CDN)
- **Payment**: Razorpay, Stripe (configurable)
- **Cache**: Redis (optional)
- **Task Queue**: Celery (optional)
- **Server**: Gunicorn + Nginx

## 📋 Prerequisites

- Python 3.12+
- pip

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/vishalkumarbhakt/electronic_house_ecommerce.git
cd electronic_house_ecommerce
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables (optional)

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit http://localhost:8000 for the store and http://localhost:8000/admin for the admin panel.

## 📁 Project Structure

```
electronic_house_ecommerce/
├── electronic_house/      # Project settings
├── products/              # Product models, views, admin
├── orders/                # Order processing, checkout
├── cart/                  # Session-based cart
├── users/                 # User authentication
├── core/                  # API views, serializers
├── templates/             # Django templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploads
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── manage.py
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL URL | SQLite |
| `REDIS_URL` | Redis URL | Local memory cache |
| `RAZORPAY_KEY_ID` | Razorpay API key | - |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | - |
| `EMAIL_HOST` | SMTP server | Console backend |

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 📱 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/products/` | GET | List products |
| `/api/products/{slug}/` | GET | Product details |
| `/api/products/featured/` | GET | Featured products |
| `/api/categories/` | GET | List categories |
| `/api/cart/` | GET/POST/PUT/DELETE | Cart operations |

## 🔐 Admin Panel Features

- **Products**: Full CRUD with specs editor, image uploads, stock management
- **Orders**: Status updates, tracking, refunds, CSV export
- **Customers**: Customer profiles, order history
- **Coupons**: Create and manage discount codes
- **Categories & Brands**: Organize product catalog

## 🧪 Sample Data

After setup, you can add sample data through the admin panel:

1. Create categories: Mobiles, Laptops, Accessories, TVs, Appliances, Gaming
2. Add brands: Apple, Samsung, OnePlus, Dell, HP, etc.
3. Add products with specs, images, and pricing
4. Create sample orders to test the flow

## 📈 Production Deployment

### Railway/Heroku

1. Set environment variables in dashboard
2. Connect GitHub repository
3. Deploy

### Manual Server

```bash
# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn electronic_house.wsgi:application --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 📞 Support

For support, email support@electronichouse.in or create an issue on GitHub.