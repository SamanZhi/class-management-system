# Class Management System

Django REST API for managing classes, session reports, and instructor payroll calculation.

This project is the final project of **Maktab 141 Python Bootcamp** and is being developed in multiple phases.

---

## Project Overview

The system is designed for an educational company that manages classes in different schools.

The main roles in the system are:

* **Teacher** — teaches classes and submits session reports.
* **Education Officer** — manages schools, terms, classes, teacher-class assignments, and reviews session reports.
* **Finance Officer** — manages payroll rates and calculates monthly teacher salaries.

The project is implemented as an API using Django and Django REST Framework.

---

## Current Progress

| Phase   | Description                      | Status      |
| ------- | -------------------------------- | ----------- |
| Phase 0 | Requirements Q&A                 | Completed   |
| Phase 1 | System Foundation, Users & Roles | Completed   |
| Phase 2 | School, Term & Class Management  | Completed   |
| Phase 3 | Session Reports                  | Not started |
| Phase 4 | Payroll & Final Integration      | Not started |

---

# Phase 1 — System Foundation, Users & Roles

## What Was Built

The following functionality was implemented during Phase 1:

* User management with three system roles:

  * Teacher
  * Education Officer
  * Finance Officer
* Role-based access control.
* JWT authentication.
* Login functionality.
* An endpoint for checking the currently authenticated user and their role.
* Teacher-specific information such as:

  * Name
  * Contact phone
  * Emergency contact
* Basic data models required for the following concepts:

  * School
  * Term
  * Class
* Management command for creating users with a specific role.
* API structure for the project.
* Tests for models, serializers, and views.

The system does not provide public user registration. Users are created by the system administrator through the management command.

---

# Phase 2 — School, Term & Class Management

## What Was Built

Phase 2 focuses on building the educational structure of the system and connecting teachers to classes.

### School Management

Education Officers can:

* Create schools.
* Update schools.
* View a list of schools.
* View school details.

### Term Management

The system supports academic terms with:

* Start date.
* End date.
* Term type:

  * Normal
  * Summer

Terms cannot overlap.

### Class Management

Education Officers can create and manage classes connected to:

* A school.
* A term.
* A teacher through a separate teacher-class relationship.

Each class has a session duration, which can only be one of:

* 60 minutes
* 90 minutes
* 120 minutes

Invalid session durations are rejected by validation.

### Teacher-Class Assignment

A teacher can be assigned to a class with:

* Assignment start date.
* Optional assignment end date.

A class can have multiple teachers during its lifetime, as long as their assignment periods do not overlap.

Teachers can view only the classes assigned to them, including their current and previous classes.

### Phase 2 Tests

Tests were added for the Phase 2 components, including:

* Model tests.
* Serializer tests.
* View/API tests.
* Validation rules.
* Teacher-class assignment rules.
* Role-based access restrictions.

---

# Project Structure

```text
class-management-system/
│
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── school/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── term/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── course/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```

> The exact directory structure may change as new phases are implemented.

---

# Requirements

Before running the project, make sure you have:

* Python 3.x
* PostgreSQL
* pip
* Git

---

# Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd class-management-system
```

## 2. Create a virtual environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root and configure the required environment variables.

Example:

```env
DEBUG=True

SECRET_KEY=your-secret-key

DB_NAME=your_database
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

Do not commit real credentials or secret keys to the repository.

---

# Database Setup

After configuring PostgreSQL and the environment variables, run:

```bash
python manage.py migrate
```

---

# Creating Users

The project does not have public user registration.

Users can be created using the Django management command.

Example:

```bash
python manage.py create_user --role=teacher
```

Other supported roles:

```text
teacher
education_officer
finance_officer
```

The exact required arguments depend on the implementation of the management command.

---

# Running the Project

Start the Django development server:

```bash
python manage.py runserver
```

The API will then be available at:

```text
http://127.0.0.1:8000/
```

---

# Running Tests

Run the complete test suite with:

```bash
python manage.py test
```

To run tests for a specific application:

```bash
python manage.py test <app_name>
```

For example:

```bash
python manage.py test school
```

Tests cover the main business rules and role-based access boundaries required by the project.

---

# Authentication

The API uses **JWT authentication**.

A user must authenticate before accessing protected endpoints.

The authenticated user's role determines which resources and operations are available to them.

The three supported roles are:

```text
Teacher
Education Officer
Finance Officer
```

---

# Main Business Rules Implemented So Far

## Roles

Each user has one system role.

A user must not be able to access operations belonging to another role.

---

## Terms

* A term has a start date and an end date.
* Terms must not overlap.
* A term has a type:

  * Normal
  * Summer

---

## Classes

* A class belongs to a school and a term.
* A class has a session duration.
* Valid session durations are only:

  * 60 minutes
  * 90 minutes
  * 120 minutes
* A class must belong to its term's date range.

---

## Teacher-Class Relationships

Teacher assignments contain a start date and an optional end date.

Multiple teachers can teach the same class during different periods.

Teacher assignment periods must not overlap.

A teacher can access their own current and previous classes but not classes belonging to other teachers.

---

# Known Limitations & Design Shortcuts

The following limitations or simplifications are intentional at the current stage of the project:

* The project currently covers only Phase 1 and Phase 2 requirements.
* Session reporting has not been implemented yet.
* Payroll calculation has not been implemented yet.
* No frontend/web UI is included. The project is API-based.
* Public user registration is not supported.
* The project uses the simplified three-role system defined by the project requirements.
* Features outside the project scope, such as students, parent accounts, notifications, support tickets, and temporary substitute teachers, are not implemented.
* Some optional features from later phases are intentionally postponed.
* The API and data model may change in future phases as new requirements are implemented.

---

# API Testing

The API can be tested using tools such as:

* Postman
* Django REST Framework browsable API
* Any HTTP client

The project does not require a separate frontend application.

---

# Development Workflow

The project is developed phase by phase.

The main branches are:

```text
main
dev
```

The `dev` branch is used for development.

Completed phases are merged into `main` and tagged with the corresponding phase tag.

Example:

```text
phase-1
phase-2
phase-3
phase-4
```

The current completed version is tagged as:

```text
phase-2
```

---

# Future Phases

## Phase 3 — Session Reports

Planned functionality includes:

* Session management.
* Session reports.
* Teacher report submission.
* 48-hour submission rule.
* Report approval/rejection.
* Report editing and resubmission.
* Education Officer review.

---

## Phase 4 — Payroll & Final Integration

Planned functionality includes:

* Teacher payroll rates.
* Monthly payroll calculation.
* Different session durations.
* Summer-term coefficient.
* Late report handling.
* Payroll history.
* Full end-to-end system testing.

---

# Project Requirements Reference

The official project requirements define four technical phases after the initial Q&A phase.

The first two completed phases focus on:

1. System foundation, users, roles and authentication.
2. School, term, class and teacher-class management.

Testing is mandatory throughout the project, especially for model behavior, role-based access boundaries, and the main business rules of each phase.

---

# License

This project was developed as part of the **Maktab 141 Python Bootcamp Final Project**.
