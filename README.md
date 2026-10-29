# Productivity Tracker

A productivity tracking application for logging tasks, reviewing recent work, and searching past weeks.

The application allows users to track tasks, time spent, focus level, and task status; visualize recent productivity; generate AI-assisted weekly summaries; and search historical productivity data using natural-language semantic search.

The project uses a React frontend, FastAPI backend, SQLite for primary persistence, Gemini for summary generation, Chroma for vector search, and Pydantic-AI for agent orchestration.

---

## Startup

From the repository root:

### 1. Create the environment file

Copy the example environment file:

    cp .env.example .env

Populate the required values:

    DATABASE_URL=sqlite:///./productivity_tracker.db
    GENAI_API_KEY=your_gemini_api_key
    GOOGLE_API_KEY=your_gemini_api_key

- `GENAI_API_KEY` is used for weekly summary generation.
- `GOOGLE_API_KEY` is used by the Pydantic-AI historical search agent.

### 2. Start the application

    docker compose up --build

### 3. Seed demo tasks (optional)

With the stack running:

    docker compose exec backend python -m scripts.seed_demo

To wipe tasks, weekly summaries, and Chroma vectors without removing volumes:

    docker compose exec backend python -m scripts.clear_seed

This loads 100 themed tasks across the previous 4 complete weeks
(coding, fitness, learning, personal). It does **not** generate weekly
summaries or Chroma vectors.

After seeding, open each of those weeks in the UI and click **Generate**,
or call `POST /weekly-summary/{week_start_date}` for each Sunday. That
endpoint writes the Gemini summary and indexes it in Chroma, which
historical search depends on.

### 4. Open the application

Frontend:

    http://localhost:5173

Backend:

    http://localhost:8000

Health check:

    http://localhost:8000/healthz

Application data is persisted through Docker volumes and survives normal `docker compose down` / `docker compose up` cycles.

---

## Features

- Create, edit, and delete productivity tasks
- Track:
  - task status
  - category
  - time spent
  - focus level
- View productivity by:
  - week
  - date range
  - weekday
- Visualize completed work and time spent
- Generate AI-written weekly productivity summaries
- Persist weekly summaries for historical review
- Store historical summaries in a local vector database
- Search historical productivity using natural-language questions
- Agent-based historical search using Pydantic-AI
- Persistent application data through Docker volumes
- Fully containerized frontend and backend

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Nginx for the production/container build

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite

### AI / Retrieval

- Google Gemini
- Pydantic-AI
- ChromaDB
- Local Chroma embeddings

### Infrastructure

- Docker
- Docker Compose

---

## Task Model

Tasks support the following fields:

### Name

Required task name.

### Category

Supported categories:

- uncategorized
- work
- learning
- personal
- fitness
- other

### Status

Supported statuses:

- planned
- in-progress
- completed

A completed task requires:

- a focus level
- time spent greater than `0`

### Time Spent

Tracked in minutes.

### Focus Level

Numeric scale from `1` to `5`, with `5` representing the highest focus level.

### Lifecycle Timestamps

- `created_at`
- `started_at`
- `completed_at`

---

## Weekly Summaries

Weekly summaries combine deterministic application metrics with an AI-generated interpretation of the selected week.

Metrics provided to the model include:

- Tasks created
- Tasks started
- Tasks completed
- Total tracked time
- Average focus level for completed tasks
- Category distribution
- Relevant tasks for the selected period

Relevant tasks include tasks that were created, started, or completed during the selected week.

Gemini returns a structured response that is validated before persistence:

    summary
    suggestions

The generated summary is stored for later lookup with:

- ID
- Week start date
- Week end date
- Total tasks created
- Total tasks started
- Total tasks completed
- Total time spent in minutes
- Average focus level
- Category distribution
- Weekly summary notes
- Weekly summary suggestions
- Related task snapshots

Each related task snapshot stores:

