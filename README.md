# DRS Quiz Platform (Team 5)

A distributed quiz platform built as a university project for the Distributed Computer Systems course.

This repository contains the team project implementation, plus a follow-up stabilization pass with practical fixes and UX improvements.

## Project Goal

The assignment was focused on designing and implementing a distributed system, not just a local CRUD app.

Main goals were:

- service separation and clear responsibilities
- SQL + NoSQL data model in one system
- inter-service communication
- asynchronous processing
- real-time updates

## What Was Built

- Microservice-based architecture with separate Main and Quiz services.
- Role-based access model (`PLAYER`, `MODERATOR`, `ADMIN`).
- Quiz approval workflow (`PENDING`, `APPROVED`, `REJECTED`).
- Real-time notifications using WebSockets.
- Asynchronous result processing and email notifications.
- Leaderboard and PDF reporting.
- Containerized local environment with Docker Compose.

## Tech Stack

- Frontend: Angular, TypeScript, RxJS
- Backend: Python, Flask, Flask-SocketIO, Flask-JWT-Extended
- Databases: PostgreSQL, MongoDB, Redis
- Infrastructure: Docker, Docker Compose, Nginx
- Reporting: ReportLab (PDF)

## Architecture Overview

### Frontend (`frontend/quiz-platform-ui`)

- Angular SPA
- Authentication, profile, quiz browsing/solving, leaderboard, results, review screens
- Nginx reverse proxy for API and WebSocket traffic

### Main Service (`backend/main-service`)

- User/auth domain (JWT, roles, profile management)
- Redis-backed token revocation and login-attempt lockout
- WebSocket event hub
- Proxy layer toward Quiz Service

### Quiz Service (`backend/quiz-service`)

- Quiz CRUD and moderation status flow
- Async submission processing
- Leaderboard and PDF report generation

### Data Stores

- PostgreSQL for relational user/auth data
- MongoDB for quiz/result domain
- Redis for cache and security-related state

## Security and Reliability

- JWT authentication with token revocation on logout
- Route-level role guards
- Internal service protection via `X-Internal-Token`
- Server-side validation on quiz submissions
- Async processing to keep user-facing responses fast

## Running Locally

### Prerequisites

- Docker
- Docker Compose

### Quick Reviewer Setup (2 Minutes)

Before first start, create service env files from committed templates:

1. Copy `backend/main-service/.env.example` to `backend/main-service/.env`
2. Copy `backend/quiz-service/.env.example` to `backend/quiz-service/.env`

Notes:

- `.env` files are intentionally gitignored, so reviewers create them locally.
- If you keep template values unchanged, default seeded admin password is `change-me-now`.

### Start

From project root:

```bash
docker compose up --build
```

Services:

- Frontend (dev): http://localhost:4200 (or `http://localhost:${FRONTEND_PORT}` if overridden in root `.env`)
- Main Service: http://localhost:5000
- Quiz Service: http://localhost:5001

### Default Admin

Main Service seeds/elevates an admin user on startup:

- Email: `admin@quizplatform.com`
- Password: value from `ADMIN_PASSWORD` in `backend/main-service/.env`
- For quick local testing with unchanged template values: `change-me-now`

## Environment Configuration

Service-level env files:

- `backend/main-service/.env`
- `backend/quiz-service/.env`

Templates:

- `backend/main-service/.env.example`
- `backend/quiz-service/.env.example`

For real email delivery, valid SMTP settings must be set in Main Service `.env`.

## Multi-Computer Usage (Same Network)

Yes, multiple users can use the same running instance at the same time.

If the stack is running on one host machine, other devices on the same LAN can open:

- `http://<HOST_LOCAL_IP>`

Notes:

- Do not use `localhost` from other devices.
- Allow inbound access through the host firewall.

## Team Project Note

This was developed as a team course project.

## CI/CD Automation

Repository now includes path-scoped GitHub Actions workflows:

