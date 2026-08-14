# Class Management System

Django REST API for managing classes, session reports, and instructor payroll calculation.

# Teacher and Payroll Management System — Phase 2

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

> **وضعیت فعلی:** فاز ۲ — مدیریت مدارس، ترم‌ها، کلاس‌ها و تخصیص مربیان

---

## قابلیت‌های پیاده‌سازی‌شده

### ✅ فاز ۱: زیرساخت کاربری و احراز هویت
* **مدل کاربری سفارشی (Custom User Model):** ارث‌بری از `AbstractUser` همراه با فیلدهای نقش (`role`)، شماره تماس (`phone_number`) و شماره اضطراری (`emergency_number`).
* **احراز هویت JWT:** استفاده از `simplejwt` برای مدیریت نشست‌ها و توکن‌ها.
* **کنترل دسترسی مبتنی بر نقش (RBAC):** پیاده‌سازی پرمیشن‌های اختصاصی مانند `IsTeacher`، `IsEducationOfficer` و `IsFinanceOfficer`.

### ✅ فاز ۲: مدیریت مدارس، ترم‌ها و کلاس‌ها
* **اپلیکیشن مدارس (`schools`):**
  * ایجاد مدل `School` دارای فیلدهای `name` و `address`.
  * مدیریت مدارس فعال با استفاده از منطق Soft Delete.
* **اپلیکیشن ترم‌ها (`terms`):**
  * ایجاد مدل `Term` دارای فیلدهای `name`، `start_date` و `end_date` برای مشخص کردن بازه‌های آموزشی.
* **اپلیکیشن کلاس‌ها (`classes`):**
  * ایجاد مدل `Class` (شامل فیلدهای ارتباط با مدرسه و ترم جاری).
  * ایجاد مدل واسط `ClassTeacher` برای انتساب مربیان به کلاس‌ها همراه با نرخ پرداختی ساعتی (`hourly_rate`) و بازه زمانی فعالیت مربی (`start_date` و `end_date`).
* **منطق جلوگیری از همپوشانی زمانی مربیان (Overlap Validation):**
  * پیاده‌سازی متد `clean()` در سطح مدل و سریالایزر در `ClassTeacher` جهت جلوگیری از انتساب همزمان بیش از یک مربی به یک کلاس در بازه‌های زمانی متداخل (با در نظر گرفتن بازه‌های بدون تاریخ پایان یا `None`).

### 🗑️ زیرساخت Soft Delete
پیاده‌سازی متد اختصاصی حذف نرم در مدل پایه `SoftDeleteModel` در اپ `core`:
* فیلتر خودکار رکوردهای حذف‌نشده از طریق چرخه‌ی پیش‌فرض `objects` (با استفاده از `SoftDeleteManager`).
* دسترسی به تمام رکوردهای حذف‌شده و حذف‌نشده با استفاده از `all_objects`.
* پیاده‌سازی متد `soft_delete()` برای تغییر فیلد `is_deleted` به `True` و ثبت زمان حذف در `deleted_at` بدون حذف فیزیکی از دیتابیس.

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
├── core/                           # ابزارها و مدل‌های پایه مشترک
│   ├── models.py                   # SoftDeleteModel و SoftDeleteManager
│   └── views.py
│
├── users/                          # مدیریت کاربران و احراز هویت
│   ├── models.py                   # مدل User سفارشی
│   ├── serializers.py              # UserSerializer
│   ├── views.py                    # Login, Me endpoints
│   ├── permissions.py              # IsTeacher, IsEducationOfficer, ...
│   ├── admin.py                    # CustomUserAdmin
│   └── tests/
│       ├── test_models.py
│       ├── test_authentication.py
│       └── test_permissions.py
│
├── schools/                        # مدیریت مدارس (فاز ۲)
│   ├── models.py                   # مدل School (ارث‌بری از SoftDeleteModel)
│   ├── serializers.py              # SchoolSerializer
│   ├── views.py                    # SchoolListView, SchoolDetailView
│   ├── admin.py                    # مدیریت مدارس در پنل ادمین
│   └── tests/                      # تست‌های اختصاصی مدارس
│       ├── test_models.py
│       ├── test_serializers.py
│       └── test_views.py
│
├── terms/                          # مدیریت ترم‌ها (فاز ۲)
│   ├── models.py                   # مدل Term (ارث‌بری از SoftDeleteModel)
│   ├── serializers.py              # TermSerializer
│   ├── views.py                    # TermListView, TermDetailView
│   └── admin.py
│
├── classes/                        # مدیریت کلاس‌ها و مربیان (فاز ۲)
│   ├── models.py                   # مدل‌های Class و ClassTeacher
│   ├── serializers.py              # سریالایزرهای Class و ClassTeacher
│   ├── views.py                    # ClassListView, ClassDetailView, ClassTeacherView
│   ├── admin.py
│   └── tests/                      # تست‌های جامع همپوشانی و عملکرد
│       ├── test_models.py
│       ├── test_serializers.py
│       └── test_views.py
│
├── manage.py
├── requirements.txt
└── README.md

---

## نصب و راه‌اندازی

### پیش‌نیازها
* Python 3.10+
* Django 4.2+
* Django REST Framework 3.14+
* djangorestframework-simplejwt 5.3+

