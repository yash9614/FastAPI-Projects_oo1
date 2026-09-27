# Rangmanch Reviews API

Theatre reviews API for a Pune-based company. Audiences rate and review plays. The API powers the app review section and average-rating displays.

Built with **FastAPI**, **SQLModel**, and **SQLite**.

## Run

```bash
cd rangmanch
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

- App: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

On Windows, prefer `python -m uvicorn` if `uvicorn` is not on PATH.

## Project layout

```
rangmanch/
  main.py              # app, lifespan, router mount
  database.py          # engine, create_tables, get_session
  models.py            # SQLModel table + request/response models
  requirements.txt
  routes/
    __init__.py
    reviews.py         # all /review endpoints
  rangmanch.db         # created on first startup (not committed)
```

## Endpoints

| Method | Path | What it does |
|---|---|
| GET | `/` | Welcome message |
| POST | `/review/` | Create a review |
| GET | `/review/` | List reviews (`play_name`, `skip`, `limit`) |
| GET | `/review/average/{play_name}` | Average rating + count for one play |
| GET | `/review/{review_id}` | One review |
| PATCH | `/review/{review_id}` | Update rating and/or comment |
| DELETE | `/review/{review_id}` | Delete a review |

Example create body:

```json
{
  "play_name": "Ghashiram Kotwal",
  "reviewer_name": "Asha",
  "rating": 5,
  "comment": "Packed house in Pune"
}
```

---

## Concepts learned in this project

### 1. FastAPI app and auto docs

`FastAPI(...)` is the application. `title` and `description` show up in Swagger at `/docs` and ReDoc at `/redoc`. Path operations become OpenAPI endpoints automatically.

```python
app = FastAPI(
    title="Rangmanch Reviews API",
    description="Theatre reviews API for Pune Rangmanch",
    lifespan=lifespan,
)
```

### 2. Lifespan (startup / shutdown)

Replaces the old `@app.on_event("startup")` style.

- Code **before** `yield` runs once when the server starts.
- Code **after** `yield` runs when the server stops.

Here, startup creates SQLite tables so the first request does not hit a missing table.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield
```

### 3. SQLite as a zero-config database

No separate database server. One file: `rangmanch.db`.

```python
DATABASE_URL = "sqlite:///rangmanch.db"
engine = create_engine(DATABASE_URL, echo=True)
```

`echo=True` prints SQL in the terminal. Useful while learning; turn it off later.

### 4. SQLModel = SQLAlchemy + Pydantic

One class can be both:

- a **table** (`table=True`)
- a **validated API model**

`Field(ge=1, le=5)` is both a DB constraint idea and request validation: a rating of `6` fails with 422 before it touches the database.

Split models so the client cannot send an `id` on create, and cannot change `play_name` on update:

| Model | Role |
|---|---|
| `Review` | table row |
| `ReviewCreate` | POST body |
| `ReviewRead` | response |
| `ReviewUpdate` | PATCH body (only `rating`, `comment`) |

### 5. Timezone-aware datetimes

Newer SQLModel rejects naive `datetime.now()`. Store UTC:

```python
created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 6. APIRouter and app structure

Routes live in `routes/reviews.py`, not in `main.py`.

```python
router = APIRouter(prefix="/review", tags=["reviews"])
app.include_router(reviews_router)
```

- `prefix="/review"` — every path on this router starts with `/review`
- `tags=["reviews"]` — groups endpoints in `/docs`

### 7. Dependency injection (`Depends`)

The route does not open the database itself. FastAPI calls `get_session()` and passes in the session.

```python
def get_session():
    with Session(engine) as session:
        yield session


def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    ...
```

`yield` means:

1. open session
2. run the route
3. close session even if the route raised

One request = one session. Routes never touch `engine` directly.

### 8. CRUD mapped to HTTP

| Action | Verb | Why this verb |
|---|---|---|
| Create | POST | new row |
| Read | GET | no change |
| Update | PATCH | partial change (`exclude_unset=True`) |
| Delete | DELETE | remove row |

`model_dump(exclude_unset=True)` on PATCH only applies fields the client actually sent. Sending `{ "rating": 4 }` does not wipe `comment`.

### 9. Path parameters vs query parameters

- Path: `/review/{review_id}` and `/review/average/{play_name}` — required part of the URL
- Query: `?play_name=...&skip=0&limit=10` — optional filters / pagination

`skip` + `limit` is offset pagination:

- page 1 → `skip=0&limit=10`
- page 2 → `skip=10&limit=10`

### 10. Route order matters

Declare `/review/average/{play_name}` **before** `/review/{review_id}`.

If `/{review_id}` comes first, FastAPI tries to parse the word `average` as an `int` and the average endpoint never matches.

### 11. `HTTPException`

Return a real HTTP status instead of a crash:

```python
if not review:
    raise HTTPException(status_code=404, detail="NO review")
```

Validation errors (bad rating, missing field) are 422 from SQLModel/Pydantic. You do not write those by hand.

### 12. Aggregations with SQLModel

Average rating is done in SQL, not in a Python loop:

```python
select(func.avg(Review.rating), func.count(Review.id)).where(
    Review.play_name == play_name
)
```

### 13. Register the table before `create_all`

`SQLModel.metadata.create_all(engine)` only creates tables for models that have been imported. That is why `main.py` imports `Review` even though it does not use the name.

### 14. Running the server

`main.py` defines `app`. Uvicorn loads that object:

```bash
uvicorn main:app --reload
```

`--reload` restarts on file save. `python main.py` does nothing unless you add a `uvicorn.run` block.

---

## How this sits after the earlier projects

| Project | Storage | New idea |
|---|---|---|
| Chai Point menu | in-memory list | routes, query filters, 404 |
| Pincode lookup | in-memory dict | custom exceptions |
| **Rangmanch** | SQLite + SQLModel | lifespan, ORM, DI, real CRUD |

Rangmanch is the first project in this series that keeps data after the process restarts.
