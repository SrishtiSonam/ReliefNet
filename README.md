# Stochastic Dynamic Post-Disaster Inventory Allocation Platform

## 📌 Project Overview
This is a full-stack AI-driven platform designed to optimize disaster relief allocation using a mixed fleet of **Trucks** and **UAVs (Drones)**. It integrates:
- **AI Forecasting**: Predicting demand surges using ARIMA, GARCH, and Transformer models.
- **Optimization**: Allocating resources using Mixed-Integer Programming (MIP) with OR-Tools.
- **Simulation**: A dynamic environment simulating road failures, aftershocks, and battery constraints.
- **Explainability**: SHAP values and RAG-based Q&A to explain AI decisions to human operators.
- **Interactive Dashboard**: A React-based frontend for real-time monitoring and control.

---

## 🚀 Features

### Backend (FastAPI + Python)
- **Forecasting Engine**: Predicts relief demand based on historical data and real-time signals.
- **Graph Neural Network (GNN)**: Embeds road network conditions to understand accessibility.
- **ADP & VFA**: Approximate Dynamic Programming with Value Function Approximation for long-term planning.
- **MIP Solver**: Optimizes immediate delivery schedules under capacity and time constraints.
- **Simulation Engine**: Simulates the disaster environment, including random road closures and demand spikes.

### Frontend (React + Tailwind)
- **Live Map**: Visualizes districts, open/closed roads, and active vehicle routes.
- **Dashboard**: Real-time KPIs for total demand, fulfilled orders, and active fleet status.
- **Control Panel**: Manually trigger simulation steps, run optimization, or override decisions.
- **Awareness Portal**: AI-powered safety assistant and educational resources.

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+** (Note: Python 3.14 is currently too new for the `ortools` solver. Use 3.10 or 3.11 for full functionality).
- **Node.js 18+** (For the frontend).

### ⚡ Windows Quick Start (Recommended)
We have provided a one-click setup script for Windows users.

1. **Open Terminal** (Command Prompt or PowerShell).
2. **Navigate to the project folder**:
   ```cmd
   C:\Users\Srish\AppData\Local\Programs\Python\Python311\python.exe --version
   C:\Users\Srish\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
   venv\Scripts\activate  
   pip install -r requirements.txt
   ```

## 🏃‍♂️ How to Run the Project

Follow these steps in order to start the full system.

### Step 1: Generate Synthetic Data
Before running the app, generate the test data (districts, roads, demand curves).
*Make sure your virtual environment is activated!*

```cmd
   venv\Scripts\activate 
   python data/generator.py
```
*Output: CSV files will be created in `data/`.*

### Step 2: Start the Backend API
Keep the terminal open and run:

```cmd
   python backend/app.py
```
*Success: You should see `Uvicorn running on http://0.0.0.0:8000`.*

### Step 3: Start the Frontend Dashboard
Open a **new** terminal window.

```cmd
cd frontend
npm install
npm start
```
*Success: The browser should open `http://localhost:3000` showing the dashboard.*

---

## 🧪 Running Simulations

### Standalone Simulation Demo
If you want to run a quick simulation without the frontend:

```cmd
venv\Scripts\activate
python backend/simulation/run_demo.py
```
This script will:
1. Initialize the environment.
2. Simulate 5 days of disaster relief.
3. Print inventory levels, demand, and allocation decisions to the console.

---

## 📂 Project Structure

```
├── backend/               # Python FastAPI Backend
│   ├── app.py             # Main Entry Point
│   ├── ml/                # AI Models (ARIMA, GNN, VFA)
│   ├── solver/            # Optimization Logic (OR-Tools)
│   ├── simulation/        # Environment Logic
│   └── routes/            # API Endpoints
├── frontend/              # React Frontend
│   ├── src/components/    # Dashboard, Map, ControlPanel
│   └── public/
├── data/                  # Generated CSV Datasets
├── notebooks/             # Jupyter Notebooks for Analysis
└── requirements.txt       # Python Dependencies
```

## ⚠️ Troubleshooting

- **"ModuleNotFoundError: No module named 'ortools'"**: 
  - This means you are likely running Python 3.14 or a version not supported by OR-Tools yet. The app will still run, but the solver will return empty allocations. To fix, install Python 3.10 or 3.11 and recreate the virtual environment.
  
- **"npm is not recognized"**:
  - Ensure Node.js is installed and added to your system PATH.

- **Frontend can't connect to Backend**:
  - Ensure the backend is running on port 8000. Check the console logs for errors.

