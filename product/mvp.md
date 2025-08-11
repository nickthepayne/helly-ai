
# MVP for Helly AI

## Product spec

Everything in the MVP is API only. We are not building a UI.

### Setting up a team

As a manager I need to define my team members. A team member needs to
- Have a name (e.g. Max Muster)
- Have a role (e.g. Lead engineer)
- Have a relationship with me (e.g. reports to me, peer)
- Have a start date

### Adding feedback

As a manager I can add feedback for a team member. Feedback needs to
- Describe a specific situation or a note to remember. Examples 
  - "Max took great ownership of the roadmap."
  - "This week I felt like Max was not very communicative. I think we should have a chat."
  - "I just heard that Max is feeling a bit burnt out. I should touch on that topic in the next call"

### Asking about a team member

As a manager I can ask questions about a team member. Examples
- "What should I discuss with Max tomorrow?"
- "What is Max's performance like?"
- "What should I do next with Max?"
- "I want to draft a feedback document for Max. Help me create a structure."

## Tech spec

### Software App

The "classic" app, meaning regular code w/o AI should be in a separate package /app.
This will include
- The REST API
- Database for keeping the feedback entries

Basically a simple CRUD app.

Tech stack for the software app:
- Kotlin
- Spring Boot
- PostgreSQL

### AI App

The AI app will be in a separate package /ai.
This is a standalone python application with its own API. The software app will call this API to get the AI generated responses.

On a regular basis (e.g. when a new feedback entry is added, or on a time schedule) all the feedback needs to be
inserted into a vector database that allows semantic search and conversational QA.
For now, we will wipe & re-insert all the feedback data whenever a change is made. We can have a simple api that allows
us to insert all the feedback data for a team member at once.

Important: The vector data needs to be filtered by team member (e.g. the ID) and time period, potentially more criteria later.
Choose an appropriate pattern to make this possible.

### Testing

We want to have integration tests at first that allow us to verify the end-to-end flow while keeping the exact implementation flexible.
This means: test on an API level. Only mock external calls. 
We want to test the software and ai apps separately.

When this MVP is completed, it should only have a small set of tests that verify that most important use cases.

### General guidelines

- Favour readability always. Follow the clean code principles.
- Separate concerns. 
- Always think API-first. Define a clear API contract and stick to it. The API must be business-oriented, no technical details.