# farmapi — Farm Management API

A **Django REST Framework** backend for a bilingual (**English / Arabic**) farm-management
 app . It serves JSON only. and each phone builds its
own interface on top. Farmers manage their farms, crops, plants (positioned on a map
image), tasks, and budgeting (income/expenses).

## Tech stack 
- Django 6 + Django REST Framework
- JWT authentication (`djangorestframework-simplejwt`) with refresh-token rotation + blacklist
- PostgreSQL (production)
- Python 3.12

## Apps
| App | Models |
|-----|--------|
| `accounts` | auth endpoints (register / login / refresh / logout) |
| `farm` | `Farm` (owned by a user) |
| `crops` | `Crop`, `CropBasemap`, `Plant`, `PlantCategory` |
| `tasks` | `Task` |
| `budgeting` | `Category`, `Transaction` |

## Setup

```bash
# 1. Create & activate the environment
conda create -n farmapi python=3.12
conda activate farmapi

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env          # then edit .env and set DJANGO_SECRET_KEY
#   generate a key:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Set up the database
python manage.py migrate
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

The API is then at `http://127.0.0.1:8000/`, admin at `/admin/`.
(Optional) load sample data: `python manage.py shell < seed_data.py`

## Authentication

All `/api/` endpoints require a JWT access token (`Authorization: Bearer <token>`),
except register and login.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/register/` | create a user |
| POST | `/api/auth/login/` | → `{ access, refresh }` |
| POST | `/api/auth/refresh/` | refresh → new access token |
| POST | `/api/auth/logout/` | revoke a refresh token |

Access tokens last 15 minutes; refresh tokens 7 days (rotated on use).

## Resource endpoints

`GET/POST` on the list, `GET/PUT/PATCH/DELETE` on `/<id>/`:

| Endpoint | Filters |
|----------|---------|
| `/api/farms/` | — |
| `/api/crops/` | `?farm=` |
| `/api/basemaps/` | `?crop=` |
| `/api/plants/` | `?crop=` |
| `/api/tasks/` | `?farm=` `?crop=` `?is_done=` |
| `/api/categories/` | `?farm=` |
| `/api/transactions/` | `?farm=` `?crop=` `?type=income\|expense` |

All data is **scoped to the logged-in user** — you only see and modify your own farms
and everything under them.


