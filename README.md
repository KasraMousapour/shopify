# 🛍️ Shopify — Full-Stack E-Commerce Platform

یک پروژه کامل فروشگاه اینترنتی مدرن و مقیاس‌پذیر، تلفیقی از فرانت‌اند پیشرفته **[Vercel Shop (Next.js)](https://github.com/vercel/shop)** و بک‌اند پرسرعت و قدرتمند **[FastAPI Full-Stack Template](https://github.com/fastapi/full-stack-fastapi-template)** به همراه پنل مدیریت **Vite + React**.

---

## 🏗️ ساختار پروژه (Monorepo Architecture)

```text
shopify/
├── storefront/             # فرانت‌ند فروشگاه (Next.js App Router, Tailwind CSS, Vercel Shop)
│   ├── app/                # صفحات App Router
│   ├── components/         # کامپوننت‌های رابط کاربری
│   ├── lib/                # کلاینت داده و اتصال به FastAPI
│   └── Dockerfile          # کانتینر اجرای استورفرانت
│
├── backend/                # سرویس بک‌اند (FastAPI, SQLModel, PostgreSQL, Alembic)
│   ├── app/
│   │   ├── api/routes/     # اندپوینت‌های REST (محصولات، دسته‌ها، سبد خرید، سفارشات)
│   │   ├── core/           # تنظیمات، پایگاه داده و احراز هویت JWT
│   │   ├── models.py       # مدل‌های داده E-Commerce و کاربران
│   │   └── initial_data.py # سید اولیه محصولات و دسته‌بندی‌ها
│   └── Dockerfile          # کانتینر اجرای بک‌اند FastAPI
│
├── admin/                  # پنل مدیریت فروشگاه (Vite, React, Tailwind CSS)
│   ├── src/                # صفحات و کامپوننت‌های مدیریت محصولات و کاربران
│   └── Dockerfile          # کانتینر اجرای پنل ادمین
│
├── docker-compose.yml      # ارکستراسیون کل سرویس‌ها با یک دستور
├── .env.example            # نمونه متغیرهای محیطی
└── package.json            # اسکریپت‌های مدیریت مونو-ریپو
```

---

## ✨ ویژگی‌های کلیدی (Features)

- **Storefront (ویترین فروشگاه)**:
  - طراحی مینیمال، مدرن و ریسپانسیو با **Next.js App Router** و **Tailwind CSS**.
  - پشتیبانی کامل از دسته‌بندی‌ها (Collections)، فیلتر قیمت، مرتب‌سازی و جستجوی پیشرفته.
  - سبد خرید تعاملی (Interactive Drawer Cart) با محاسبه لحظه‌ای قیمت.
  - سئو بهینه و رندر سریع (Server-Side Rendering / Static Generation).

- **Backend (هسته بک‌اند FastAPI)**:
  - معماری تمیز و پرسرعت مبتنی بر **FastAPI** و **SQLModel** (ترکیب Pydantic و SQLAlchemy).
  - احراز هویت امن با توکن **OAuth2 JWT**.
  - مدل‌های جامع فروشگاهی: `Products`, `ProductVariants`, `Collections`, `Cart`, `CartItem`, `Orders`.
  - ایجاد خودکار جداول و سید دیتابیس با محصولات تستی واقع‌گرایانه در شروع کار.
  - مستندات خودکار و تعاملی Swagger در آدرس `/docs`.

- **Admin Dashboard (پنل مدیریت)**:
  - داشبورد مدیریتی سریع با **Vite** و **React**.
  - مدیریت محصولات، دسته‌ها، سفارشات و کاربران سیستم.

- **DevOps & Containerization**:
  - آماده‌سازی کامل با **Docker** و **Docker Compose** برای اجرای فوری در محیط توسعه یا پروداکشن.

---

## 🚀 راهنمای اجرای سریع با داکر (Docker Quickstart)

ساده‌ترین روش برای اجرای کل پشته نرم‌افزاری (دیتابیس، بک‌اند، فرانت‌ند و پنل ادمین):

1. **کپی فایل متغیرهای محیطی:**
   ```bash
   cp .env.example .env
   ```

2. **اجرای سرویس‌ها با Docker Compose:**
   ```bash
   docker compose up --build
   ```

3. **دسترسی به سرویس‌ها:**
   - 🛒 **Storefront (فروشگاه):** [http://localhost:3000](http://localhost:3000)
   - ⚙️ **FastAPI Backend & API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - 📊 **Admin Dashboard (پنل ادمین):** [http://localhost:5173](http://localhost:5173)

> **اطلاعات ادمین پیش‌فرض:**
> - ایمیل: `admin@shopify.local`
> - رمز عبور: `adminpassword123`

---

## 💻 راهنمای اجرای محلی بدون داکر (Local Development)

### ۱. اجرای بک‌اند (FastAPI)
```bash
cd backend
python -m venv .venv
# ویندوز:
.venv\Scripts\activate
# لینوکس/مک:
source .venv/bin/activate

pip install -r pyproject.toml
python -m app.initial_data
uvicorn app.main:app --reload --port 8000
```

### ۲. اجرای فروشگاه (Next.js Storefront)
```bash
cd storefront
npm install --legacy-peer-deps
npm run dev
```

### ۳. اجرای پنل مدیریت (Admin)
```bash
cd admin
npm install --legacy-peer-deps
npm run dev
```

---

## 📡 آدرس اندپوینت‌های اصلی API (FastAPI REST Endpoints)

| متد | آدرس اندپوینت | توضیحات |
| :--- | :--- | :--- |
| `GET` | `/api/v1/products/` | دریافت لیست محصولات (با فیلتر دسته، جستجو و مرتب‌سازی) |
| `GET` | `/api/v1/products/{handle}` | دریافت مشخصات یک محصول بر اساس اسلاگ |
| `POST` | `/api/v1/products/` | افزودن محصول جدید (ویژه ادمین) |
| `GET` | `/api/v1/collections/` | دریافت لیست دسته‌بندی‌ها |
| `POST` | `/api/v1/cart/` | ایجاد سبد خرید جدید |
| `GET` | `/api/v1/cart/{cart_id}` | دریافت اطلاعات و آیتم‌های سبد خرید |
| `POST` | `/api/v1/cart/{cart_id}/lines` | افزودن کالا یا تنوع محصول به سبد |
| `POST` | `/api/v1/orders/checkout` | ثبت سفارش و پرداخت سبد خرید |

---

## 🐙 نحوه انتشار و اتصال به گیت‌هاب (Push to GitHub)

برای انتشار این پروژه در حساب گیت‌هاب خود به نام **shopify**:

1. در گیت‌هاب یک ریپازیتوری جدید به نام `shopify` ایجاد کنید:
   [https://github.com/new](https://github.com/new)

2. دستورات زیر را در پوشه ریشه پروژه اجرا کنید:
   ```bash
   git remote add origin https://github.com/KasraMousapour/shopify.git
   git branch -M main
   git push -u origin main
   ```
   *(در صورت استفاده از کلید SSH: `git remote add origin git@github.com:KasraMousapour/shopify.git`)*

---

## 📄 لایسنس
پروژه تحت لایسنس MIT منتشر شده است.
