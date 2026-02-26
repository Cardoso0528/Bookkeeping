# Bookkeeping App

An AI-powered bookkeeping application for small businesses, featuring multi-tenant architecture, JWT authentication, and a modern React frontend.

## Tech Stack

**Backend**
- Java 17, Spring Boot 3.2.1
- Spring Data JPA, Spring Security
- PostgreSQL 15
- Flyway (database migrations)
- JWT authentication (access + refresh tokens)
- Google OAuth 2.0

**Frontend**
- React 19, TypeScript
- Vite, TailwindCSS
- React Router DOM

## Features

- **Multi-tenant architecture** — isolated data per business organization
- **Authentication** — email/password registration and login, Google OAuth, JWT with refresh token rotation
- **Transaction management** — track income and expenses with debit/credit entries
- **Account management** — bank accounts, credit cards, and more
- **Category management** — hierarchical categories with tax-deductible tracking
- **Dashboard** — financial overview and statistics
- **Document support** — receipt/invoice uploads (planned)
- **AI categorization** — automatic transaction categorization (planned)

## Project Structure

```
bookeeping-app/
├── src/main/java/com/bookkeeping/
│   ├── config/              # JPA and app configuration
│   ├── controller/          # REST API controllers
│   ├── domain/
│   │   ├── entity/          # JPA entities
│   │   └── enums/           # Enumerations
│   ├── dto/                 # Request/response DTOs
│   ├── repository/          # Spring Data JPA repositories
│   ├── security/            # JWT, filters, tenant context
│   └── service/             # Business logic services
├── src/main/resources/
│   ├── application.yml      # App configuration
│   └── db/migration/        # Flyway SQL migrations
├── frontend/                # React + TypeScript frontend
├── docker-compose.yml
├── Dockerfile
└── pom.xml
```

## Prerequisites

- Java 17+
- Node.js 18+
- PostgreSQL 15 (or Docker)

## Getting Started

### 1. Start the database

The easiest way is with Docker Compose, which starts PostgreSQL automatically:

```bash
docker-compose up -d postgres
```

This creates a `bookkeeping` database with user `bookkeeping_user` on port **5432**.

### 2. Run the backend

```bash
# Build and run with Maven
./mvnw spring-boot:run
```

The API starts on **http://localhost:8080**.

Flyway will automatically run database migrations on startup.

### 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend starts on **http://localhost:5173**.

### Run everything with Docker

```bash
docker-compose up -d
```

This starts both PostgreSQL and the Spring Boot application.

## Configuration

### Backend (`application.yml`)

| Variable | Description | Default |
|---|---|---|
| `JWT_SECRET` | Secret key for JWT signing (min 32 chars) | dev default (change in production) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | — |
| `SPRING_DATASOURCE_URL` | PostgreSQL connection URL | `jdbc:postgresql://localhost:5432/bookkeeping` |
| `SPRING_DATASOURCE_USERNAME` | Database username | `bookkeeping` |
| `SPRING_DATASOURCE_PASSWORD` | Database password | `dev_password` |

### Frontend (`.env`)

```
VITE_API_URL=http://localhost:8080/api
```

See `.env.example` in the `frontend/` directory.

## API Endpoints

All endpoints except `/api/auth/**` require a JWT token via the `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/google` | Login with Google OAuth |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout (revoke refresh token) |

### Transactions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/transactions` | List transactions (filterable) |
| GET | `/api/transactions/{id}` | Get transaction by ID |
| POST | `/api/transactions` | Create a transaction |
| PUT | `/api/transactions/{id}` | Update a transaction |
| DELETE | `/api/transactions/{id}` | Delete a transaction |

### Accounts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/accounts` | List all accounts |
| GET | `/api/accounts/{id}` | Get account by ID |
| POST | `/api/accounts` | Create an account |
| PUT | `/api/accounts/{id}` | Update an account |
| DELETE | `/api/accounts/{id}` | Delete an account |

### Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories` | List all categories |
| GET | `/api/categories/{id}` | Get category by ID |
| POST | `/api/categories` | Create a category |
| PUT | `/api/categories/{id}` | Update a category |
| DELETE | `/api/categories/{id}` | Delete a category |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/stats` | Get financial statistics |

## Database Schema

Managed by Flyway migrations in `src/main/resources/db/migration/`.

Key tables: `tenants`, `users`, `accounts`, `categories`, `transactions`, `documents`, `refresh_tokens`, `audit_logs`.

Monetary values use `DECIMAL(19,4)` for precision.

## Security

- JWT-based stateless authentication with refresh token rotation
- BCrypt password hashing (strength 12)
- Google OAuth server-side token verification
- Multi-tenant data isolation via `TenantContext` and `TenantFilter`
- CORS configured for the frontend origin
- Generic error messages to prevent account enumeration

## License

Private — all rights reserved.
