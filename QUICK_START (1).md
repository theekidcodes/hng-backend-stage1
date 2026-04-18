# Backend Wizards Stage 1 - Quick Start (5 Minutes)

## What You're Building
A REST API that:
1. Takes a name → calls 3 external APIs
2. Gets gender (Genderize), age (Agify), nationality (Nationalize)
3. Classifies age into groups (child/teenager/adult/senior)
4. Stores profiles in SQLite database
5. Serves data back via 4 REST endpoints

## File Structure
```
backend-wizards-stage1/
├── main.py              # FastAPI app + all endpoints
├── database.py          # SQLAlchemy + database setup
├── schemas.py           # Pydantic models (request/response)
├── external_api.py      # Integration with 3 external APIs
├── test_api.py          # Comprehensive test suite
├── requirements.txt     # Dependencies
├── README.md            # Full documentation
├── SETUP_GUIDE.md       # Detailed setup walkthrough
├── .gitignore           # Git ignore rules
├── Procfile             # Heroku deployment
├── railway.json         # Railway deployment
└── vercel.json          # Vercel deployment
```

## 60-Second Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
uvicorn main:app --reload

# 4. In another terminal, test
python test_api.py
```

**Server running?** → Open http://localhost:8000/health

## 4 Endpoints (What Graders Test)

### 1️⃣ CREATE PROFILE
```bash
POST /api/profiles
Body: {"name": "ella"}
```
Returns: Profile with all demographic data (gender, age, age_group, country)
**Key:** If name exists → return existing (idempotency)

### 2️⃣ GET ONE PROFILE
```bash
GET /api/profiles/{id}
```
Returns: Single profile with all fields

### 3️⃣ GET ALL PROFILES (with filtering)
```bash
GET /api/profiles?gender=female&country_id=NG&age_group=adult
```
Returns: List of profiles matching filters
**Key:** Filters are case-insensitive!

### 4️⃣ DELETE PROFILE
```bash
DELETE /api/profiles/{id}
```
Returns: 204 No Content (empty response)

## Error Responses (Important!)

| Status | Reason | Return This |
|--------|--------|-------------|
| 400 | Name is empty | `{"status": "error", "message": "Name is required..."}` |
| 404 | Profile not found | `{"status": "error", "message": "Profile not found"}` |
| 502 | Genderize returned null | `{"status": "error", "message": "Genderize returned an invalid response"}` |
| 502 | Agify returned null | `{"status": "error", "message": "Agify returned an invalid response"}` |
| 502 | Nationalize returned nothing | `{"status": "error", "message": "Nationalize returned an invalid response"}` |

## Classification Rules (Hardcoded!)

**Age Groups:**
- 0-12 → "child"
- 13-19 → "teenager"
- 20-59 → "adult"
- 60+ → "senior"

**Country:** Pick the one with highest probability from Nationalize

## Key Requirements (Don't Miss!)

✅ **CORS Header:** `Access-Control-Allow-Origin: *` (already in code)
✅ **Timestamps:** ISO 8601 format with Z suffix: `"2026-04-01T12:00:00Z"`
✅ **IDs:** UUID v7 (already in code with `uuid7` library)
✅ **Idempotency:** Same name = return existing, no new record
✅ **Duplicate Detection:** Use `func.lower()` in SQLAlchemy for case-insensitive lookup
✅ **Response Format:** MUST match spec exactly (grading is automated!)

## Testing (Quick Validation)

Run test suite:
```bash
python test_api.py
```

This tests:
- ✅ All 4 endpoints
- ✅ Duplicate handling
- ✅ Filtering
- ✅ Error cases
- ✅ CORS headers
- ✅ Response format

**Expect 15+ tests.** All should pass ✓

## Manual Testing (cURL)

```bash
# Create profile
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "ella"}'

# Get all
curl http://localhost:8000/api/profiles

# Get filtered
curl "http://localhost:8000/api/profiles?gender=male&age_group=adult"

# Get one (replace ID)
curl http://localhost:8000/api/profiles/PROFILE_ID_HERE

# Delete (replace ID)
curl -X DELETE http://localhost:8000/api/profiles/PROFILE_ID_HERE
```

## Deployment (Railway = Easiest)

1. Push to GitHub
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Done! Copy the live URL

**Get live URL:** Check Railway dashboard after deploy

## Common Mistakes 🚨

| Mistake | Fix |
|---------|-----|
| Response format doesn't match spec | Copy exact format from README |
| Duplicate names create new profiles | Add `UNIQUE` constraint in schema |
| Filtering is case-sensitive | Use `func.lower()` in SQLAlchemy |
| Missing CORS header | Check line with `Access-Control-Allow-Origin` |
| Timestamps without Z | Add `+ "Z"` when returning ISO format |
| UUID not v7 | Use `from uuid7 import uuid7` |
| 502 error but storing data anyway | Check null handling in external_api.py |
| Database locked error | It's fixed in database.py already |

## Grading Breakdown (100 pts)

| Criteria | Points |
|----------|--------|
| API Design (4 endpoints work) | 15 |
| Multi-API Integration (3 APIs called) | 15 |
| Data Persistence (data stored/retrieved) | 20 |
| Idempotency (duplicates handled) | 15 |
| Filtering Logic (query params work) | 10 |
| Data Modeling (schema matches) | 10 |
| Error Handling (502 for bad APIs) | 10 |
| Response Structure (format matches spec) | 5 |
| **TOTAL** | **100** |
| **Pass Mark** | **75+** |

## Submission Checklist

- [ ] Server runs locally without errors
- [ ] All tests pass
- [ ] Server deployed and live
- [ ] Tested from live URL (not localhost)
- [ ] `/api/profiles` works from live URL
- [ ] GitHub repo pushed with README
- [ ] Run `/submit` in Discord stage-one-backend
- [ ] Wait for Thanos bot confirmation

## Submission URLs Needed

```
API Base URL:   https://your-app-name.railway.app
GitHub Repo:    https://github.com/yourusername/backend-wizards-stage1
```

## Common External API Responses

**Genderize (OK):**
```json
{"name": "ella", "gender": "female", "probability": 0.99, "count": 1234}
```

**Genderize (FAIL - Return 502):**
```json
{"name": "xyz", "gender": null, "probability": 0, "count": 0}
```

**Agify (OK):**
```json
{"name": "ella", "age": 46, "count": 500}
```

**Agify (FAIL - Return 502):**
```json
{"name": "xyz", "age": null, "count": 0}
```

**Nationalize (OK):**
```json
{"name": "ella", "country": [{"country_id": "DRC", "probability": 0.85}]}
```

**Nationalize (FAIL - Return 502):**
```json
{"name": "xyz", "country": []}
```

## Pro Tips 💡

1. **Test with common names first:** "ella", "john", "sarah", "ahmed"
2. **Use Insomnia/Postman:** Easier than cURL for testing
3. **Check logs when 502 happens:** Print which API failed
4. **Database persists:** Profiles stay in `profiles.db`
5. **Timestamps important:** Many bugs come from wrong format
6. **Deploy early:** Don't wait until last minute

## Deadline ⏰

**Friday, Apr 17, 2026 | 11:59 PM GMT+1 (WAT)**

(That's ~3 days from now if Stage 1 just went live)

---

**You got this! Start with setup, run tests, deploy, submit. 🚀**
