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
- push images to GHCR (`ghcr.io/<owner>/...`)
- can optionally trigger Render deploy hooks

Optional secrets for deploy hooks:

- `FRONTEND_RENDER_DEPLOY_HOOK`
- `MAIN_SERVICE_RENDER_DEPLOY_HOOK`
- `QUIZ_SERVICE_RENDER_DEPLOY_HOOK`

Local Docker Compose is configured to use `Dockerfile.dev` variants for faster development iteration.

## Current Gaps / Next Steps

- Add a formal automated test suite (unit/integration/e2e).
- Add CI pipeline for validation on pull requests.
- Prepare production-grade deployment and scaling setup for WebSocket-heavy workloads.