- task ID
- task name
- category
- status

---

## Historical Search / RAG

Historical search uses the following pipeline:

    Natural-language question
            │
            ▼
    Pydantic-AI Agent
            │
            ▼
    Historical Search Tool
            │
            ▼
    Chroma Semantic Search
            │
            ▼
    Ranked Weekly Summary IDs
            │
            ▼
    SQLite Hydration
            │
            ▼
    Agent reasoning over retrieved summaries
            │
            ▼
    Structured response

Chroma is used only for semantic retrieval.

SQLite remains the authoritative source of persisted application data. After Chroma returns ranked summary IDs, the matching summaries are loaded from SQLite and returned in semantic relevance order.

---

## Design Decisions

Several design choices were made to keep the application small and local.

### SQLite Instead of Browser Persistence

Task persistence lives in the backend rather than `localStorage`.

Because the application already requires server-side AI, vector retrieval, and historical summaries, centralizing state in the backend avoids maintaining separate frontend and backend data models.

SQLite also keeps local setup lightweight while still providing relational persistence.

### SQLite as the Source of Truth

SQLite stores authoritative application data.

Chroma is treated as a rebuildable derived index rather than primary storage.

This keeps semantic retrieval concerns separate from transactional application state.

### Chroma Instead of a Raw FAISS Index

Chroma was selected because the project benefits from:

- local persistence
- metadata
- stable document IDs
- straightforward upserts
- simple semantic querying

Weekly summaries use stable vector IDs so regenerating a summary updates the corresponding semantic-search document rather than producing duplicates.

### Structured AI Output

Weekly summary generation uses a Pydantic schema rather than depending on unstructured model text.

The model is expected to return:

    summary: str
    suggestions: list[str]

This reduces parsing ambiguity and gives the API a predictable contract.

### JavaScript Instead of TypeScript

React was implemented using JavaScript.

JavaScript keeps the frontend setup light so more of the project can stay on backend architecture, AI integration, persistence, and retrieval.

---

## Known Tradeoffs and Limitations

### Historical Task State

Tasks are not event-sourced or fully versioned.

Weekly summaries are derived from lifecycle timestamps and the task state available when the summary is generated.

As a result, regenerating an older summary after later edits to a task can produce small differences.

A production system could address this with task-event history or state versioning.

### Time Attribution

`time_spent_minutes` is stored cumulatively on the task.

The application does not currently maintain individual work sessions.

Because of this, a task worked across multiple weeks cannot have its cumulative time perfectly allocated to the exact week in which each work session occurred.

A future implementation could use a separate time-entry model such as:

    task_id
    started_at
    ended_at
    duration

This is one of the first areas I would address in a future iteration.

### Weekly Summary Scheduling

Weekly summaries are currently generated on demand.

A production version could automatically generate the previous week's summary through a scheduled background job at the beginning of each new week.

### Single User

The application is designed for a single user.

Authentication, authorization, and multi-tenant data ownership were considered outside the current scope.

---

## AI-Assisted Development

AI-assisted development tools were used throughout the project as part of the implementation workflow.

They were used primarily for:

- frontend implementation and styling assistance
- implementation brainstorming
- debugging
- code review
- documentation support

Architectural decisions, backend data modeling, API behavior, analytics logic, persistence strategy, retrieval architecture, and implementation tradeoffs were reviewed and understood by the author. Suggestions from AI tooling were reviewed, revised, or rejected when they did not fit the intended design.

The use of AI tooling is disclosed rather than hidden.

---

## Future Improvements

Several potential improvements are also noted directly in the code where they became relevant during implementation.

Given additional development time, the next areas I would explore include:

- automatic weekly-summary generation
- task-event/version history
- individual time-entry tracking
- stronger automated test coverage
- vector-index rebuild tooling
- configurable similarity thresholds
- authentication and multiple users
- richer historical analytics
- database migrations
- production deployment configuration
