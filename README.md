# Smart Disaster Prediction, Decision & Resource Allocation System (SDPD)

A comprehensive disaster management system for India using MERN stack + FastAPI microservices architecture.

## 🏗️ Architecture

- **Frontend**: React + Vite + Tailwind CSS
- **Backend API Gateway**: Node.js + Express
- **ML Microservices**: FastAPI (Python)
  - Forecasting Service (Port 8001)
  - Routing Service (Port 8002)
  - Decision Service (Port 8003)
- **Database**: MongoDB
- **Orchestration**: Docker + Docker Compose

## 📋 Design Reference

This system is based on the design document: `/mnt/data/RG14.docx.pdf`

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git

### Running the Complete System

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd C:\Users\Srish\Desktop\ReliefNet
   ```

2. **Start all services with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:5000
   - **Forecasting Service**: http://localhost:8001
   - **Routing Service**: http://localhost:8002
   - **Decision Service**: http://localhost:8003
   - **MongoDB**: localhost:27017

4. **Stop all services**:
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes** (clears database):
   ```bash
   docker-compose down -v
   ```

## 🔧 Running Individual Services (Development)

### Backend Express

```bash
cd backend-express
npm install
npm run dev
```

### Forecasting Service

```bash
cd ml-fastapi/forecasting_service
pip install -r requirements.txt
python main.py
```

### Routing Service

```bash
cd ml-fastapi/routing_service
pip install -r requirements.txt
python main.py
```

### Decision Service

```bash
cd ml-fastapi/decision_service
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
sdpd-ai/
├── backend-express/          # Express API Gateway
│   ├── src/
│   │   ├── config.js
│   │   ├── models/
│   │   │   └── user.js
│   │   └── routes/
│   │       ├── auth.js
│   │       ├── forecasting_proxy.js
│   │       ├── routing_proxy.js
│   │       └── decision_proxy.js
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
├── ml-fastapi/               # ML Microservices
│   ├── forecasting_service/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── requirements.txt
│   │   ├── model_placeholder.pkl
│   │   └── Dockerfile
│   ├── routing_service/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── requirements.txt
│   │   ├── distance_matrix_placeholder.csv
│   │   └── Dockerfile
│   └── decision_service/
│       ├── main.py
│       ├── models.py
│       ├── requirements.txt
│       ├── dispatch_model_placeholder.pkl
│       └── Dockerfile
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DisasterPrediction.jsx
│   │   │   ├── ResourceMap.jsx
│   │   │   └── DispatchRecommendation.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   └── tailwind.css
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── api_endpoints.md
│   ├── integration_guide.md
│   └── design_reference.md
├── docker-compose.yml
└── README.md
```

## 🔑 Key Features

### 1. Dashboard
- System health monitoring
- Real-time statistics
- Recent activity feed
- Quick action buttons

### 2. Disaster Prediction
- Input disaster parameters (district, type, date, weather)
- ML-powered demand forecasting
- Resource requirement predictions (food, water, medical)
- Severity assessment

### 3. Resource Map
- Interactive Leaflet map of India
- District-wise resource visualization
- Real-time resource availability
- Severity indicators with color-coded circles

### 4. Dispatch Recommendation
- Intelligent dispatch decision system
- Multi-factor analysis (severity, weather, traffic, distance)
- Resource optimization
- Confidence scoring
- Alternative options

## 🔐 Authentication

The system includes JWT-based authentication:

**Register a new user:**
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@sdpd.gov.in","password":"admin123"}'
```

**Login:**
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sdpd.gov.in","password":"admin123"}'
```

## 🧪 Testing the System

### Test Forecasting Service
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

### Test Routing Service
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

### Test Decision Service
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

## 👥 Team Integration Guide

See [docs/integration_guide.md](docs/integration_guide.md) for detailed instructions on:
- Where to place your trained ML models
- How to integrate custom algorithms
- Data format requirements
- Model loading examples

## 📚 Documentation

- **[Architecture](docs/architecture.md)**: System design and component overview
- **[API Endpoints](docs/api_endpoints.md)**: Complete API reference with examples
- **[Integration Guide](docs/integration_guide.md)**: How to integrate ML models and data
- **[Design Reference](docs/design_reference.md)**: Link to original design document

## 🐛 Troubleshooting

### Services not starting
```bash
# Check logs
docker-compose logs backend-express
docker-compose logs forecasting_service

# Rebuild specific service
docker-compose up --build backend-express
```

### MongoDB connection issues
```bash
# Ensure MongoDB is healthy
docker-compose ps

# Check MongoDB logs
docker-compose logs mongo
```

### Port conflicts
If ports are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change host port (left side)
```

## 🔄 Environment Variables

Create `.env` files in each service directory for custom configuration:

**backend-express/.env**:
```env
MONGO_URI=mongodb://mongo:27017/sdpd_db
JWT_SECRET=your-secret-key
PORT=5000
```

**frontend/.env**:
```env
VITE_API_URL=http://localhost:5000
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues and questions:
- Check the [Integration Guide](docs/integration_guide.md)
- Review [API Documentation](docs/api_endpoints.md)
- Refer to design document: `/mnt/data/RG14.docx.pdf`

---

**Built with ❤️ for India's Disaster Management**
