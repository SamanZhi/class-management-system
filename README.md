# Class Management System

Django REST API برای مدیریت مدارس، ترم‌ها، کلاس‌ها، جلسات، گزارش جلسات و در ادامه محاسبه حقوق مربیان.

## وضعیت پروژه

**نسخه فعلی: پایان فاز ۳**

در این نسخه، فازهای ۱ تا ۳ پیاده‌سازی شده‌اند:

- فاز ۱: زیرساخت کاربران، نقش‌ها و احراز هویت JWT
- فاز ۲: مدیریت مدرسه، ترم، کلاس و تخصیص مربی
- فاز ۳: مدیریت جلسات و چرخه کامل گزارش جلسه

فاز ۴ شامل محاسبه حقوق مربیان در ادامه پروژه خواهد بود.

---

## فهرست مطالب

- [معرفی پروژه](#معرفی-پروژه)
- [نقش‌های سیستم](#نقشهای-سیستم)
- [قابلیت‌های پیاده‌سازی‌شده](#قابلیتهای-پیادهسازی‌شده)
- [ساختار پروژه](#ساختار-پروژه)
- [نصب و راه‌اندازی](#نصب-و-راهاندازی)
- [احراز هویت](#احراز-هویت)
- [API Endpoints](#api-endpoints)
- [چرخه گزارش جلسه](#چرخه-گزارش-جلسه)
- [تست‌ها](#تستها)
- [محدودیت‌ها و نکات](#محدودیتها-و-نکات)
- [تصمیمات فنی](#تصمیمات-فنی)
- [فازهای پروژه](#فازهای-پروژه)

---

## معرفی پروژه

این پروژه یک سیستم مدیریت آموزشی و گزارش‌دهی کلاس است که در آن:

1. مسئول آموزش مدرسه، ترم و کلاس را مدیریت می‌کند.
2. مربی به کلاس اختصاص داده می‌شود.
3. جلسات کلاس از قبل توسط مسئول آموزش ثبت می‌شوند.
4. مربی بعد از برگزاری جلسه گزارش آن را ثبت می‌کند.
5. مسئول آموزش گزارش را بررسی، تأیید یا رد می‌کند.
6. گزارش ردشده می‌تواند توسط همان مربی ویرایش و دوباره ارسال شود.
7. در فاز ۴، گزارش‌های تأییدشده مبنای محاسبه حقوق خواهند بود.

API با Django REST Framework پیاده‌سازی شده و احراز هویت با JWT انجام می‌شود.

---

## نقش‌های سیستم

سیستم سه نقش اصلی دارد:

- `teacher` — مربی
- `education_officer` — مسئول آموزش
- `finance_officer` — مسئول مالی

هر کاربر فقط یک نقش دارد و دسترسی endpointها بر اساس نقش کنترل می‌شود.

---

## قابلیت‌های پیاده‌سازی‌شده

### فاز ۱ — کاربران و احراز هویت

- Custom User Model بر پایه `AbstractUser`
- نقش‌های `teacher`، `education_officer` و `finance_officer`
- اطلاعات تماس مربی شامل شماره تماس و شماره تماس اضطراری
- احراز هویت JWT با `djangorestframework-simplejwt`
- endpoint برای مشاهده کاربر واردشده
- کنترل دسترسی مبتنی بر نقش
- management command برای ساخت کاربر:

```bash
python manage.py create_user --role=teacher
```

---

### فاز ۲ — مدرسه، ترم، کلاس و تخصیص مربی

مدل‌های اصلی فاز ۲ در اپ `education` قرار دارند:

- `School`
- `Term`
- `Course`
- `CourseTeacher`

قابلیت‌های اصلی:

- ایجاد، مشاهده و ویرایش مدرسه
- ایجاد و مدیریت ترم
- ارتباط کلاس با مدرسه و ترم
- تعیین مدت جلسه کلاس
- اختصاص مربی به کلاس با `start_date` و `end_date`
- پشتیبانی از چند مربی برای یک کلاس در بازه‌های زمانی مختلف
- جلوگیری از همپوشانی بازه‌های مسئولیت مربیان
- نمایش کلاس‌های مربوط به مربی
- Soft Delete برای مدل‌هایی که از `SoftDeleteModel` استفاده می‌کنند

---

### فاز ۳ — جلسات و گزارش جلسات

فاز ۳ در اپ `education` پیاده‌سازی شده و شامل دو مدل اصلی است:

#### `Session`

هر جلسه به یک کلاس (`Course`) متصل است و شامل:

- `session_number`
- `date`
- `course_obj`

قواعد اصلی:

- شماره جلسه برای هر کلاس یکتا است.
- برای یک کلاس، دو جلسه در یک تاریخ ثبت نمی‌شود.
- تاریخ جلسه باید داخل بازه ترم باشد.
- جلسات توسط مسئول آموزش ایجاد و مدیریت می‌شوند.
- جلسه آینده می‌تواند از قبل برنامه‌ریزی شود.
- حذف جلسه به صورت Soft Delete انجام می‌شود.

#### `SessionReport`

هر جلسه حداکثر یک گزارش دارد و شامل:

- `session`
- `teacher`
- `summary`
- `present_count`
- `absent_count`
- `status`
- `rejection_reason`
- `reviewed_by`
- `created_at`
- `updated_at`

وضعیت‌های گزارش:

- `pending`
- `approved`
- `rejected`

قواعد اصلی گزارش:

- فقط مربی می‌تواند گزارش ایجاد کند.
- مربی فقط برای کلاسی که در تاریخ جلسه مسئول آن بوده می‌تواند گزارش ثبت کند.
- ثبت گزارش برای جلسه آینده مجاز نیست.
- مربی نمی‌تواند گزارش مربی دیگر را مشاهده یا ویرایش کند.
- مسئول آموزش می‌تواند گزارش‌ها را مشاهده و بررسی کند.
- مسئول آموزش فقط وضعیت و توضیح بررسی را تغییر می‌دهد و محتوای گزارش را تغییر نمی‌دهد.
- مربی نمی‌تواند گزارش خودش را تأیید یا رد کند.
- رد کردن گزارش نیازمند `rejection_reason` است.
- گزارش تأییدشده قابل ویرایش نیست.
- گزارش ردشده توسط مربی قابل ویرایش و ارسال مجدد است.
- بعد از ارسال مجدد، وضعیت گزارش دوباره `pending` می‌شود.
- گزارش به صورت `OneToOne` به جلسه متصل است؛ بنابراین برای هر جلسه فقط یک گزارش وجود دارد.

### قاعده ۴۸ ساعت

ویژگی `is_late` در مدل `SessionReport` به صورت property محاسبه می‌شود.

مبنای محاسبه:

```text
session.date + 48 hours
```

اگر `updated_at` گزارش **بیشتر از** این زمان باشد:

```text
is_late = True
```

و اگر دقیقاً در مرز ۴۸ ساعت باشد:

```text
is_late = False
```

`updated_at` زمان آخرین ویرایش گزارش است؛ بنابراین در ویرایش و ارسال مجدد نیز وضعیت تأخیر بر اساس آخرین ویرایش دوباره محاسبه می‌شود.

---

## ساختار پروژه

```text
project_root/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   └── models.py
│       ├── BaseModel
│       ├── SoftDeleteModel
│       └── SoftDeleteManager
│
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── urls.py
│   ├── admin.py
│   ├── management/
│   │   └── commands/
│   │       └── create_user.py
│   └── tests/
│
├── education/
│   ├── models/
│   │   ├── school.py
│   │   ├── term.py
│   │   ├── course.py
│   │   ├── session.py
│   │   └── session_report.py
│   │
│   ├── serializers/
│   │   ├── school.py
│   │   ├── term.py
│   │   ├── course.py
│   │   ├── session.py
│   │   └── session_report.py
│   │
│   ├── views/
│   │   ├── school.py
│   │   ├── term.py
│   │   ├── course.py
│   │   ├── session.py
│   │   └── session_report.py
│   │
│   ├── migrations/
│   └── tests/
│       ├── school_tests/
│       ├── term_tests/
│       ├── course_tests/
│       ├── session_tests/
│       └── session_report_tests/
│
├── postman/
├── .postman/
├── manage.py
├── requirements.txt
├── db.sqlite3
└── README.md
```

---

## نصب و راه‌اندازی

### پیش‌نیاز

- Python 3.10+
- Django
- Django REST Framework
- djangorestframework-simplejwt
- drf-spectacular

### نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### اعمال migrationها

```bash
python manage.py makemigrations
python manage.py migrate
```

### ساخت کاربر

نمونه:

```bash
python manage.py create_user --role=teacher
```

نقش‌های معتبر:

```text
teacher
education_officer
finance_officer
```

### اجرای سرور

```bash
python manage.py runserver
```

در تنظیمات فعلی پروژه، دیتابیس توسعه `SQLite` است و فایل آن `db.sqlite3` است.

---

## احراز هویت

احراز هویت API با JWT انجام می‌شود.

### دریافت توکن

```http
POST /api/users/login/
```

### Refresh Token

```http
POST /api/users/token/refresh/
```

برای endpointهای محافظت‌شده باید access token را به صورت زیر ارسال کرد:

```http
Authorization: Bearer <access_token>
```

### کاربر فعلی

```http
GET /api/users/me/
```

### پروفایل

```http
GET /api/users/profile/
```

---

## API Endpoints

Base URL:

```text
/api/
```

### کاربران

| Method | Endpoint | توضیح |
|---|---|---|
| `POST` | `/api/users/login/` | دریافت JWT |
| `POST` | `/api/users/token/refresh/` | دریافت access token جدید |
| `GET` | `/api/users/me/` | اطلاعات کاربر واردشده |
| `GET` | `/api/users/profile/` | مشاهده پروفایل |
| `GET` | `/api/users/dashboard/teacher/` | داشبورد مربی |
| `GET` | `/api/users/dashboard/education-officer/` | داشبورد مسئول آموزش |
| `GET` | `/api/users/dashboard/finance-officer/` | داشبورد مسئول مالی |

### آموزش — مدرسه

| Method | Endpoint | توضیح |
|---|---|---|
| `GET` | `/api/education/schools/` | لیست مدارس |
| `POST` | `/api/education/schools/` | ایجاد مدرسه |
| `GET` | `/api/education/schools/<id>/` | جزئیات مدرسه |
| `PUT` | `/api/education/schools/<id>/` | ویرایش مدرسه |
| `DELETE` | `/api/education/schools/<id>/` | حذف نرم |

### آموزش — ترم

| Method | Endpoint | توضیح |
|---|---|---|
| `GET` | `/api/education/terms/` | لیست ترم‌ها |
| `POST` | `/api/education/terms/` | ایجاد ترم |
| `GET` | `/api/education/terms/<id>/` | جزئیات ترم |
| `PUT` | `/api/education/terms/<id>/` | ویرایش ترم |
| `DELETE` | `/api/education/terms/<id>/` | حذف نرم |

### آموزش — کلاس و مربی

| Method | Endpoint | توضیح |
|---|---|---|
| `GET` | `/api/education/courses/` | لیست کلاس‌ها |
| `POST` | `/api/education/courses/` | ایجاد کلاس |
| `GET` | `/api/education/courses/<id>/` | جزئیات کلاس |
| `PUT` | `/api/education/courses/<id>/` | ویرایش کلاس |
| `DELETE` | `/api/education/courses/<id>/` | حذف نرم |
| `GET` | `/api/education/courses/teachers/` | لیست تخصیص‌های مربی |
| `POST` | `/api/education/courses/teachers/` | تخصیص مربی |
| `GET` | `/api/education/courses/teachers/<id>/` | جزئیات تخصیص |
| `PUT` | `/api/education/courses/teachers/<id>/` | ویرایش تخصیص |
| `DELETE` | `/api/education/courses/teachers/<id>/` | حذف تخصیص |

### آموزش — جلسات

| Method | Endpoint | توضیح |
|---|---|---|
| `GET` | `/api/education/sessions/` | لیست جلسات |
| `POST` | `/api/education/sessions/` | ایجاد جلسه |
| `GET` | `/api/education/sessions/<id>/` | جزئیات جلسه |
| `PUT` | `/api/education/sessions/<id>/` | ویرایش جلسه |
| `DELETE` | `/api/education/sessions/<id>/` | حذف نرم جلسه |

مدیریت جلسات در نسخه فعلی فقط برای `education_officer` مجاز است.

### آموزش — گزارش جلسات

| Method | Endpoint | توضیح |
|---|---|---|
| `GET` | `/api/education/session-reports/` | لیست گزارش‌ها |
| `POST` | `/api/education/session-reports/` | ثبت گزارش توسط مربی |
| `GET` | `/api/education/session-reports/<id>/` | مشاهده گزارش |
| `PUT` | `/api/education/session-reports/<id>/` | ویرایش گزارش توسط مربی |
| `PATCH` | `/api/education/session-reports/<id>/review/` | تأیید یا رد توسط مسئول آموزش |

لیست گزارش‌ها برای مسئول آموزش امکان فیلتر بر اساس موارد زیر را دارد:

```text
school
course
teacher
start_date
end_date
```

مربی در لیست گزارش‌ها فقط گزارش‌های خودش را مشاهده می‌کند.

---

## چرخه گزارش جلسه

چرخه اصلی گزارش به صورت زیر است:

```text
Session
   │
   ▼
Teacher creates report
   │
   ▼
Pending
   │
   ├── Approve ──► Approved
   │                  │
   │                  └── Locked
   │
   └── Reject ──► Rejected
                       │
                       ▼
                 Teacher edits
                       │
                       ▼
                    Pending
```

قواعد مهم:

- گزارش آینده قابل ثبت نیست.
- فقط مربی مسئول کلاس در تاریخ جلسه می‌تواند گزارش را ثبت کند.
- گزارش تأییدشده قفل است.
- گزارش ردشده قابل ویرایش و ارسال مجدد است.
- مسئول آموزش نمی‌تواند محتوای گزارش را تغییر دهد.
- رد گزارش بدون دلیل مجاز نیست.
- مربی نمی‌تواند گزارش خودش را review کند.

---

## تست‌ها

نوشتن تست برای مدل‌ها، serializerها، viewها و قواعد اصلی کسب‌وکار در پروژه انجام شده است.

ساختار تست‌های فاز ۳:

```text
education/tests/
├── session_tests/
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_views.py
│
└── session_report_tests/
    ├── test_models.py
    ├── test_serializers.py
    └── test_views.py
```

### تست‌های Session

در مجموع **32 تست** برای Session نوشته شده است:

- 10 تست مدل
- 7 تست serializer
- 15 تست view

مواردی مانند:

- قرار داشتن تاریخ جلسه داخل ترم
- یکتا بودن شماره جلسه برای هر کلاس
- جلوگیری از دو جلسه در یک روز برای یک کلاس
- Soft Delete
- دسترسی نقش‌ها به endpointهای جلسه

### تست‌های SessionReport

در مجموع **38 تست** برای SessionReport نوشته شده است:

- 7 تست مدل
- 17 تست serializer
- 14 تست view

موارد مهم:

- ایجاد گزارش
- یک گزارش برای هر جلسه
- قاعده ۴۸ ساعت
- محاسبه مجدد `is_late` پس از تغییر `updated_at`
- جلوگیری از ثبت گزارش برای جلسه آینده
- بررسی مسئول بودن مربی در تاریخ جلسه
- محدودیت دسترسی مربی به گزارش‌های خودش
- تأیید و رد گزارش
- اجباری بودن دلیل رد
- جلوگیری از تغییر محتوای گزارش توسط مسئول آموزش
- قفل شدن گزارش تأییدشده
- ویرایش و ارسال مجدد گزارش ردشده
- تست چرخه کامل گزارش

### اجرای تست‌ها

اجرای کل تست‌ها:

```bash
python manage.py test
```

تست‌های Session:

```bash
python manage.py test education.tests.session_tests
```

تست‌های SessionReport:

```bash
python manage.py test education.tests.session_report_tests
```

---

## مستندات API

پروژه از `drf-spectacular` برای تولید مستندات OpenAPI استفاده می‌کند.

Schema:

```http
GET /api/schema/
```

Swagger UI:

```text
/api/docs/
```

ReDoc:

```text
/api/redoc/
```

---

## محدودیت‌ها و نکات

1. محاسبه حقوق در فاز ۳ پیاده‌سازی نشده و مربوط به فاز ۴ است.
2. در تنظیمات فعلی، SQLite برای محیط توسعه استفاده می‌شود.
3. رابط کاربری وب یا موبایل در Scope پروژه نیست و تمرکز روی API است.
4. گزارش تأییدشده قابل ویرایش یا حذف نیست.
5. گزارش ردشده برای ارسال مجدد محدودیت تعداد مشخصی ندارد.
6. SessionReport دارای Soft Delete نیست؛ حذف گزارش از چرخه API پشتیبانی نمی‌شود.
7. مدیریت جلسات در نسخه فعلی در اختیار مسئول آموزش است.
8. Postman در پروژه وجود دارد، اما اجرای اصلی سیستم وابسته به Postman نیست.

---

## تصمیمات فنی

### استفاده از اپلیکیشن `education`

به جای ساخت اپلیکیشن جداگانه برای مدرسه، ترم، کلاس، جلسه و گزارش، موجودیت‌های آموزشی در اپلیکیشن `education` نگهداری شده‌اند.

این ساختار باعث شده ارتباط بین:

```text
School
  ↓
Term
  ↓
Course
  ↓
Session
  ↓
SessionReport
```

در یک دامنه منطقی قرار بگیرد.

### استفاده از `SessionReport` به صورت OneToOne

برای هر جلسه فقط یک گزارش وجود دارد؛ بنابراین رابطه `OneToOne` بین `Session` و `SessionReport` استفاده شده است.

### محاسبه `is_late` به صورت property

`is_late` در دیتابیس ذخیره نمی‌شود و هر بار از روی `session.date` و `updated_at` محاسبه می‌شود. این کار باعث می‌شود پس از ویرایش و ارسال مجدد گزارش، وضعیت تأخیر بر اساس آخرین زمان ویرایش محاسبه شود.

### جداسازی تست‌ها

برای هر بخش، تست‌های مدل، serializer و view در فایل‌های جدا قرار گرفته‌اند:

```text
test_models.py
test_serializers.py
test_views.py
```

این ساختار خوانایی تست‌ها و نگهداری آن‌ها را ساده‌تر می‌کند.

---

## فازهای پروژه

- [x] **Phase 1** — زیرساخت کاربران، نقش‌ها و احراز هویت
- [x] **Phase 2** — مدیریت مدرسه، ترم، کلاس و تخصیص مربی
- [x] **Phase 3** — مدیریت جلسات و چرخه گزارش جلسه
- [ ] **Phase 4** — محاسبه حقوق، یکپارچه‌سازی نهایی و تکمیل پروژه

---

## وضعیت نهایی فاز ۳

**Current Version:** Phase 3  
**Status:** ✅ Phase 3 Completed

تمرکز فاز ۳ روی پیاده‌سازی و تست چرخه کامل گزارش جلسه بوده است:

```text
ثبت جلسه
   ↓
ثبت گزارش توسط مربی
   ↓
Pending
   ↓
Approve / Reject
   ↓
در صورت Reject:
ویرایش و ارسال مجدد
   ↓
Pending
   ↓
Approve
```

در پایان فاز ۳، منطق اصلی Session و SessionReport، کنترل دسترسی نقش‌ها، اعتبارسنجی‌ها، چرخه تأیید/رد و قاعده ۴۸ ساعت تحت تست قرار گرفته‌اند.
