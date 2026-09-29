# FastAPI Projects

Course projects from a FastAPI backends track — REST APIs first, then databases, then RAG.

## Projects

| Folder | What it is | Storage |
|---|---|---|
| [chai-point](./chai-point) | Chai Point read-only menu API for kiosks and mobile | in-memory list |
| [pincode-lookup](./pincode-lookup) | Checkout auto-fill: PIN → city + state, plus bulk POST | in-memory dict |
| [rangmanch](./rangmanch) | Theatre reviews API — SQLite, SQLModel, lifespan, DI, CRUD | SQLite |
| [dabbewala](./dabbewala) | Mumbai tiffin order tracker — Enum statuses, PATCH, routers, daily stats | SQLite |
| [kitaab-exchange](./kitaab-exchange) | DU used-textbook exchange — header auth, User→Books, search listings | SQLite |
| [rag](./rag) | Ask a PDF questions — chunk, embed, Qdrant, then generate | Qdrant + OpenAI |

Notes, diagrams, and concept tables live in each folder's `README.md`.

### How the projects build

| Project | New idea |
|---|---|
| **Chai Point** | FastAPI + uvicorn, query vs path, Pydantic `response_model`, `HTTPException` |
| **Pincode lookup** | `field_validator`, custom exceptions + `add_exception_handler`, POST body vs path |
| **Rangmanch** | Lifespan, SQLModel, `Depends` session, real CRUD |
| **Dabbewala** | Enum statuses, extra routers, daily aggregation |
| **Kitaab Exchange** | `Header` dependency, API key on writes, one-to-many SQLModel, query search |
| **RAG intro** | PDF chunks, embeddings, Qdrant, `POST /index/` + `POST /query/` |

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

---

## RAG intro — project diagram

Upload a PDF. Chunk it. Embed it. Ask questions. The chat model only sees the retrieved pages.

```mermaid
flowchart LR
    Upload["POST /index/"] --> Qdrant[("Qdrant :6333")]
    CLI["index.py"] --> Qdrant
    Client["POST /query/"] --> Search["similarity_search"]
    Search --> Qdrant
    Qdrant --> LLM["chat model"]
    LLM --> JSON["answer + sources"]
```

```mermaid
flowchart TB
    subgraph learn6 ["RAG intro — skills"]
        A6["PyPDFLoader + overlapping chunks"]
        B6["OpenAI embeddings vs chat models"]
        C6["Qdrant vector store"]
        D6["UploadFile multipart POST /index/"]
        E6["Retrieve-then-generate on POST /query/"]
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

---

## Kitaab Exchange — project diagram

Delhi University students buy and sell used textbooks. Writes need `X-API-Key`. Reads are public.

```mermaid
flowchart LR
    Client["Client<br/>(Student App)"] --> Check{"X-API-Key"}
    Check -->|Valid| API["FastAPI Server"]
    Check -->|Invalid| E401["401 Invalid API Key"]
    API --> Users["Users Router"]
    API --> Books["Books Router"]
    Users --> DB[("SQLite kitaab.db")]
    Books --> DB
```

---

## REST ideas that show up across the repo

| Idea | Chai Point | Pincode | Rangmanch / Dabbewala | Kitaab Exchange | RAG |
|---|---|---|---|---|---|
| Resource URL | `/menu`, `/menu/{id}` | `/pincode/{code}` | `/review/{id}` | `/users/`, `/books/{id}` | `/index/`, `/query/` |
| Query filter | `?category=chai` | — | `?play_name=&skip=&limit=` | `?title=` `?author=` | — |
| Request body | — | `POST /pincode/bulk` | `POST /review/`, `PATCH` | `POST /users/`, `POST /books/` | JSON question + multipart PDF |
| Auth | — | — | — | `X-API-Key` on writes | OpenAI key in `.env` |
| 4xx not 500 | `HTTPException` | custom handlers | `HTTPException` | `HTTPException` 401/400/404 | 400 / 500 / 503 |
| Typed JSON | Pydantic models | Pydantic + validators | SQLModel schemas | SQLModel + Relationship | Pydantic `QueryRequest` |
