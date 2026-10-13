# Engineering Decisions

This document captures notable design decisions made during implementation, along with the reasoning and tradeoffs behind them.

---

## Backend Persistence Instead of Browser-Only Storage

### Decision

Use FastAPI + SQLite for application persistence instead of `localStorage` or IndexedDB.

### Why

The application already requires server-side GenAI, historical summary generation, and vector-search functionality.

Centralizing persistence in the backend:

- keeps application data in one place
- avoids maintaining separate frontend and backend data models
- prevents API credentials from reaching the browser
- makes historical analytics and semantic search easier to support

### Alternatives Considered

- `localStorage`
- IndexedDB

### Tradeoff

This adds backend setup and persistence complexity compared with a browser-only implementation, but provides a cleaner architecture for the features required by the challenge.

---

## JavaScript Instead of TypeScript

### Decision

Use JavaScript for the React frontend.

### Why

The challenge does not require TypeScript, and JavaScript reduces setup and implementation overhead for a one-week build.

I also have more experience working directly in JavaScript than TypeScript.

The reduced frontend overhead allowed more time to focus on:

- backend architecture
- persistence
- analytics
- GenAI integration
- semantic retrieval
- agent orchestration

### Tradeoff

TypeScript would provide stronger compile-time guarantees and better type safety across the frontend.

For the scope of this challenge, I considered that additional type-definition work lower priority than completing the core application features.

---

## AI-Assisted Frontend Development

Frontend development is not my primary area of expertise, so I used AI-assisted development tools more heavily for frontend implementation and styling.

The goal was not to delegate architectural decisions, but to accelerate areas where I have less experience while still understanding and reviewing the resulting implementation.

AI suggestions were reviewed, modified, or rejected when they did not fit the intended design.

---

## Task Data Model

### Categories

### Decision

Use a fixed set of categories:

- personal
- work
- learning
- fitness
- other
- uncategorized

### Why

A normalized set of categories provides predictable values for analytics and historical summaries.

`uncategorized` is used as the default so a user is not required to categorize a task immediately.

### Tradeoff

User-defined categories would provide more flexibility, but would also make aggregation and comparison less predictable.

For this challenge, a small fixed category set provides enough flexibility while keeping analytics simple.

---

## Task Status

### Decision

Use three task states:

- planned
- in-progress
- completed

New tasks default to `planned`.

### Why

These states provide enough lifecycle information to distinguish:

- work that has only been planned
- work that has actually started
- work that has been completed

This became important when determining which tasks should contribute to weekly productivity metrics.

---

## Focus Level

### Decision

Represent focus as a numeric enum from `1` to `5`.

### Why

A fixed scale gives the user enough flexibility to express focus while also producing normalized data that can be averaged and compared across tasks and weeks.

Focus is optional while a task is planned or in progress, but required when a task is completed.

### Tradeoff

Focus remains subjective and user-reported.

The goal is not to treat it as an objective productivity measurement, but as an additional signal that can be used alongside time and completion data.

---

## Completed Task Validation

### Decision

A completed task must have:

- a focus level
- `time_spent_minutes > 0`

### Why

A completed task without time or focus would weaken the usefulness of weekly analytics.

Enforcing these values when a task is completed ensures that completed tasks contribute meaningful data to summaries.

### Tradeoff

There are valid real-world cases where a user may want to retroactively add a completed task without knowing its exact duration or focus level.

For the scope of this application, I chose stronger data consistency over supporting that edge case.

---

## Task Lifecycle Timestamps

### Decision

Track:

- `created_at`
- `started_at`
- `completed_at`

### Why

Initially, I considered calculating weekly productivity using only `created_at` or `completed_at`.

That created ambiguity.

For example:

- a task may be created this week but not worked on
- a task may be created for future work
- a task may begin this week but finish later
- a task may have been created previously but completed this week

Adding `started_at` provides an additional signal indicating when work actually began.

This allows weekly summaries to distinguish between tasks that were:

- created
- started
- completed

during the selected period.

### Future Consideration

A more complete implementation could use an event-history or work-session model rather than relying only on lifecycle timestamps.

---

## CRUD Organization

### Decision

Separate CRUD operations by model, while keeping reusable database operations in a shared utilities module.

### Why

Model-specific CRUD files keep business logic close to the model it affects.

Generic operations such as adding, deleting, and retrieving records can remain reusable.

For example:

- `task_crud.py` contains task-specific update and validation behavior
- shared database helpers live in `crud/utilities.py`

### Tradeoff

For an application this small, the separation introduces more files than strictly necessary.

I chose the structure because it scales better as model-specific behavior increases.

---

## Weekly Summary Metrics

### Decision

Generate weekly metrics from task lifecycle events rather than relying on only one timestamp.

For a selected week, the backend separately finds tasks that were:

- created
- started
- completed

The resulting data is used to calculate:

- total tasks created
- total tasks started
- total tasks completed
- total tracked time
- average focus
- category distribution
- relevant task context