- `.github/workflows/frontend-ci-cd.yml`
- `.github/workflows/backend-ci-cd.yml`

Both workflows:

- trigger on push to `main` when matching paths change
- build production images from `Dockerfile.prod`
- push images to GHCR (`ghcr.io/<dmtrhub>/...`)
- can optionally trigger Render deploy hooks

Secrets for deploy hooks:

- `FRONTEND_RENDER_DEPLOY_HOOK`
- `MAIN_SERVICE_RENDER_DEPLOY_HOOK`
- `QUIZ_SERVICE_RENDER_DEPLOY_HOOK`

Local Docker Compose is configured to use `Dockerfile.dev` variants for faster development iteration.

## Production Deployment

The project is deployed with managed cloud services and automated delivery from GitHub.

### Infrastructure Setup

- PostgreSQL is hosted on Neon.
- MongoDB is hosted on MongoDB Atlas.
- Redis is hosted on Render Key Value.
- Application runtime is split into 4 Render services:
- Frontend service (Angular + Nginx)
- Main service (Flask)
- Quiz service (Flask)
- Redis (Render Key Value)

### Deployment Flow

1. A new commit is pushed to `main`.
2. GitHub Actions builds production images with `Dockerfile.prod`.
3. Images are pushed to GHCR.
4. Render deploy hooks are triggered automatically.
5. Render pulls the latest image and deploys updated service versions.

### Service Links (Template)

Replace placeholders below with your real links.

- Frontend URL: `https://<your-frontend-service>.onrender.com`
- Main Service URL: `https://<your-main-service>.onrender.com`
- Quiz Service URL: `https://<your-quiz-service>.onrender.com`
- GitHub Actions (repository): `https://github.com/<owner>/<repo>/actions`
- GHCR package namespace: `https://github.com/<owner>?tab=packages`

## Screenshots Guide (Template)

Use this section to make the README reviewer-friendly and easy to verify.

### 1. Architecture and Infrastructure

Suggested screenshot: high-level architecture diagram (frontend, main, quiz, Neon, Atlas, Render Redis).

```md
![Architecture Overview](docs/images/architecture-overview.png)
```

Suggested screenshot: Render dashboard showing all 4 services.

```md
![Render Services](docs/images/render-services.png)
```

Suggested screenshot: Neon project/database overview.

```md
![Neon PostgreSQL](docs/images/neon-postgres.png)
```

Suggested screenshot: MongoDB Atlas cluster + database overview.

```md
![MongoDB Atlas](docs/images/mongodb-atlas.png)
```

### 2. CI/CD Pipeline

Suggested screenshot: successful backend workflow run.

```md
![Backend CI/CD Success](docs/images/backend-workflow-success.png)
```

Suggested screenshot: successful frontend workflow run.

```md
![Frontend CI/CD Success](docs/images/frontend-workflow-success.png)
```

Suggested screenshot: workflow step that triggers Render deploy hook.

```md
![Render Deploy Hook Trigger](docs/images/render-hook-trigger.png)
```

### 3. Application Walkthrough

Suggested screenshot: login page.

```md
![Login Page](docs/images/login-page.png)
```

Suggested screenshot: quiz list (player view).

```md
![Quiz List](docs/images/quiz-list.png)
```

Suggested screenshot: create quiz form.

```md
![Create Quiz](docs/images/create-quiz.png)
```

Suggested screenshot: quiz review page (moderator/admin).

```md
![Quiz Review](docs/images/quiz-review.png)
```

Suggested screenshot: leaderboard or results page.

```md
![Leaderboard](docs/images/leaderboard.png)
```

### 4. Verification Endpoints

Suggested screenshot: `/health` response for main service.

```md
![Main Service Health](docs/images/main-health.png)
```

Suggested screenshot: `/health` response for quiz service.

```md
![Quiz Service Health](docs/images/quiz-health.png)
```

## Current Gaps / Next Steps

- Add a formal automated test suite (unit/integration/e2e).
