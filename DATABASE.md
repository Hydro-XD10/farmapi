# farmapi — Database Schema & Relationships

Data model for the bilingual (EN/AR) farm-management API. All primary keys are
`UUID` except `User` (auto integer). All text fields accept Arabic or English
Unicode. Money is `Decimal(12,2)`; timestamps are UTC.

## Relationship overview (ERD)

```
                         ┌─────────────┐
                         │    User     │  (accounts)  login = phone_number
                         └──────┬──────┘
                                │ 1
                                │ owner (CASCADE)
                                │ *
                         ┌──────▼──────┐
                         │    Farm     │  (farm)   the tenant root
                         └──────┬──────┘
        ┌───────────────┬───────┼─────────────┬──────────────────┐
        │1              │1      │1            │1                 │1
        │* crops        │* tasks│* transactions│* categories     │
   ┌────▼────┐     ┌────▼────┐  │         ┌────▼─────┐           │
   │  Crop   │     │  Task   │  │         │ Category │◄──────────┘ (nullable:
   └────┬────┘     └─────────┘  │         └────┬─────┘   NULL farm = system cat)
    │1  │1  ▲ ▲                 │              │*
    │*  │*  │ │                 │  category    │ (SET_NULL)
┌───▼──┐│ ┌─┴─┴──────┐          │ ┌────────────▼──┐
│Base- ││ │  Plant   │          └─│  Transaction  │
│map   ││ └────┬─────┘  crop      └───────────────┘
└──────┘│      │1        (SET_NULL)
        │      │*
   ┌────▼──────▼───┐
   │ PlantCategory │  (links a Crop + a Plant)
   └───────────────┘
```

Arrows into `Task`/`Transaction` from `Crop`/`Plant` are **optional** (`SET_NULL`);
the solid ownership chain (`User → Farm → Crop → Plant`) is `CASCADE`.

---

## Tables

### User  (`accounts.User`)
Custom user; **login identifier is `phone_number`** (no username).

| Field | Type | Notes |
|-------|------|-------|
| id | int PK | auto |
| phone_number | char(15) | **unique**, `USERNAME_FIELD`, regex `^\+?\d{8,15}$` |
| password | char | hashed (never plain) |
| email | email | optional |
| is_staff / is_superuser / is_active | bool | from AbstractUser |
| date_joined / last_login | datetime | |

Reverse: `user.farms` → all Farms owned.

---

### Farm  (`farm.Farm`) — the tenant root
Everything a user owns hangs off a Farm. Authorization scopes all queries through it.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| owner | FK → User | `CASCADE`; currently `null=True` (dev) — should become required |
| name | char(255) | EN/AR |
| location | char(255) | optional, EN/AR |
| lat, lng | float | optional coordinates |
| created_at | datetime | auto |

Reverse: `farm.crops`, `farm.tasks`, `farm.transactions`, `farm.categories`.

---

### Crop  (`crops.Crop`)
| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| farm | FK → Farm | **CASCADE** (crop dies with farm) |
| name | char(255) | EN/AR |
| type | char(255) | optional |
| created_at | datetime | auto |

Reverse: `crop.basemaps`, `crop.plants`, `crop.plant_categories`, `crop.tasks`, `crop.transactions`.

---

### CropBasemap  (`crops.CropBasemap`)
Frozen background photo; plants are positioned on it.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| crop | FK → Crop | **CASCADE** |
| image_uri | char(500) | external URI |
| source | char(50) | 'user_upload','mapbox'… optional |
| width_px, height_px | int | optional |
| center_lat, center_lng, zoom | float | optional georef |
| is_active | bool | default True |
| captured_at | datetime | auto |

**Constraint:** `one_active_basemap_per_crop` — at most one `is_active=True` basemap per crop (partial unique index).

---

### Plant  (`crops.Plant`)
A point on the crop's basemap; `img_x`/`img_y` are normalized 0..1.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| crop | FK → Crop | **CASCADE** |
| label | char(255) | optional, EN/AR |
| img_x, img_y | float | 0..1 (validated) — position on image |
| color | char(9) | hex, default `#4F8F2C` |
| type | char(255) | optional |
| age_months | int | optional |
| notes | text | optional |
| is_special | bool | default False |
| needs_care | bool | default False |
| srblh | bool | default False — سربلة |
| bunch | int | default 0 — عذوق |
| created_at | datetime | auto |

Reverse: `plant.categories` (PlantCategory), `plant.plant_tasks` (Task).

---

