# Finance Dashboard API

A role-based finance records and analytics backend built with **Django REST Framework**.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.12 | Readable, strong ecosystem |
| Framework | Django 6 + DRF | Battle-tested, batteries-included |
| Auth | JWT (SimpleJWT) | Stateless, standard |
| Database | SQLite (default) / PostgreSQL | SQLite for zero-config dev; swap via `DATABASE_URL` |
| Filtering | django-filter | Clean, declarative |
| Docs | drf-spectacular (Swagger) | Auto-generated from code |

---

## Quick Start

```bash
# 1. Clone and install
git clone <repo>
cd finance_dashboard
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Seed demo users + records
python seed.py

# 4. Start server
python manage.py runserver
```

Swagger UI → http://localhost:8000/api/docs/

---

## Demo Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@finance.dev | Admin@1234 |
| Analyst | analyst@finance.dev | Analyst@1234 |
| Viewer | viewer@finance.dev | Viewer@1234 |

---

## Project Structure

```
finance_dashboard/
├── core/
│   ├── settings.py        # Project config
│   ├── urls.py            # Root URL routing
│   └── exceptions.py      # Uniform error envelope
├── users/
│   ├── models.py          # Custom User with Role enum
│   ├── permissions.py     # IsAdmin, IsAnalystOrAdmin, IsActiveUser
│   ├── serializers.py     # Register, UserUpdate, ChangePassword
│   ├── views.py           # Auth, Me, UserViewSet (admin)
│   └── urls.py
├── records/
│   ├── models.py          # FinancialRecord (soft delete, indexes)
│   ├── serializers.py     # Full + light list serializer
│   ├── filters.py         # Date range, amount range, type, category
│   ├── services.py        # Analytics aggregation (summary, trends, categories)
│   ├── views.py           # RecordViewSet + 5 dashboard views
│   └── urls.py
├── seed.py                # Demo data
└── requirements.txt
```

---

## Role-Based Access Control

| Action | Viewer | Analyst | Admin |
|---|:---:|:---:|:---:|
| List / retrieve records | ✅ | ✅ | ✅ |
| Recent activity | ✅ | ✅ | ✅ |
| Dashboard summary | ❌ | ✅ | ✅ |
| Category totals | ❌ | ✅ | ✅ |
| Monthly / weekly trends | ❌ | ✅ | ✅ |
| Create record | ❌ | ❌ | ✅ |
| Update / delete record | ❌ | ❌ | ✅ |
| Restore soft-deleted | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

Permissions are enforced via **permission classes** on each view/viewset action — not inline `if` checks.

---

## API Reference

### Auth

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | Public | Register (always Viewer) |
| POST | `/api/auth/login/` | Public | Get JWT tokens |
| POST | `/api/auth/token/refresh/` | Public | Refresh access token |
| GET/PATCH | `/api/auth/me/` | Any auth | Own profile |
| PUT | `/api/auth/me/change-password/` | Any auth | Change own password |

### User Management (Admin only)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/auth/users/` | List all users |
| POST | `/api/auth/users/` | Create user with any role |
| GET/PUT/PATCH | `/api/auth/users/{id}/` | View / update user |
| PATCH | `/api/auth/users/{id}/toggle-status/` | Activate / deactivate |
| PATCH | `/api/auth/users/{id}/set-role/` | Change role |

### Financial Records

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/records/` | All | List with filters + pagination |
| POST | `/api/records/` | Admin | Create record |
| GET | `/api/records/{id}/` | All | Retrieve single |
| PUT/PATCH | `/api/records/{id}/` | Admin | Update |
| DELETE | `/api/records/{id}/` | Admin | Soft delete |
| POST | `/api/records/{id}/restore/` | Admin | Restore soft-deleted |
| GET | `/api/records/deleted/` | Admin | List soft-deleted |

**Filters** (query params):

| Param | Example | Description |
|---|---|---|
| `record_type` | `income` / `expense` | Filter by type |
| `category` | `salary`, `food`, `rent`… | Filter by category |
| `date_from` | `2026-01-01` | Date ≥ |
| `date_to` | `2026-03-31` | Date ≤ |
| `amount_min` | `1000` | Amount ≥ |
| `amount_max` | `50000` | Amount ≤ |
| `search` | `bonus` | Search description / category |
| `ordering` | `-date`, `amount` | Sort field |
| `page` | `2` | Pagination |

### Dashboard (Analyst + Admin)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/summary/` | Total income, expense, net balance |
| GET | `/api/dashboard/categories/` | Breakdown by category + type |
| GET | `/api/dashboard/trends/monthly/?months=6` | Monthly income vs expense |
| GET | `/api/dashboard/trends/weekly/?weeks=8` | Weekly income vs expense |
| GET | `/api/dashboard/recent/?limit=10` | Recent records (all auth users) |

---

## Data Model

### User
```
id, email (unique), full_name, role (viewer/analyst/admin),
is_active, is_staff, date_joined
```

### FinancialRecord
```
id, created_by (FK User), amount (Decimal 14,2),
record_type (income/expense), category (11 choices),
date, description, is_deleted, deleted_at,
created_at, updated_at
```

Categories: `salary`, `freelance`, `investment`, `food`, `transport`,
`utilities`, `healthcare`, `entertainment`, `education`, `rent`, `other`

---

## Error Responses

All errors follow a uniform envelope:

```json
{
  "success": false,
  "status_code": 403,
  "errors": {
    "detail": "Admin access required."
  }
}
```

---

## Design Decisions & Trade-offs

### 1. SQLite as default
**Decision**: SQLite ships with Python — no external DB needed to run locally.
**Trade-off**: Not production-suitable for concurrent writes. Swap to PostgreSQL/Neon via `DATABASE_URL` in settings; the ORM query code is identical.

### 2. Soft delete over hard delete
**Decision**: `is_deleted` flag + `deleted_at` timestamp, with a `/restore/` endpoint.
**Trade-off**: Queries must always filter `is_deleted=False`. Handled by overriding `get_queryset()` in the ViewSet; the deleted list is only accessible to admins.

### 3. Analytics in a service layer
**Decision**: All aggregation logic lives in `records/services.py`, not in views.
**Reason**: Views should stay thin. The service functions are pure Django ORM — easy to unit test independently and swap for raw SQL if performance demands it.

### 4. Public register forces Viewer role
**Decision**: `POST /api/auth/register/` always assigns the `viewer` role, ignoring any `role` field in the request body. Admins use `POST /api/auth/users/` to create analyst or admin accounts.
**Reason**: Prevents privilege escalation via self-registration.

### 5. Permission classes over inline checks
**Decision**: `IsAdmin`, `IsAnalystOrAdmin`, `IsActiveUser` are standalone DRF permission classes, applied per view/action via `get_permissions()`.
**Trade-off**: Slightly more code than inline `if request.user.role == 'admin'`, but far more testable, composable, and explicit.

### 6. Pagination default 20 items
Configurable in `settings.py → PAGE_SIZE`. All list endpoints support `?page=N`.

---

## Optional Enhancements Included
- ✅ JWT Authentication
- ✅ Pagination (page-based, 20/page)
- ✅ Search (`?search=`)
- ✅ Soft delete + restore
- ✅ Swagger / OpenAPI docs at `/api/docs/`
- ✅ Custom error envelope via exception handler

## Not Included (out of scope)
- Rate limiting (add `django-ratelimit` or nginx config in production)
- Unit / integration test suite (structure supports pytest-django)
