# ABDM Gateway Service

The ABDM Gateway is a FastAPI-based microservice that routes requests between Health Information Providers (HIPs), Health Information Users (HIUs), and the Consent Manager in the ABDM (Ayushman Bharat Digital Mission) ecosystem.

## Features

- Fast, asynchronous request handling using FastAPI
- JWT-based authentication middleware
- Comprehensive request/response logging
- MongoDB integration with Motor (async driver)
- CORS support for cross-origin requests
- Health check and status endpoints
- Environment-based configuration using Pydantic Settings
- Docker containerization

## Architecture

### Core Components

1. **main.py** - FastAPI application initialization with lifecycle management
2. **config.py** - Environment configuration using Pydantic Settings
3. **middleware/logging.py** - Request/response logging middleware
4. **middleware/auth.py** - JWT authentication middleware with password hashing utilities

### Key Endpoints

- `GET /` - Service information
- `GET /health` - Health check endpoint
- `GET /status` - Detailed service status
- Additional ABDM routing endpoints (to be implemented)

## Installation

### Local Development

1. Clone the repository
2. Navigate to the gateway service directory:
   ```bash
   cd abdm-local-dev-kit/services/gateway
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. Start the service:
   ```bash
   python main.py
   ```

The service will start on `http://localhost:8090`

### Docker

1. Build the image:
   ```bash
   docker build -t abdm-gateway:latest .
   ```

2. Run the container:
   ```bash
   docker run -p 8090:8090 \
     -e MONGODB_URL=mongodb://mongo:27017 \
     -e SECRET_KEY=your-secret-key \
     abdm-gateway:latest
   ```

## Configuration

Environment variables are loaded from `.env` file or system environment. See `.env.example` for all available options.

### Key Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8090 | Server port |
| `MONGODB_URL` | mongodb://localhost:27017 | MongoDB connection URL |
| `MONGODB_DATABASE` | abdm_gateway | MongoDB database name |
| `SECRET_KEY` | your-secret-key-change-in-production | JWT secret key |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `HIP_SERVICE_URL` | http://hip:8091 | HIP service URL |
| `HIU_SERVICE_URL` | http://hiu:8092 | HIU service URL |
| `CONSENT_MANAGER_URL` | http://consent-manager:8093 | Consent Manager service URL |

## API Documentation

Once the service is running, access the interactive API documentation:

- Swagger UI: `http://localhost:8090/docs`
- ReDoc: `http://localhost:8090/redoc`

## Authentication

The gateway uses JWT (JSON Web Token) authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-token>
```

Exempt routes that don't require authentication:
- `GET /health`
- `GET /`
- `GET /docs`
- `GET /openapi.json`
- `GET /redoc`

## Middleware

### Logging Middleware
- Logs all incoming requests with method, path, and client IP
- Logs response status code and processing time
- Adds request ID tracking via `X-Request-ID` header

### Auth Middleware
- Validates JWT tokens from the `Authorization` header
- Supports token creation and verification
- Password hashing using bcrypt
- Exempt routes bypass authentication

## Database

The service uses MongoDB for data storage. Ensure MongoDB is running and accessible via the configured `MONGODB_URL`.

### Connection Lifecycle

- Connects to MongoDB on startup (lifespan startup event)
- Disconnects from MongoDB on shutdown (lifespan shutdown event)
- Verifies connection with a ping command

## Error Handling

The service includes centralized error handling:

- HTTP exceptions return standardized JSON responses
- Unhandled exceptions are logged with full traceback
- All errors include appropriate HTTP status codes

## Development

### Project Structure

```
gateway/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── .env.example          # Example environment variables
├── middleware/
│   ├── __init__.py
│   ├── logging.py        # Request/response logging
│   └── auth.py           # JWT authentication
└── README.md
```

### Running Tests

```bash
pytest
```

### Code Quality

Ensure code quality with linting and formatting:

```bash
# Install dev dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Lint
flake8 .
```

## Dependencies

- **fastapi** (0.109.0) - Modern web framework for building APIs
- **uvicorn** (0.27.0) - ASGI server
- **pydantic** (2.5.3) - Data validation using Python type hints
- **motor** (3.3.2) - Async MongoDB driver
- **python-jose** (3.3.0) - JWT authentication
- **passlib** (1.7.4) - Password hashing
- **httpx** (0.26.0) - Async HTTP client
- **python-dateutil** (2.8.2) - Date utilities

## Troubleshooting

### MongoDB Connection Issues
- Verify MongoDB is running
- Check `MONGODB_URL` is correctly configured
- Ensure network connectivity to MongoDB

### JWT Token Errors
- Verify `SECRET_KEY` matches across services
- Check token hasn't expired
- Ensure correct `Authorization` header format

### Port Already in Use
- Change the `PORT` environment variable
- Or stop the service using port 8090

## Future Enhancements

- Request/response validation against ABDM specifications
- Rate limiting and throttling
- Service discovery integration
- Distributed tracing with OpenTelemetry
- Metrics collection and monitoring
- Gateway-specific routing logic for ABDM flows
