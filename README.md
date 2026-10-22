# Address Book API

A minimal FastAPI-based API for managing addresses with geographic coordinates; via **FastAPI**, **SQLAlchemy 2.0** and **SQLite**.

---

## Endpoints

| Capability | Endpoint |
| --- | --- |
| Create an address | `POST /addresses/` |
| List addresses (paginated) | `GET /addresses/` |
| Fetch a single address | `GET /addresses/{address_id}` |
| Partially update an address | `PATCH /addresses/{address_id}` |
| Delete an address | `DELETE /addresses/{address_id}` |
| Find addresses within a radius | `GET /addresses/nearby` |
| Health check | `GET /health` |
---

## Requirements

- Python **3.12+**
- [`uv`](https://docs.astral.sh/uv/) (recommended) **or** `pip`

---

## Getting started

### Option A - with `uv` 

```bash
git clone https://github.com/LinkAnJarad/fastapi-eastvantage-tech-exam
cd addressbook

# Create the virtual environment and install dependencies
uv sync

# Run the app (http://127.0.0.1:8000)
uv run uvicorn app.main:app --reload
```

`uv sync` reads `pyproject.toml` / `uv.lock` and installs both runtime and
dev dependencies into `.venv/`.

### Option B - with `pip`

```bash
git clone https://github.com/LinkAnJarad/fastapi-eastvantage-tech-exam
cd addressbook

python -m venv .venv

# Linux / macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (cmd.exe)
.venv\Scripts\activate.bat

pip install -r requirements.txt

uvicorn app.main:app --reload
```

### Verifying the install

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","message":"Address Book API is running."}
```

Open <http://127.0.0.1:8000/docs> for auto-generated docs and trying out the routes.

---

## Running the tests

```bash
uv run pytest
```


The suite runs against a throwaway SQLite database (selected through the `ADDRESSBOOK_DATABASE_URL` environment variable).

To run the tests with `pip`:

```bash
pytest
```

---

## API reference

Base URL: `http://127.0.0.1:8000`

### Address schema

| Field | Type | Rules |
| --- | --- | --- |
| `id` | integer | Assigned by the database, read-only |
| `street` | string | 1-255 characters, required |
| `barangay` | string | 1-255 characters, required |
| `city` | string | 1-255 characters, required |
| `region` | string | 1-255 characters, required |
| `postal_code` | string | 1-20 characters, required |
| `latitude` | float | -90.0 to 90.0, required |
| `longitude` | float | -180.0 to 180.0, required |

The address fields follow Philippine address conventions.

### `POST /addresses/` - create an address

Returns `201 Created`.

```bash
curl -X POST http://127.0.0.1:8000/addresses/ \
  -H "Content-Type: application/json" \
  -d '{
    "street": "1000 EDSA",
    "barangay": "Barangay Kalusugan",
    "city": "Quezon City",
    "region": "National Capital Region",
    "postal_code": "1104",
    "latitude": 14.6091,
    "longitude": 121.0223
  }'
```

```json
{
  "street": "1000 EDSA",
  "barangay": "Barangay Kalusugan",
  "city": "Quezon City",
  "region": "National Capital Region",
  "postal_code": "1104",
  "latitude": 14.6091,
  "longitude": 121.0223,
  "id": 1
}
```

### `GET /addresses/` - list addresses

Query parameters: `skip` (offset, default `0`) and `limit` (default `64`).

```bash
curl "http://127.0.0.1:8000/addresses/?skip=0&limit=10"
```

### `GET /addresses/{address_id}` - fetch one address

```bash
curl http://127.0.0.1:8000/addresses/1
```

Returns `404 Not Found` if no address has that ID.

### `PATCH /addresses/{address_id}` - partially update an address

Only the fields sent are changed; the rest are left untouched.

```bash
curl -X PATCH http://127.0.0.1:8000/addresses/1 \
  -H "Content-Type: application/json" \
  -d '{"street": "1001 EDSA", "latitude": 14.61}'
```

### `DELETE /addresses/{address_id}` - delete an address

Returns `204 No Content`.

```bash
curl -X DELETE http://127.0.0.1:8000/addresses/1
```

### `GET /addresses/nearby` - proximity search

Query parameters:

| Parameter | Type | Rules |
| --- | --- | --- |
| `target_lat` | float | -90.0 to 90.0, required |
| `target_lon` | float | -180.0 to 180.0, required |
| `max_distance_km` | float | > 0, required |

```bash
curl "http://127.0.0.1:8000/addresses/nearby?target_lat=14.6091&target_lon=121.0223&max_distance_km=5"
```

Each result is an address plus its `distance_km` from the target, sorted closest-first:

```json
[
  {
    "street": "1000 EDSA",
    "barangay": "Barangay Kalusugan",
    "city": "Quezon City",
    "region": "National Capital Region",
    "postal_code": "1104",
    "latitude": 14.6091,
    "longitude": 121.0223,
    "id": 1,
    "distance_km": 0.0
  }
]
```

### `GET /health` - health check

```bash
curl http://127.0.0.1:8000/health
```

---

## Config

The variable `ADDRESSBOOK_DATABASE_URL` is defaulted to `sqlite:///./addresses.db`. Used by the test suite to point at a temporary database. |

The SQLite file `addresses.db` is created in the project root on first startup.

---

## Design notes

Distance calculation is done via haversine distance (for spherical earth). Larger databases/addresses may need a pre-filter to cut the candidate set down + haversine distance calculation. Spatial index (like PostGIS) can also be done.