### PlantAttribute  (`crops.PlantAttribute`)
A **user-defined** per-plant field (e.g. مسربل: yes/no, عدد العذوق: number). The
user names it and picks the value type — nothing is hardcoded. Endpoint:
`/api/plant-attributes/` (`?crop=`).

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| crop | FK → Crop | CASCADE, reverse `crop.plant_attributes` |
| name | char(255) | EN/AR, **unique per crop** |
| value_type | char(5) | choices: `bool` / `int` / `float` / `text` |

### PlantAttributeValue  (`crops.PlantAttributeValue`)
The value of one attribute for one plant. Endpoint: `/api/plant-attribute-values/`
(`?plant=`, `?attribute=`).

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| attribute | FK → PlantAttribute | CASCADE, reverse `attribute.values` |
| plant | FK → Plant | CASCADE, reverse `plant.attribute_values` |
| value | JSONField | any JSON type; serializer enforces it matches `value_type` |

**Constraints:** one value per (attribute, plant); attribute and plant must belong
to the same crop (serializer-enforced).

---

### TaskCategory  (`tasks.TaskCategory`)
User-made work categories (ري، تقليم…) — no rigid predefined ones. Endpoint:
`/api/task-categories/`.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| farm | FK → Farm | **CASCADE**, required (always user-made) |
| name | char(255) | EN/AR |

---

### Task  (`tasks.Task`)
| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| farm | FK → Farm | **CASCADE** (required) |
| crop | FK → Crop | **SET_NULL**, optional |
| plant | FK → Plant | **SET_NULL**, optional (reverse `plant.plant_tasks`) |
| category | FK → TaskCategory | **SET_NULL**, optional |
| title | char(255) | EN/AR |
| assigned_to | char(255) | optional — اسم العامل (who works on it; free text) |
| priority | char(6) | choices: low / medium / high; optional |
| is_done | bool | default False |
| cost | Decimal(12,2) | optional — **auto-syncs to an expense Transaction** (see below) |
| hours_spent | float | optional |
| created_at | datetime | auto |

**Cost → budgeting sync (`tasks/signals.py`):** whenever a task is saved with a
cost, the server creates/updates one linked expense `Transaction`
(`Transaction.task`, one-to-one). Clearing the cost — or deleting the task —
removes that transaction. Budgeting is the single source of truth, so
`/api/budget/summary/` includes task costs with no double counting.

---

### Category  (`budgeting.Category`)
Two kinds: **user-made** (`farm` set, `is_user_made=True`) and **system**
(`farm=NULL`, `is_user_made=False`, shared by everyone; created only by seed data).

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| farm | FK → Farm | **CASCADE**, nullable (NULL = system) |
| name | char(255) | EN/AR |
| is_user_made | bool | default True (server-controlled via API) |

---

### Transaction  (`budgeting.Transaction`)
| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| farm | FK → Farm | **CASCADE** (required) |
| crop | FK → Crop | **SET_NULL**, optional |
| category | FK → Category | **SET_NULL**, optional |
| task | OneToOne → Task | **CASCADE**, nullable, **server-managed** — marks the auto-created expense for a Task's cost; read-only via API |
| type | char(10) | choices: income / expense (CHECK constraint) |
| amount | Decimal(12,2) | required |
| date_gregorian | date | optional — التاريخ الميلادي |
| date_hijri | char(20) | optional text — التاريخ الهجري |
| from_supplier | bool | default False |
| notes | text | optional |
| created_at | datetime | auto |

**Constraint:** `transaction_type_valid` — `type` must be `income` or `expense`.

---

## Delete behavior (cascade rules)

| Delete this | Effect |
|-------------|--------|
| User | → their Farms → all Crops/Tasks/Transactions/Categories → Plants/Basemaps (full cascade) |
| Farm | → its Crops (→ Plants, Basemaps, PlantCategories), Tasks, Transactions, Categories |
| Crop | → its Plants, Basemaps, PlantCategories; **detaches** (SET_NULL) from Tasks & Transactions |
| Plant | → its PlantCategories; **detaches** from Tasks |
| Category | **detaches** (SET_NULL) from Transactions |

**Rule of thumb:** things meaningless without their parent = `CASCADE`; historical
records (tasks, money) that should survive a parent deletion = `SET_NULL`.

## Multi-tenancy / authorization
There is no per-row `owner` except on `Farm`. Every other table is scoped to the
user by walking the FK chain back to `Farm.owner` (e.g. `farm__owner`,
`crop__farm__owner`). System categories (`farm=NULL`) are the one shared resource,
readable by all, writable by none via the API.
