# FastAPI Projects

Course projects from a FastAPI backends track — REST APIs first, then databases.

## Projects

| Folder | What it is | Storage |
|---|---|---|
| [chai-point](./chai-point) | Chai Point read-only menu API for kiosks and mobile | in-memory list |
| [pincode-lookup](./pincode-lookup) | Checkout auto-fill: PIN → city + state, plus bulk POST | in-memory dict |
| [rangmanch](./rangmanch) | Theatre reviews API — SQLite, SQLModel, lifespan, DI, CRUD | SQLite |
| [dabbewala](./dabbewala) | Mumbai tiffin order tracker — Enum statuses, PATCH, routers, daily stats | SQLite |

Notes, diagrams, and concept tables live in each folder's `README.md`.

### How the projects build

| Project | New idea |
|---|---|
| **Chai Point** | FastAPI + uvicorn, query vs path, Pydantic `response_model`, `HTTPException` |
| **Pincode lookup** | `field_validator`, custom exceptions + `add_exception_handler`, POST body vs path |
| **Rangmanch** | Lifespan, SQLModel, `Depends` session, real CRUD |
| **Dabbewala** | Enum statuses, extra routers, daily aggregation |

---

## Chai Point — project diagram

Chai Point, Bengaluru wants a read-only menu API so kiosk displays and mobile apps can fetch the latest menu without hitting a database.

```mermaid
flowchart LR
    Kiosk["Client<br/>(App / Kiosk)"] --> API["FastAPI Server"]
    Mobile["Mobile"] --> API
    API --> Mem["In-Memory<br/>Menu Data"]
    API --> JSON["JSON Response"]

    API -->|"GET /menu"| All["List All Items"]
    API -->|"GET /menu?category=chai"| Filter["Filter by Category"]
    API -->|"GET /menu/{id}"| One["Single Item"]
```

```mermaid
flowchart TB
    subgraph learn1 ["Chai Point — dotted skills box"]
        A1["Creating a FastAPI app and running it with uvicorn"]
        B1["Path parameters and query parameters"]
        C1["Pydantic response models for consistent API output"]
        D1["Raising HTTPException for error handling"]
    end
```

---

## Pincode lookup — project diagram

Checkout form sends a PIN. Validate first. Only valid PINs hit the directory.

```mermaid
flowchart TB
    Req["Client request"] --> Val["Pydantic Validation"]
    Val -->|Invalid| E422["Error Response 422 / 400"]
    Val -->|Valid| DB["Pincode Database"]
    DB -->|Found| OK["City + State Response"]
    DB -->|Not Found| E404["404 Not Found"]
```

```mermaid
flowchart TB
    subgraph learn2 ["Pincode — dotted skills box"]
        A2["Pydantic field_validator for input validation"]
        B2["Custom exception classes and exception handlers"]
        C2["POST requests with JSON body"]
        D2["Difference between path parameters and request bodies"]
        E2["Clean error response patterns"]
    end
```

Handlers are registered with `app.add_exception_handler(ErrorClass, handler)`. Bulk codes arrive in the **POST request body**, not the URL.

---

## Rangmanch — project diagram

Rangmanch, a Pune-based theatre company, needs a reviews API so audiences can rate and review plays.

```mermaid
flowchart LR
    Client["Client<br/>(Theatre App)"] --> FastAPI["FastAPI Server"]

    FastAPI -->|"POST /review/"| Create["Create Review"]
    FastAPI -->|"GET /review/"| List["List Reviews<br/>(Paginated)"]
    FastAPI -->|"PATCH /review/id"| Update["Update Review"]
    FastAPI -->|"DELETE /review/id"| Delete["Delete Review"]

    Create --> Session["SQLModel Session"]
    List --> Session
    Update --> Session
    Delete --> Session

    Session --> DB[("SQLite<br/>rangmanch.db")]
```

Also used, not drawn above: `GET /review/{id}` and `GET /review/average/{play_name}`.

```mermaid
flowchart TB
    subgraph stack ["Stack"]
        A["SQLModel — models that are both tables and Pydantic schemas"]
        B["SQLite — zero-config file database"]
        C["FastAPI lifespan — create tables on startup"]
        D["Depends + yield — one Session per request"]
        E["APIRouter — /review routes in their own module"]
        F["Full CRUD + average rating"]
    end
```

---

## REST ideas that show up across the repo

| Idea | Chai Point | Pincode | Rangmanch / Dabbewala |
|---|---|---|---|
| Resource URL | `/menu`, `/menu/{id}` | `/pincode/{code}` | `/review/{id}` |
| Query filter | `?category=chai` | — | `?play_name=&skip=&limit=` |
| Request body | — | `POST /pincode/bulk` | `POST /review/`, `PATCH` |
| 4xx not 500 | `HTTPException` | custom handlers | `HTTPException` |
| Typed JSON | Pydantic models | Pydantic + validators | SQLModel schemas |
