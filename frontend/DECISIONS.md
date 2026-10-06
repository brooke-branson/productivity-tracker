## Backend persistence instead of localStorage

Decision:
Use FastAPI + SQLite.

Why:
The application already requires server-side GenAI and vector-search
functionality, so centralizing persistence avoids creating separate client
and server data models.

Alternatives considered:
- localStorage
- IndexedDB

Tradeoff:
Adds backend setup complexity, but simplifies data ownership and prevents
API credentials from reaching the browser.

## JavaScript instead of TypeScript

## GEN AI HEADS UP ##
    Front End is not my main area of expertise, I am very much a backend engineer who utilizes multiple different LLMs when designing and implementing FE components and design.
    For this challenge I will continue to lean on them for that, but will do less so than normal so I can showcase my ability to actually learn on the fly.

Decision:
Use JavaScript for the React frontend.

Why:
The challenge does not require TypeScript, and JavaScript reduces setup
and implementation overhead for a one-week build. Additionally I have more expereince writing in JS. 

Tradeoff:
TypeScript would provide stronger compile-time guarantees, but the added
type-definition work is not necessary for the scope of this project.