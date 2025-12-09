# Quick Start Guide

## ✅ Backend Server (Running Successfully)

The backend is currently running on **http://localhost:8000**

- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/vehicles
- **Status**: ✅ Active

## ⚠️ Frontend Server (Needs Manual Start)

Due to a Node.js v22 compatibility issue with Vite, please start the frontend manually:

### Option 1: Using npm (Recommended)

```bash
cd C:\Users\Srish\Desktop\ReliefNet\frontend
npm run dev
```

### Option 2: If npm fails, try with --force

```bash
cd C:\Users\Srish\Desktop\ReliefNet\frontend
npm run dev -- --force
```

### Option 3: Alternative Vite start

```bash
cd C:\Users\Srish\Desktop\ReliefNet\frontend
npx vite
```

Once started, the frontend will be available at: **http://localhost:5173**

## 🚀 Access the Application

1. Open your browser
2. Navigate to: **http://localhost:5173**
3. You'll see three role options:
   - **State Dashboard (SDMA)** - State-level management
   - **District Dashboard (DDMA)** - District operations
   - **Public Portal** - Citizen services

## 🔧 Troubleshooting

If the frontend still has issues:

1. **Clear node_modules and reinstall:**
   ```bash
   cd C:\Users\Srish\Desktop\ReliefNet\frontend
   rmdir /s /q node_modules
   npm install
   npm run dev
   ```

2. **Use a different Node version (if available):**
   - Node v18 or v20 are more stable with Vite
   - Use nvm to switch: `nvm use 18`

3. **Check for port conflicts:**
   - Make sure port 5173 is not in use
   - Try a different port: `npm run dev -- --port 3000`

## 📊 What's Running

- ✅ **Backend API**: Port 8000 (Active)
- ⏳ **Frontend**: Port 5173 (Start manually)

## 🎯 Features to Test

Once both servers are running:

1. **State Dashboard**: Real-time vehicle tracking, surge forecasts, AI explanations
2. **District Dashboard**: Public requests, roadblock reporting
3. **Public Portal**: Relief requests, shelter locator, status tracking
