# 🛍️ PZAFIRA — RESTful API for Online Clothing Store

**PZAFIRA** is a fully-featured backend built with **Django** and **Django REST Framework**, designed to power a modern clothing store. It supports product management, user authentication, admin dashboard, shopping cart, order processing, reviews, wishlists, coupons, and more.

---

## 🚀 Features

- ✅ JWT Authentication with Email Verification (via Djoser & SimpleJWT)
- 👗 Product & Variant Management (size, color, images)
- 📦 Cart and Checkout system
- 💵 Order and Payment processing
- ✍️ Product Reviews and Ratings
- ❤️ Wishlist and Coupons
- 📬 Shipping Info Management
- 📄 Auto-generated API docs (Swagger)
- 🛡️ Secure token-based authentication


---

## 🛠️ Tech Stack

- **Backend:** Django 5.2, Django REST Framework
- **Auth:** JWT (SimpleJWT), Djoser
- **Database:** PostgreSQL
- **Docs:** drf-yasg (Swagger)
- **Others:** Django Filters, Decouple, Email notification.

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/AbirHasanPiash/pzafira-cloth-store
cd pzafira-cloth-store

# Create and activate virtual environment
python -m venv env
source env/bin/activate   # on Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (.env)
cp .env.example .env
# Edit .env and add your SECRET_KEY, DB credentials, and email config

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver


EMAIL_BACKEND=your.email.backend
EMAIL_HOST=smtp.yourhost.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=yourpassword
DEFAULT_FROM_EMAIL=your@email.com
```

## 🧑‍💻 Author

**[MD. ABIR HASAN PIASH](https://www.linkedin.com/in/a-h-piash/)**  
📧 [abirhasanpiash@gmail.com](mailto:abirhasanpiash@gmail.com)  
🔗 [GitHub Profile](https://github.com/AbirHasanPiash)

---

## 📄 License

This project is licensed under the **[MIT License](LICENSE)**.  
Feel free to use, modify, and distribute this project with proper attribution.