### Why

Using only `created_at` would overrepresent planned work.

Using only `completed_at` would ignore unfinished work that still consumed time and attention.

Using multiple lifecycle signals provides a more useful picture of weekly activity.

---

## Historical Summary State

### Decision

Persist generated weekly summaries rather than regenerating them every time they are viewed.

### Why

Persisting the generated result:

- avoids unnecessary model calls
- reduces API usage
- provides a stable historical record
- allows summaries to be indexed for semantic search

### Limitation

Tasks themselves are not fully versioned.

Because of this, regenerating an older summary after a task has been edited may produce slightly different results.

A production system could address this using task-event history or state snapshots.

---

## Related Task Snapshots

### Decision

Store a lightweight snapshot of relevant tasks with each weekly summary.

Each snapshot currently includes:

- task ID
- task name
- category
- status

### Why

Originally, weekly summaries stored only related task IDs.

That was not sufficient for semantic historical search because task IDs provide no meaningful semantic information to the embedding model.

Storing a lightweight snapshot preserves the context that existed when the weekly summary was generated and provides richer information for Chroma indexing.

### Tradeoff

This duplicates a small amount of task data.

That duplication is intentional because the weekly summary represents historical state rather than always depending on the current task row.

---

## SQLite as the Source of Truth

### Decision

Use SQLite as the authoritative application database.

### Why

SQLite provides:

- relational persistence
- minimal setup
- local portability
- predictable structured queries
- easy integration with SQLAlchemy

It also works well for the single-user scope of the challenge.

### Tradeoff

SQLite is not the database I would necessarily choose for a high-concurrency production deployment.

For this project, its simplicity is an advantage.

---

## Chroma for Semantic Retrieval

### Decision

Use Chroma as the local vector store.

### Why

Chroma provides:

- local persistence
- metadata support
- semantic querying
- stable document IDs
- simple upsert behavior

These features fit the application's historical-summary search requirements well.

### Alternative Considered

FAISS.

FAISS provides efficient vector similarity search, but Chroma offers a more convenient application-level interface for persisted documents and metadata.

---

## SQLite + Chroma Separation

### Decision

Treat Chroma as a derived semantic index rather than the source of truth.

### Flow

1. A weekly summary is persisted in SQLite.
2. A searchable representation is upserted into Chroma.
3. Chroma returns semantically ranked summary IDs during search.
4. Those IDs are hydrated from SQLite.
5. SQLite records are returned in the relevance order provided by Chroma.

### Why

This keeps responsibilities separate:

- SQLite handles authoritative structured data.
- Chroma handles semantic retrieval.

The vector index can be rebuilt if necessary without losing application state.

---

## Structured GenAI Output

### Decision

Use Pydantic models to validate Gemini responses.

Weekly summary generation expects:

- `summary: str`
- `suggestions: list[str]`

Historical search also returns a structured response.

### Why

Structured responses provide a predictable contract between the language model and the application.

This avoids depending on parsing arbitrary free-form model output.

---

## Pydantic-AI for Historical Search

### Decision

Use Pydantic-AI as the agent orchestration layer for historical search.

### Flow

The agent can call a historical-search tool that:

1. queries Chroma using the user's natural-language question
2. retrieves the most relevant summary IDs
3. hydrates the records from SQLite
4. returns the retrieved context to the agent

The agent then produces a structured answer using only the retrieved historical data.

### Why

The retrieval pipeline was intentionally implemented independently first.

Pydantic-AI was then added as an orchestration layer rather than replacing the existing retrieval logic.

This keeps the underlying retrieval system understandable, testable, and reusable outside of the agent.

---

## Time Attribution

### Current Decision

Store `time_spent_minutes` cumulatively on each task.

### Limitation

A task that spans multiple weeks cannot have its time perfectly attributed to the exact week in which each portion of the work occurred.

For example, if a task begins one week and is completed the next, its cumulative time does not contain enough information to determine how much effort occurred in each individual week.

### Future Improvement

One of the first improvements I would make is a separate time-entry or work-session model containing data such as:

- task ID
- start time
- end time
- duration

This would allow weekly analytics to attribute work much more accurately.

---

## Weekly Summary Scheduling

### Current Decision

Generate weekly summaries manually on demand.

### Why

Manual generation satisfies the challenge requirements and avoids introducing background scheduling infrastructure for a single-user prototype.

### Future Improvement

A production version could automatically generate the completed week's summary when the next week begins.

That would make historical summaries available without requiring user action.

---

## Docker

### Decision

Containerize both the frontend and backend with Docker Compose.

SQLite and Chroma use persistent Docker volumes.

### Why

The project includes several runtime dependencies across Python, Node, Nginx, SQLite, and Chroma.

Docker provides a reproducible setup and minimizes machine-specific configuration.

The final setup was validated by cloning the repository onto a separate machine and starting the application using:

    docker compose up --build

Persisted data was also verified to survive a normal Compose down/up cycle.