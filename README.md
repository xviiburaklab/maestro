## This project is a simulation of a production-like system designed for learning and experimentation._

#  AI Agent-Orchestrated Microservice Platform

This project is a microservice-based system where an AI agent
orchestrates multi-step workflows across services.

Instead of hardcoding flows, an AI planner generates an execution plan
(as a DAG), and the system executes it step by step. If something fails
along the way, compensation logic kicks in automatically (Saga-style) to
keep things consistent.

------------------------------------------------------------------------

##  Why this project?

Most backend projects focus on CRUD APIs.\
This project explores what happens when:

-   workflows become multi-step and distributed\
-   failures happen in the middle of execution\
-   systems need to recover automatically\
-   AI is used to dynamically plan actions

The goal here is to simulate a **real-world backend challenge**:\
coordinating multiple services reliably under failure conditions.

It's also an attempt to combine: - microservice architecture\
- async processing\
- orchestration patterns\
- and AI-driven decision making

in a single, cohesive system.

------------------------------------------------------------------------

##  What this project focuses on

-   Mixing **sync + async communication** (REST + Celery)
-   Handling failures with a **Saga-like approach**
-   Simulating an **AI-driven workflow planner**
-   Observability with **correlation IDs + audit logs**
-   Keeping things close to a **production-ready setup**

------------------------------------------------------------------------

## Key Features

-   **Hybrid orchestration**\
    REST APIs for immediate actions, Celery/Redis for background jobs.

-   **Saga-lite pattern**\
    Each step has a compensation path if something goes wrong.

-   **AI planner (mocked)**\
    A fake LLM generates execution plans as DAGs.

-   **Distributed tracing**\
    `X-Correlation-ID` is propagated across all services.

-   **Centralized auditing**\
    All steps are logged into MongoDB for later inspection.

-   **Production-minded setup**\
    JWT auth, RBAC, structured logs, Dockerized services.

------------------------------------------------------------------------

##  Tech Stack

-   **FastAPI (Python)** -- API layer\
-   **MySQL** -- relational data (auth, users, workflow state)\
-   **MongoDB** -- audit logs & traces\
-   **Redis** -- broker & caching\
-   **Celery** -- async task processing

------------------------------------------------------------------------

## Architecture

``` mermaid
flowchart LR
    Client --> API_Gateway

    API_Gateway --> Auth_Service
    API_Gateway --> Orchestrator

    Orchestrator --> User_Service
    Orchestrator --> Worker

    Worker --> Redis
    Worker --> MongoDB

    Auth_Service --> MySQL
    User_Service --> MySQL

    Orchestrator --> MongoDB

    Worker --> Notification_Service
```

------------------------------------------------------------------------

##  Getting Started

### Requirements

-   Docker
-   Docker Compose

### Run the project

``` bash
docker-compose up --build
```

That's it. All services should start together.

------------------------------------------------------------------------

##  API Flow

### 1. Register

    POST /auth/register

### 2. Login

    POST /auth/login

Returns a JWT token.

------------------------------------------------------------------------

### 3. Trigger a workflow

    POST /orchestrator/orchestrate
    Authorization: Bearer <your_token>

Example:

``` json
{
  "user_input": "Create a new user with admin privileges"
}
```

------------------------------------------------------------------------

### 4. Check execution status

    GET /orchestrator/executions/{job_id}

------------------------------------------------------------------------

## Example Workflow Execution

Let's say the system receives this request:

``` json
{
  "user_input": "Create a new user with admin privileges"
}
```

### Step-by-step:

1.  **AI Planner**
    -   Generates a plan like:
        -   Create user
        -   Assign role
        -   Send notification
2.  **Orchestrator**
    -   Executes steps one by one
3.  **Worker (Celery)**
    -   Handles async tasks

------------------------------------------------------------------------

###  Success case

-   User is created\
-   Role is assigned\
-   Notification is sent\
-   Execution marked as **COMPLETED**

------------------------------------------------------------------------

### Failure case (Saga in action)

Example: - User created ✅\
- Role assignment fails ❌

System will: - Trigger compensation\
- Delete created user (rollback)

Final state: - System remains consistent\
- Execution marked as **FAILED + COMPENSATED**

------------------------------------------------------------------------

##  Demo

There's a simple script (`demo.py`) that walks through:

-   user registration\
-   login\
-   successful workflow\
-   failed workflow + compensation

Run it:

``` bash
pip install requests
python demo.py
```

------------------------------------------------------------------------

##  Services Overview

-   **api-gateway** → Entry point, auth validation, routing\
-   **auth-service** → JWT, RBAC, authentication\
-   **user-service** → user/profile management\
-   **orchestrator** → AI planning + workflow state machine\
-   **worker** → Celery workers + compensation logic\
-   **audit-service** → MongoDB logging\
-   **notification-service** → mock email/SMS

------------------------------------------------------------------------

##  Notes

This project is mainly a **learning/portfolio project** focused on: -
distributed systems basics\
- orchestration patterns\
- async processing\
- AI-assisted workflows (simulated)
=======
# maestro
AI-powered microservice orchestration platform with Saga-based fault tolerance and distributed workflow execution.
>>>>>>> 9a7b5ab54f8ee6f203eaf96f3412ac35b74fb452