### مراحل نصب و راه‌اندازی مشابه فازهای قبلی است:
1. فعال‌سازی محیط مجازی و نصب وابستگی‌ها با `pip install -r requirements.txt`.
2. اعمال مهاجرت‌ها با دستورهای `python manage.py makemigrations` و `python manage.py migrate`.
3. راه‌اندازی سرور با `python manage.py runserver`.

---

## راهنمای استفاده و API Endpoints (فاز ۲)

تمامی مسیرهای فاز ۲ نیاز به احراز هویت JWT با نقش مناسب (مثلاً کارشناس آموزش یا `education_officer`) دارند.

| متد | مسیر (Endpoint) | توضیحات |
| :--- | :--- | :--- |
| `GET` | `/api/schools/` | لیست تمامی مدارس فعال |
| `POST` | `/api/schools/` | ثبت مدرسه جدید |
| `GET` | `/api/schools/<id>/` | جزئیات یک مدرسه خاص |
| `PUT` | `/api/schools/<id>/` | به‌روزرسانی کامل اطلاعات مدرسه |
| `DELETE` | `/api/schools/<id>/` | حذف نرم (Soft Delete) مدرسه |
| `GET` | `/api/terms/` | لیست ترم‌های ثبت‌شده |
| `POST` | `/api/terms/` | ثبت ترم جدید |
| `GET` | `/api/classes/` | لیست کلاس‌ها (با فیلترهای اختیاری `school` و `term`) |
| `POST` | `/api/classes/` | ایجاد کلاس جدید |
| `GET` | `/api/classes/<id>/` | جزئیات کلاس به همراه مشخصات مربی جاری (`current_teacher`) |
| `POST` | `/api/classes/<id>/teachers/` | انتساب یک مربی جدید به کلاس با رعایت عدم همپوشانی زمانی |

---

## تست‌ها

در فاز ۲، ساختار فایل‌های تست از حالت تک‌فایلی به ساختار ماژولار تفکیک شد و تست‌های واحد جامع در سطح مدل‌ها، سریالایزرها و ویوها پیاده‌سازی شدند.

### سناریوهای تستی پوشش داده‌شده:

#### ۱. تست‌های مدارس (`schools/tests/`)
* **تست‌های مدل:** بررسی صحت فیلدهای مدل `School` و اطمینان از عملکرد درست متد `soft_delete()` (تغییر وضعیت `is_deleted` به جای حذف فیزیکی).
* **تست‌های سریالایزر:** بررسی اعتبار سنجی ورودی‌ها و ساختار خروجی داده‌ها.
* **تست‌های API:** دسترسی‌سنجی متدهای `GET` ،`POST` و `DELETE` برای کاربران مهمان، مربیان و کارشناسان آموزش.

#### ۲. تست‌های کلاس و همپوشانی مربیان (`classes/tests/`)
* **تست اعتبارسنجی همپوشانی بازه‌های زمانی (Overlap Validation):**
  * سناریوی همپوشانی کامل دو بازه زمانی.
  * سناریوی ثبت بازه کاری جدید در شرایطی که بازه مربی قبلی فاقد تاریخ پایان (`end_date=None`) است.
  * صحت ثبت مربیان در بازه‌های زمانی متوالی بدون همپوشانی.
* **تست‌های API:** بررسی فیلتر کردن کلاس‌ها بر اساس ترم و مدرسه و دسترسی مربی جاری در خروجی سریالایزر کلاس.

### نحوه اجرای تست‌ها
برای اجرای کامل تست‌های سیستم:
bash
python manage.py test

---

## محدودیت‌ها و نکات (فاز ۲)

### ⚠️ نکات پیاده‌سازی
1. **عدم امکان حذف فیزیکی:** در اپلیکیشن‌های `schools` ،`terms` و `classes` امکان حذف دائمی (Hard Delete) از طریق وب‌سرویس وجود ندارد و حذف‌ها همگی به صورت سیستمی و از نوع Soft Delete هستند.
2. **مدیریت مربیان جاری:** متد `get_current_teacher` در سریالایزر کلاس، تاریخ جاری سرور را ملاک مقایسه با فیلدهای `start_date` و `end_date` در مدل واسط قرار می‌دهد تا مربی فعال را شناسایی و بازگرداند.
3. **عدم حذف مربیان:** بر اساس الزامات امنیتی و سیستمی، مدل کاربران (`User`) فاقد فیلد حذف نرم بوده و غیرقابل حذف تعریف شده است.

---

## تصمیمات فنی

### چرا تفکیک تست‌ها به ساختار دایرکتوری؟
با افزایش پیچیدگی پروژه در فاز ۲ و اضافه شدن منطق‌های اعتبارسنجی همپوشانی، تقسیم تست‌ها به فایل‌های اختصاصی `test_models.py`، `test_serializers.py` و `test_views.py` باعث خوانایی بهتر، نگهداری آسان‌تر و تفکیک وظایف تست‌ها گردید.

---

## فازهای بعدی

* [x] **Phase 1** — زیرساخت و احراز هویت
* [x] **Phase 2** — مدیریت مدارس، ترم‌ها، کلاس‌ها و تخصیص مربیان
* [ ] **Phase 3** — ثبت جلسات و سیستم تایید/رد گزارش‌ها
* [ ] **Phase 4** — محاسبه حقوق و پرداختی مربیان

---

## وضعیت پروژه

**Current Version:** Phase 2
**Status:** 🚧 In Development
