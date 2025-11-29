# API Endpoints Reference

Complete API documentation for all services in the SDPD system.

## Base URLs

- **Frontend**: http://localhost:3000
- **Backend Express**: http://localhost:5000
- **Forecasting Service**: http://localhost:8001
- **Routing Service**: http://localhost:8002
- **Decision Service**: http://localhost:8003

---

## Backend Express API

### Authentication Endpoints

#### POST /register

Register a new user account.

**Request:**
```json
{
  "username": "admin",
  "email": "admin@sdpd.gov.in",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "admin",
    "email": "admin@sdpd.gov.in",
    "role": "user"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@sdpd.gov.in",
    "password": "securepassword123"
  }'
```

---

#### POST /login

Authenticate and get JWT token.

**Request:**
```json
{
  "email": "admin@sdpd.gov.in",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "admin",
    "email": "admin@sdpd.gov.in",
    "role": "user"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sdpd.gov.in",
    "password": "securepassword123"
  }'
```

---

#### GET /protected

Example protected route requiring authentication.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200 OK):**
```json
{
  "message": "Access granted to protected resource",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "admin",
    "email": "admin@sdpd.gov.in"
  }
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:5000/protected \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### ML Service Proxy Endpoints

#### POST /api/forecast/demand

Proxy to Forecasting Service for disaster demand prediction.

**Request:**
```json
{
  "district": "Mumbai",
  "disaster_type": "flood",
  "date_features": {
    "month": 7,
    "season": "monsoon"
  },
  "other_features": {
    "population": 12442373,
    "rainfall_mm": 250
  }
}
```

**Response (200 OK):**
```json
{
  "predicted_demand": {
    "food": 15000,
    "water": 25000,
    "medical": 1200
  },
  "severity": "high",
  "model_version": "placeholder-v1.0",
  "confidence": 0.85
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Mumbai",
    "disaster_type": "flood",
    "date_features": {"month": 7, "season": "monsoon"},
    "other_features": {"population": 12442373, "rainfall_mm": 250}
  }'
```

---

#### POST /api/routing/optimal-route

Proxy to Routing Service for route optimization.

**Request:**
```json
{
  "from_district": "Mumbai",
  "to_district": "Pune",
  "vehicle_type": "ambulance",
  "constraints": {
    "avoid_tolls": false,
    "max_distance_km": 500
  }
}
```

**Response (200 OK):**
```json
{
  "route": ["Mumbai", "Pune"],
  "travel_time_min": 150.5,
  "cost": 1250.0,
  "distance_km": 150.0,
  "model_version": "placeholder-v1.0"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/routing/optimal-route \
  -H "Content-Type: application/json" \
  -d '{
    "from_district": "Mumbai",
    "to_district": "Pune",
    "vehicle_type": "ambulance",
    "constraints": {}
  }'
```

---

#### POST /api/decision/recommend

Proxy to Decision Service for dispatch recommendations.

**Request:**
```json
{
  "severity": "high",
  "weather": "clear",
  "traffic": "low",
  "distance": 50.0,
  "hospital_capacity": 80,
  "ambulance_availability": 5,
  "drone_availability": 2,
  "truck_availability": 3,
  "time_of_day": "afternoon"
}
```

**Response (200 OK):**
```json
{
  "decision": "Deploy 3 ambulance(s) + Deploy 1 drone for aerial assessment",
  "confidence": 0.85,
  "explanation": "High severity with favorable weather conditions. Long distance (50.0km) may require air support.",
  "model_version": "rule-based-v1.0",
  "alternative_options": [
    "Consider helicopter deployment for faster response"
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/decision/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "high",
    "weather": "clear",
    "traffic": "low",
    "distance": 50,
    "hospital_capacity": 80,
    "ambulance_availability": 5,
    "drone_availability": 2
  }'
```

---

#### GET /health

Health check endpoint for backend service.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "backend-express",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "mongodb": "connected"
}
```

**cURL Example:**
```bash
curl http://localhost:5000/health
```

---

## Forecasting Service API (FastAPI)

### GET /

Service health check and information.

**Response (200 OK):**
```json
{
  "service": "forecasting_service",
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": false,
  "endpoints": {
    "forecast": "POST /forecast/demand"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8001/
```

---

### POST /forecast/demand

Direct access to forecasting service (bypassing Express proxy).

**Request/Response**: Same as `/api/forecast/demand` above

**cURL Example:**
```bash
curl -X POST http://localhost:8001/forecast/demand \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Delhi",
    "disaster_type": "earthquake",
    "date_features": {"month": 3},
    "other_features": {}
  }'
```

---

## Routing Service API (FastAPI)

### GET /

Service health check and information.

**Response (200 OK):**
```json
{
  "service": "routing_service",
  "status": "healthy",
  "version": "1.0.0",
  "distance_matrix_loaded": true,
  "routes_available": 23,
  "endpoints": {
    "routing": "POST /routing/optimal-route"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8002/
```

---

### POST /routing/optimal-route

Direct access to routing service.

**Request/Response**: Same as `/api/routing/optimal-route` above

**cURL Example:**
```bash
curl -X POST http://localhost:8002/routing/optimal-route \
  -H "Content-Type: application/json" \
  -d '{
    "from_district": "Delhi",
    "to_district": "Jaipur",
    "vehicle_type": "truck",
    "constraints": {}
  }'
```

---

## Decision Service API (FastAPI)

### GET /

Service health check and information.

**Response (200 OK):**
```json
{
  "service": "decision_service",
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": false,
  "decision_mode": "rule-based",
  "endpoints": {
    "decision": "POST /decision/recommend"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8003/
```

---

### POST /decision/recommend

Direct access to decision service.

**Request/Response**: Same as `/api/decision/recommend` above

**cURL Example:**
```bash
curl -X POST http://localhost:8003/decision/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "critical",
    "weather": "storm",
    "traffic": "high",
    "distance": 100,
    "hospital_capacity": 30,
    "ambulance_availability": 2,
    "drone_availability": 0
  }'
```

---

## Error Responses

All services return consistent error responses:

### 400 Bad Request
```json
{
  "error": "Validation error",
  "message": "Invalid input parameters",
  "details": "district field is required"
}
```

### 401 Unauthorized
```json
{
  "error": "Access token required"
}
```

### 403 Forbidden
```json
{
  "error": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "error": "Route not found",
  "path": "/api/invalid"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

### 503 Service Unavailable
```json
{
  "error": "Forecasting service unavailable",
  "message": "Unable to connect to forecasting service. Please try again later."
}
```

---

## Interactive API Documentation

FastAPI services provide interactive API documentation:

- **Forecasting Service**: http://localhost:8001/docs
- **Routing Service**: http://localhost:8002/docs
- **Decision Service**: http://localhost:8003/docs

These provide Swagger UI for testing endpoints directly in the browser.

---

## Rate Limiting

Currently not implemented. For production, consider:
- Express rate limiter middleware
- API gateway rate limiting
- Per-user/per-IP limits

---

## Versioning

Current version: `v1.0.0`

Future API versions should use URL versioning:
- `/api/v1/forecast/demand`
- `/api/v2/forecast/demand`
