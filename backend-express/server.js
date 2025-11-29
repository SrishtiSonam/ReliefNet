const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const morgan = require('morgan');
const config = require('./src/config');

// Import routes
const authRoutes = require('./src/routes/auth');
const forecastingProxy = require('./src/routes/forecasting_proxy');
const routingProxy = require('./src/routes/routing_proxy');
const decisionProxy = require('./src/routes/decision_proxy');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'backend-express',
        timestamp: new Date().toISOString(),
        mongodb: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected'
    });
});

// Mount routes
app.use('/api/auth', authRoutes);
app.use('/register', authRoutes);
app.use('/login', authRoutes);
app.use('/protected', authRoutes);
app.use('/api/forecast', forecastingProxy);
app.use('/api/routing', routingProxy);
app.use('/api/decision', decisionProxy);

// Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'Smart Disaster Prediction & Decision System - API Gateway',
        version: '1.0.0',
        endpoints: {
            auth: {
                register: 'POST /register',
                login: 'POST /login',
                protected: 'GET /protected'
            },
            forecasting: {
                demand: 'POST /api/forecast/demand'
            },
            routing: {
                optimalRoute: 'POST /api/routing/optimal-route'
            },
            decision: {
                recommend: 'POST /api/decision/recommend'
            }
        }
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(err.status || 500).json({
        error: err.message || 'Internal server error',
        ...(config.nodeEnv === 'development' && { stack: err.stack })
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Route not found',
        path: req.path
    });
});

// MongoDB Connection
const connectDB = async () => {
    try {
        console.log('Connecting to MongoDB...');
        console.log('MongoDB URI:', config.mongoUri);

        await mongoose.connect(config.mongoUri, {
            serverSelectionTimeoutMS: 5000,
            socketTimeoutMS: 45000,
        });

        console.log('✓ MongoDB connected successfully');
    } catch (error) {
        console.error('✗ MongoDB connection error:', error.message);
        console.log('Retrying in 5 seconds...');
        setTimeout(connectDB, 5000);
    }
};

// Handle MongoDB connection events
mongoose.connection.on('disconnected', () => {
    console.log('MongoDB disconnected. Attempting to reconnect...');
});

mongoose.connection.on('error', (err) => {
    console.error('MongoDB error:', err);
});

// Start server
const startServer = async () => {
    await connectDB();

    app.listen(config.port, '0.0.0.0', () => {
        console.log('='.repeat(50));
        console.log(`🚀 Backend Express Server Running`);
        console.log(`   Port: ${config.port}`);
        console.log(`   Environment: ${config.nodeEnv}`);
        console.log(`   MongoDB: ${mongoose.connection.readyState === 1 ? 'Connected' : 'Disconnected'}`);
        console.log('='.repeat(50));
        console.log('ML Services:');
        console.log(`   Forecasting: ${config.services.forecasting}`);
        console.log(`   Routing: ${config.services.routing}`);
        console.log(`   Decision: ${config.services.decision}`);
        console.log('='.repeat(50));
    });
};

startServer();
