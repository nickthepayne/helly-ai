# Helly AI

Helly is your friendly people management assistant. 

This system supports team leads, managers, and people ops in managing feedback, performance, 1:1s, and goals with the help of lightweight AI agents. The goal is to create a modular, proactive "second brain" for people management — one that can plug into existing HR tools or stand alone.

---

## Strategic Vision

- **Build as a platform**: The core logic, memory, and agent behavior should be system-agnostic — easily integrated into tools like Lattice, BambooHR, Leapsome, etc.
- **Composable AI agents**: Each capability is managed by an autonomous agent (e.g., FeedbackAgent, FollowUpAgent) that can run standalone or be embedded via API/webhook.
- **Pluggable architecture**: Slack/Teams bots, web widgets, REST/gRPC interfaces — focus on integration rather than full-stack replacement.

---

## Core Use Cases

### 1. **Feedback Catalog on the Go**
- Write feedback any time (voice, text, Slack, etc.)
- System tags person, date, topic, and sentiment automatically
- Stores feedback in an ongoing timeline ("performance catalog")

**AI Role:**
- Extracts themes and tags
- Detects praise vs concern
- Suggests reframing if tone is harsh
- Connects feedback to goals or 1:1 agendas

---

### 2. **Proactive Follow-ups**
- Detects silence or imbalance ("You haven’t said anything about Max in 2 months")
- Prompts for check-ins based on gaps or negative trends

**AI Role:**
- FollowUpAgent monitors interaction frequency
- Nudges manager with lightweight prompts
- Tracks omissions, not just activity

---

### 3. **1:1 Agenda Management**
- Drafts agendas from recent feedback, goals, and loose ends
- Reminds about unresolved issues, team dynamics, or goal blockers
- Generates actionable talking points

**AI Role:**
- OneOnOneAgent analyzes recent data
- Highlights urgent or time-sensitive items
- Suggests framing or priority

---

### 4. **Goal Setting & Tracking**
- Create SMART goals, link to feedback and actions
- Track updates passively (via feedback, performance data)
- Get reminders when progress is stalled

**AI Role:**
- GoalAgent helps define clear, aligned objectives
- Monitors goal staleness or drift
- Suggests next actions based on historical behavior

---

## Technical Design Principles

- **Event-driven agents** with persistent memory (DB + embeddings)
- **Modular agents** with clear boundaries and APIs:
  - `FeedbackAgent`
  - `FollowUpAgent`
  - `OneOnOneAgent`
  - `GoalAgent`
- **Context-aware RAG**: Retrieval-Augmented Generation for summarizing past feedback, goals, 1:1s
- **Interoperable I/O**:
  - Slack, Teams, Email, Mobile input
  - Expose APIs and webhooks for HRIS and PM system integration

---

## Sample Prompts / Interactions

- "Log feedback for Max: took great ownership of the roadmap."
- "Who haven’t I talked about lately?"
- "What should I discuss with Lisa tomorrow?"
- "Remind me to follow up on Alex’s new goal next week."
- "Summarize Julia’s Q2 performance."

---

## Future Features (TBD)

- Timeline view per person with feedback, goals, and 1:1s
- Sentiment heatmaps for teams
- Voice-to-feedback input with tagging
- Shared vs private notes toggle
- HRIS sync (e.g., BambooHR, HiBob, Personio)
- Exportable review packets

---

## What’s Next

- Define MVP loop (e.g. FeedbackAgent + FollowUpAgent)
- Build memory backend (structured + vector)
- Ship as Slackbot or web extension first
- Focus on *one tight loop* that shows agent value