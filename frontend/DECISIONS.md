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

## Data Models

    10-6 waiting on feedback from team to decide on the Tasks data model:
        Need verification on focus level being completely user based, or provide a few options
        Need verification on category, same issue, user based or provided options.

        Will carry forward with the design around, leaving room to fix these. Designing around the idea that they are nullable when task is created, and required when task is marked as completed.

    ## Tasks model decisions made:
        Created 3 enum objects to normalize the optional settings for the users.
        
        category: 
            Defaulted category to an UNCATEGORIZED enum value. Allows the user to wait to categorize until they've completed the task or come back later to update. Also guarantees there is a value to read for analytic reasons.
        Status:
            Same idea as category, the default value will go in as Planned enum value. 
        

