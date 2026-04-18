# Backend Wizards Stage 1: Data Persistence & API Design

A FastAPI-based REST API that integrates three external APIs (Genderize, Agify, Nationalize) to create user profiles with demographic classification, stores them in a database, and exposes endpoints for CRUD operations with filtering.

## Features

✅ **Multi-API Integration** — Calls Genderize, Agify, and Nationalize APIs  
✅ **Data Persistence** — SQLite database with SQLAlchemy ORM  
✅ **Idempotency** — Duplicate name detection (returns existing profile)  
✅ **Smart Filtering** — Query profiles by gender, country, age group (case-insensitive)  
✅ **Error Handling** — Proper 502 responses for invalid external API data  
✅ **UUID v7 IDs** — Unique identifiers for each profile  
✅ **CORS Support** — Accessible from any origin  

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: SQLite + SQLAlchemy ORM
- **HTTP Client**: httpx (async)
- **UUID**: uuid7 library
- **Deployment**: Railway, Heroku, Vercel, or AWS

## Installation & Setup

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd backend-wizards-stage1
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

Server runs on `http://localhost:8000`

## API Endpoints

### 1. Create Profile
**POST** `/api/profiles`

Request:
```json
{ "name": "ella" }
```

Response (201 Created):
```json
{
  "status": "success",
  "data": {
    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
    "name": "ella",
    "gender": "female",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 46,
    "age_group": "adult",
    "country_id": "DRC",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}
```

If name already exists:
```json
{
  "status": "success",
  "message": "Profile already exists",
  "data": { ...existing profile... }
}
```

### 2. Get Single Profile
**GET** `/api/profiles/{id}`

Response (200):
```json
{
  "status": "success",
  "data": { ...profile object... }
}
```

### 3. Get All Profiles (with filtering)
**GET** `/api/profiles`

Query parameters (all optional, case-insensitive):
- `gender` — Filter by gender (male, female)
- `country_id` — Filter by country code (e.g., NG, US, DRC)
- `age_group` — Filter by age group (child, teenager, adult, senior)

Examples:
```
/api/profiles
/api/profiles?gender=male
/api/profiles?country_id=NG&age_group=adult
/api/profiles?gender=female
```

Response (200):
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "id": "id-1",
      "name": "emmanuel",
      "gender": "male",
      "age": 25,
      "age_group": "adult",
      "country_id": "NG"
    },
    {
      "id": "id-2",
      "name": "sarah",
      "gender": "female",
      "age": 28,
      "age_group": "adult",
      "country_id": "US"
    }
  ]
}
```

### 4. Delete Profile
**DELETE** `/api/profiles/{id}`

Response: 204 No Content (on success)

## Error Responses

All errors follow this format:
```json
{ "status": "error", "message": "<error message>" }
```

| Status | Message | Reason |
|--------|---------|--------|
| 400 | "Name is required and cannot be empty" | Missing/empty name |
| 404 | "Profile not found" | ID doesn't exist |
| 502 | "Genderize returned an invalid response" | External API failure |
| 502 | "Agify returned an invalid response" | External API failure |
| 502 | "Nationalize returned an invalid response" | External API failure |

## Classification Rules

**Age Groups** (from Agify):
- 0–12: `child`
- 13–19: `teenager`
- 20–59: `adult`
- 60+: `senior`

**Nationality**: Highest probability country from Nationalize API

## Testing

### Manual Testing with cURL

```bash
# Create profile
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "ella"}'

# Get all profiles
curl http://localhost:8000/api/profiles

# Get filtered profiles
curl http://localhost:8000/api/profiles?gender=female&country_id=NG

# Get single profile
curl http://localhost:8000/api/profiles/{id}

# Delete profile
curl -X DELETE http://localhost:8000/api/profiles/{id}
```

### Testing Script
Run `test_api.py` to test all endpoints:
```bash
python test_api.py
```

## Deployment

### Railway
1. Push code to GitHub
2. Connect repo to Railway
3. Set `PYTHON_VERSION` to 3.10+
4. Deploy
5. Copy the live URL

### Heroku
```bash
git push heroku main
```

### Vercel (with serverless functions)
Use `vercel.json` to deploy FastAPI on Vercel

## Database

SQLite database stored in `profiles.db`. Schema:

```sql
CREATE TABLE profiles (
  id TEXT PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  gender TEXT,
  gender_probability FLOAT,
  sample_size INTEGER,
  age INTEGER,
  age_group TEXT,
  country_id TEXT,
  country_probability FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Implementation Details

1. **UUID v7**: All profile IDs are UUID v7 (sortable by timestamp)
2. **Idempotency**: Same name query checks DB first—no duplicates
3. **Error Handling**: If any external API returns invalid data (null age, null gender, no country), return 502
4. **CORS**: `Access-Control-Allow-Origin: *` header on all responses
5. **UTC Timestamps**: All times in ISO 8601 format

## Passing Requirements (75/100 minimum)

- ✅ API Design (15 pts) — All 4 endpoints working
- ✅ Multi-API Integration (15 pts) — All 3 APIs called correctly
- ✅ Data Persistence (20 pts) — Database stores & retrieves correctly
- ✅ Idempotency (15 pts) — Duplicate names handled
- ✅ Filtering Logic (10 pts) — Query params work case-insensitively
- ✅ Data Modeling (10 pts) — Schema matches spec
- ✅ Error Handling (10 pts) — 502 errors for bad upstream data

---

**Submission Deadline**: Friday, Apr 17, 2026 | 11:59 PM GMT+1 (WAT)

**Pass Mark**: 75/100

Good luck! 🚀
