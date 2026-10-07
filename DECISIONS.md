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

    10-6 waiting on feedback from team to decide on the Tasks data model: #### Feedback Recieved - Moving forward with my design decisions.

        Need verification on focus level being completely user based, or provide a few options
        -> Design focus level to enumerate to 5 levels 1-5 for a good level of customization and analytics use
        Need verification on category, same issue, user based or provided options.
        -> Design category into 5 different categories. Personal, work, learning, fitness, other and the default "uncategorized" 

        --Will carry forward with the design around, leaving room to fix these. Designing around the idea that they are nullable when task is created, and required when task is marked as completed.--

    ## Tasks model decisions made:
        Created 3 enum objects to normalize the optional settings for the users.
        
        category: 
            Defaulted category to an UNCATEGORIZED enum value. Allows the user to wait to categorize until they've completed the task or come back later to update. Also guarantees there is a value to read for analytic reasons.
        Status:
            Same idea as category, the default value will go in as Planned enum value. 
        

    ## Weekly Summary model decisions made:
        10-6 - Evening:
            Mulling over more design questions, when generating the weekly summary, I have the option of 
            looking at all tasks based on completed_at time or created_at, this lead me down the rabbit hole of
            what is important signal. Multiple tasks with a planned but never completed status are obviously signal of something, however since tasks can be created into the future, it may be something that was prioritized over. DECISION best concession is to create a new start_at column that tracks when work actually started on a task. 
                    -> Future design possibilities, similar to a TTL, create a scheduled task set X days after task is scheduled to ask if user is ready to start. This can be variable.
## CRUD Decisions
    First main decision, as I do with other projects and apps, I chose to break the CRUD functionality into individual files for each model, and a general utilities file that contains operations that can be shared between models, like the general add/remove.

    Task_crud:
        Main functions are very simple, just pointing toward utilities. The update function is the important one that contains some business logic that validates input data before changing the task object.