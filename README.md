# ReliefNet - Disaster Management Platform for India

A comprehensive multi-role disaster management platform featuring real-time vehicle tracking, AI-powered resource allocation, and public relief services.

## 🎯 Overview

ReliefNet provides three specialized interfaces:

1. **State Dashboard (SDMA)** - State-level disaster management and resource coordination
2. **District Dashboard (DDMA)** - District-level operations and local response management
3. **Public Portal** - Citizen services, relief requests, and safety information

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.8+
- **Real-time Communication**: WebSocket for live vehicle tracking
- **AI/ML**: Placeholder functions for forecasting, optimization, and explainable AI
- **Data**: Mock datasets representing Indian districts, warehouses, and resources

### Frontend (React)
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **Maps**: React-Leaflet with OpenStreetMap tiles
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **Styling**: Vanilla CSS with modern design system

## 📋 Features

### State Dashboard (SDMA)
- ✅ Interactive India map with district boundaries
- ✅ Real-time vehicle tracking (trucks, UAVs, ambulances)
- ✅ Surge forecasting with 7-day predictions
- ✅ Explainable AI (SHAP-style feature importance)
- ✅ Resource allocation dashboard
- ✅ Warehouse stock management
- ✅ Live statistics and metrics

### District Dashboard (DDMA)
- ✅ District-level map with warehouses and roadblocks
- ✅ Public request viewer and management
- ✅ Roadblock reporting system
- ✅ Local warehouse inventory
- ✅ Mission planning interface
- ✅ Real-time alerts

### Public Portal
- ✅ Shelter locator map
- ✅ Relief request submission form
- ✅ Visual request status tracker
- ✅ Safety guidelines
- ✅ Emergency contact numbers
- ✅ Active disaster alerts

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **npm**: 8.x or higher

### Installation

#### 1. Clone the Repository

```bash
cd C:\Users\Srish\Desktop\ReliefNet
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend
py -3.11 -m venv venv
.\venv\Scripts\activate
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend will start on **http://localhost:8000**

- API Documentation: http://localhost:8000/docs
- WebSocket endpoint: ws://localhost:8000/ws/vehicles

#### 3. Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on **http://localhost:5173**

## 📡 API Endpoints

### Dashboard & Data
- `GET /dashboard?role={state_admin|district_admin|public}` - Role-based dashboard data
- `GET /districts_geo` - District boundaries as GeoJSON
- `GET /vehicles` - Current vehicle positions
- `GET /forecast?district={name}&days={n}` - Surge forecast

### AI & Optimization
- `POST /optimize_allocation` - Resource optimization
- `GET /explain_allocation?district_id={id}` - Explainable AI insights

### Public Services
- `GET /public_requests` - List relief requests
- `POST /public_requests` - Submit new request
- `GET /roadblocks` - List roadblocks
- `POST /roadblocks` - Report roadblock

### Real-time
- `WebSocket /ws/vehicles` - Live vehicle position updates

## 🎨 Visual Components

### Maps
- Interactive OpenStreetMap integration
- Color-coded risk zones (green → yellow → red)
- Animated vehicle markers
- District polygons with hover information
- Route visualization

### Charts
- **Line Charts**: Surge forecasting trends
- **Bar Charts**: Resource stock levels, feature importance
- **Status Trackers**: Visual request progress timeline

### Dashboards
- Real-time statistics cards
- Warehouse inventory displays
- Vehicle status panels
- Alert notifications

## 🤖 AI/ML Placeholder Functions

All AI functions are implemented as structured placeholders:

1. **`forecast()`** - Generates mock surge predictions
2. **`optimize_allocation()`** - Returns optimal resource distribution
3. **`explain_allocation()`** - Provides SHAP-style explanations
4. **`simulate_vehicle_movements()`** - Updates vehicle GPS coordinates
5. **`validate_public_request()`** - Request validation logic

## 📊 Mock Datasets

The platform includes placeholder data for:

- **Districts**: 8 major Indian cities with coordinates
- **Warehouses**: Stock levels for food, water, medicine, blankets, tents
- **Vehicles**: Trucks, UAVs, ambulances with real-time positions
- **Shelters**: Capacity and facility information
- **Public Requests**: Relief assistance requests
- **Roadblocks**: Affected areas and severity levels

## 🎯 Usage

### 1. Start Both Servers

Ensure both backend (port 8000) and frontend (port 5173) are running.

### 2. Access the Application

Open your browser and navigate to: **http://localhost:5173**

### 3. Select Your Role

Choose from three options:
- **State Dashboard** - For state-level administrators
- **District Dashboard** - For district-level officers
- **Public Portal** - For citizens

### 4. Explore Features

- **State Dashboard**: View live vehicle tracking, check surge forecasts, analyze AI explanations
- **District Dashboard**: Manage public requests, report roadblocks, monitor local warehouses
- **Public Portal**: Submit relief requests, find shelters, view safety guidelines

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` to modify:
- CORS origins
- WebSocket update frequency
- Mock data parameters

### Frontend Configuration

Edit `frontend/src/services/api.js` to change:
- API base URL
- WebSocket endpoint

## 📁 Project Structure

```
ReliefNet/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── ai_placeholders.py      # AI/ML functions
│   ├── mock_data.py            # Mock datasets
│   └── requirements.txt        # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/         # Reusable components
    │   │   ├── MapView.jsx
    │   │   ├── SurgeChart.jsx
    │   │   ├── ExplainableAI.jsx
    │   │   ├── ResourceDashboard.jsx
    │   │   ├── PublicRequestForm.jsx
    │   │   └── RequestStatusTracker.jsx
    │   ├── pages/              # Main pages
    │   │   ├── Login.jsx
    │   │   ├── StateDashboard.jsx
    │   │   ├── DistrictDashboard.jsx
    │   │   └── PublicPortal.jsx
    │   ├── services/
    │   │   └── api.js          # API service layer
    │   ├── App.jsx             # Main app component
    │   ├── main.jsx            # Entry point
    │   └── index.css           # Global styles
    ├── package.json
    └── vite.config.js
```

## 🎨 Design System

The platform uses a modern dark theme with:

- **Primary Color**: Blue (#2563eb)
- **Success**: Green (#22c55e)
- **Warning**: Orange (#f59e0b)
- **Danger**: Red (#ef4444)
- **Background**: Dark slate tones
- **Typography**: System fonts with clear hierarchy
- **Animations**: Smooth transitions and hover effects

## 🔮 Future Enhancements

To productionize this platform:

1. **Real AI/ML Models**
   - Integrate actual forecasting models
   - Implement real optimization algorithms
   - Add genuine SHAP explanations

2. **Database Integration**
   - PostgreSQL with PostGIS for geospatial data
   - Redis for caching and real-time data
   - MongoDB for flexible document storage

3. **Authentication**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - OAuth integration

4. **Real-time GPS**
   - Integration with vehicle tracking systems
   - Live route optimization
   - ETA calculations

5. **Data Sources**
   - India Meteorological Department (IMD) API
   - ISRO satellite data
   - Data.gov.in datasets
   - OpenStreetMap extracts

## 📝 License

This is a demonstration project for disaster management platform development.

## 👥 Support

For questions or issues, please refer to the API documentation at http://localhost:8000/docs when the backend is running.

---

**Built with ❤️ for disaster resilience in India**
