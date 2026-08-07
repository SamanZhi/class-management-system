# Class Management System

Django REST API for managing classes, session reports, and instructor payroll calculation.

# Teacher and Payroll Management System — Phase 1

---

## 📋 فهرست مطالب

* [معرفی پروژه](#معرفی-پروژه)
* [قابلیت‌های پیاده‌سازی‌شده](#قابلیتهای-پیادهسازی‌شده)
* [ساختار پروژه](#ساختار-پروژه)
* [نصب و راه‌اندازی](#نصب-و-راهاندازی)
* [راهنمای استفاده](#راهنمای-استفاده)
* [API Endpoints](#api-endpoints)
* [تست‌ها](#تستها)
* [محدودیت‌ها و نکات](#محدودیتها-و-نکات)
* [تصمیمات فنی](#تصمیمات-فنی)
* [فازهای بعدی](#فازهای-بعدی)

---

## معرفی پروژه

این پروژه یک سیستم مدیریت مربیان و حقوق است که در چهار فاز توسعه می‌یابد.

اهداف اصلی پروژه عبارت‌اند از:

* مدیریت کاربران با نقش‌های مختلف:

  * مربی (`teacher`)
  * کارشناس آموزش (`education_officer`)
  * کارشناس مالی (`finance_officer`)
* ثبت و مدیریت جلسات کلاسی
* تأیید و رد گزارش‌های جلسات
* محاسبه و پردازش حقوق مربیان

> **وضعیت فعلی:** فاز ۱ — زیرساخت و احراز هویت

---

## قابلیت‌های پیاده‌سازی‌شده

### ✅ مدل کاربری سفارشی (Custom User Model)

* ارث‌بری از `AbstractUser` جنگو
* سه نقش اصلی:

  * `teacher`
  * `education_officer`
  * `finance_officer`
* فیلدهای اضافی همراه با اعتبارسنجی:

  * `phone_number`: شماره تماس با فرمت `+98xxxxxxxxxx`
  * `emergency_number`: شماره اضطراری

### 🔐 سیستم احراز هویت

* احراز هویت مبتنی بر JWT با استفاده از `djangorestframework-simplejwt`
* Endpoint ورود برای دریافت Access و Refresh Token
* Endpoint اطلاعات کاربر جاری:

  * `/api/auth/me/`
* کنترل دسترسی مبتنی بر نقش (RBAC)

### 👥 مدیریت کاربران

* Management Command برای ایجاد کاربران جدید
* پنل ادمین سفارشی‌سازی‌شده جنگو
* اعتبارسنجی خودکار داده‌ها
* هش کردن امن رمز عبور

### 📚 مدل‌های پایه

مدل‌های موردنیاز فازهای آینده در اپ‌های جداگانه ایجاد شده‌اند:

* **schools**

  * مدل `School`
* **terms**

  * مدل `Term`
* **classes**

  * مدل‌های `Class` و `ClassTeacher`

### 🗑️ Soft Delete

زیرساخت اولیه Soft Delete پیاده‌سازی شده است:

* کلاس پایه `SoftDeleteModel` برای حذف منطقی
* Manager سفارشی برای فیلتر خودکار
* استفاده از `is_active` برای مدیریت وضعیت کاربران

---

## ساختار پروژه

```text
project_root/
│
├── config/                         # تنظیمات پروژه
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/                          # مدیریت کاربران و احراز هویت
│   ├── models.py                   # مدل User سفارشی
│   ├── serializers.py              # UserSerializer
│   ├── views.py                    # Login, Me endpoints
│   ├── permissions.py              # IsTeacher, IsEducationOfficer, ...
│   ├── admin.py                    # CustomUserAdmin
│   │
│   ├── management/
│   │   └── commands/
│   │       └── create_user.py
│   │
│   └── tests/
│       ├── test_models.py
│       ├── test_auth.py
│       └── test_permissions.py
│
├── schools/                        # مدیریت مدارس
│   └── models.py
│
├── terms/                          # مدیریت ترم‌ها
│   └── models.py
│
├── classes/                        # مدیریت کلاس‌ها
│   └── models.py
│
├── core/                           # ابزارهای مشترک
│   └── models.py                   # SoftDeleteModel
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## نصب و راه‌اندازی

### پیش‌نیازها

* Python 3.10+
* Django 4.2+
* Django REST Framework 3.14+
* djangorestframework-simplejwt 5.3+

### مراحل نصب

#### 1. کلون کردن مخزن

```bash
git clone <repository-url>
cd <project-directory>
```

#### 2. ایجاد محیط مجازی

**Linux / macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

#### 3. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

#### 4. اجرای Migrationها

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. ایجاد Superuser — اختیاری

```bash
python manage.py createsuperuser
```

#### 6. ایجاد کاربران نمونه

**مربی:**

```bash
python manage.py create_user \
    --username teacher1 \
    --password Test1234 \
    --role teacher \
    --phone +989123456789 \
    --emergency +989121111111
```

**کارشناس آموزش:**

```bash
python manage.py create_user \
    --username edu_officer \
    --password Test1234 \
    --role education_officer \
    --phone +989123456788 \
    --emergency +989122222222
```

**کارشناس مالی:**

```bash
python manage.py create_user \
    --username finance_officer \
    --password Test1234 \
    --role finance_officer \
    --phone +989123456787 \
    --emergency +989123333333
```

> در Windows می‌توانید دستورها را در یک خط اجرا کنید یا از روش مناسب خط‌شکنی PowerShell استفاده کنید.

#### 7. اجرای سرور

```bash
python manage.py runserver
```

سرور در آدرس زیر در دسترس خواهد بود:

`http://127.0.0.1:8000/`

---

## راهنمای استفاده

### ورود به سیستم (Login)

#### درخواست

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
    "username": "teacher1",
    "password": "Test1234"
}
```

#### پاسخ موفق

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### دریافت اطلاعات کاربر جاری

#### درخواست

```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

#### پاسخ

```json
{
    "id": 3,
    "username": "teacher1",
    "role": "teacher",
    "phone_number": "+989123456789"
}
```

---

### تازه‌سازی Access Token

#### درخواست

```http
POST /api/auth/token/refresh/
Content-Type: application/json
```

```json
{
    "refresh": "<refresh_token>"
}
```

---

## API Endpoints

| Method | Endpoint                   | توضیحات                   | نیاز به احراز هویت |
| ------ | -------------------------- | ------------------------- | ------------------ |
| `POST` | `/api/auth/login/`         | ورود و دریافت JWT Token   | ❌                  |
| `GET`  | `/api/auth/me/`            | دریافت اطلاعات کاربر جاری | ✅                  |
| `POST` | `/api/auth/token/refresh/` | تازه‌سازی Access Token    | ✅ (Refresh Token)  |

---

## تست‌ها

### اجرای تمام تست‌ها

```bash
python manage.py test
```

### اجرای تست‌های یک اپ خاص

```bash
python manage.py test users
```

### اجرای یک فایل تست خاص

```bash
python manage.py test users.tests.test_models
```

### اجرای یک تست خاص

```bash
python manage.py test users.tests.test_models.UserModelTestCase.test_create_user_with_valid_role
```

### نمایش خروجی مفصل

```bash
python manage.py test --verbosity=2
```

### پوشش تست‌ها

#### مدل User

* ✅ ایجاد کاربران با نقش‌های مختلف
* ✅ رد کردن نقش‌های نامعتبر
* ✅ بررسی یکتایی نام کاربری
* ✅ اعتبارسنجی فرمت شماره تلفن
* ✅ هش کردن رمز عبور

#### احراز هویت

* ✅ ورود موفق با اطلاعات صحیح
* ✅ رد کردن ورود با اطلاعات نادرست
* ✅ دریافت JWT Token
* ✅ محافظت Endpoint با JWT

#### کنترل دسترسی

* ✅ بررسی مجوزها بر اساس نقش
* ✅ رد دسترسی برای نقش‌های غیرمجاز

---

## محدودیت‌ها و نکات

### ⚠️ محدودیت‌های شناخته‌شده

#### 1. Soft Delete ناقص

زیرساخت Soft Delete آماده است، اما منطق تجاری آن به‌صورت کامل پیاده‌سازی نشده است.

* بررسی وابستگی‌ها هنوز پیاده‌سازی نشده
* قابلیت بازیابی (Restore) هنوز پیاده‌سازی نشده

#### 2. عدم وجود قابلیت فراموشی رمز عبور

سیستم بازیابی رمز عبور در حال حاضر وجود ندارد.

#### 3. عدم ثبت‌نام عمومی

طبق الزامات پروژه، کاربران فقط از طریق پنل ادمین یا Management Command ایجاد می‌شوند.

#### 4. مدل‌های پایه فاقد منطق تجاری

مدل‌های `School`، `Term` و `Class` صرفاً برای آماده‌سازی فازهای بعدی ایجاد شده‌اند.

#### 5. محدودیت Unique Together

مدل `ClassTeacher` در حال حاضر به محدودیت `Unique Together` نیاز ندارد و این محدودیت در فازهای آینده اضافه خواهد شد.

---

## ✨ نکات امنیتی

* تمامی رمزهای عبور با الگوریتم `PBKDF2` هش می‌شوند.
* JWT Tokenها دارای زمان انقضا هستند.
* شماره تلفن‌ها قبل از ذخیره اعتبارسنجی می‌شوند.
* نقش کاربر از `request.user` استخراج می‌شود، نه از بدنه درخواست.
* کاربران بدون مجوز مناسب نمی‌توانند به Endpointهای محافظت‌شده دسترسی داشته باشند.

---

## تصمیمات فنی

### چرا JWT؟

#### مزایا

* ✅ Stateless بودن → مقیاس‌پذیری بهتر
* ✅ مناسب برای معماری API-first
* ✅ قابل استفاده در اپلیکیشن‌های موبایل و SPA
* ✅ کنترل دقیق زمان انقضا

#### معایب

* ❌ عدم امکان باطل کردن Token قبل از انقضا به‌صورت پیش‌فرض

  * راه‌حل احتمالی: استفاده از Blacklist
* ❌ حجم بیشتر نسبت به Session ID

---

### چرا اپ‌های جداگانه؟

دلایل اصلی جداسازی پروژه به اپ‌های مستقل:

* **Separation of Concerns:** هر اپ مسئولیت مشخصی دارد.
* **Reusability:** امکان استفاده مجدد از اپ‌ها در پروژه‌های دیگر.
* **Maintainability:** توسعه و نگهداری آسان‌تر.
* **Testability:** امکان تست مستقل هر بخش.

---

### چرا Custom User Model از ابتدا؟

تغییر مدل User در میانه پروژه می‌تواند بسیار پیچیده باشد. بنابراین، تعریف Custom User Model از ابتدای پروژه باعث می‌شود:

* ✅ انعطاف‌پذیری کامل برای اضافه کردن فیلدهای جدید
* ✅ جلوگیری از Migrationهای پیچیده در آینده
* ✅ پیروی از Best Practiceهای Django

---

## فازهای بعدی

این پروژه در چهار فاز توسعه خواهد یافت.

### Phase 1 — زیرساخت و احراز هویت

* [x] Custom User Model
* [x] JWT Authentication
* [x] Role-Based Access Control
* [x] User Management
* [x] Basic Soft Delete Infrastructure

### Phase 2 — مدیریت مدارس، ترم‌ها و کلاس‌ها

* [ ] مدیریت مدارس
* [ ] مدیریت ترم‌ها
* [ ] ایجاد و مدیریت کلاس‌ها
* [ ] اختصاص مربیان به کلاس‌ها

### Phase 3 — مدیریت جلسات

* [ ] ثبت جلسات
* [ ] ثبت گزارش جلسات
* [ ] تأیید و رد گزارش‌ها
* [ ] مدیریت وضعیت جلسات

### Phase 4 — محاسبه حقوق مربیان

* [ ] محاسبه ساعات تدریس
* [ ] محاسبه حقوق
* [ ] تأیید پرداخت‌ها
* [ ] گزارش‌های مالی

---

## وضعیت پروژه

**Current Version:** Phase 1
**Status:** 🚧 In Development

---
