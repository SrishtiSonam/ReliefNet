require('dotenv').config();

module.exports = {
    // MongoDB Configuration
    mongoUri: process.env.MONGO_URI || 'mongodb://mongo:27017/sdpd_db',

    // JWT Configuration
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
    jwtExpire: process.env.JWT_EXPIRE || '24h',

    // Server Configuration
    port: process.env.PORT || 5000,
    nodeEnv: process.env.NODE_ENV || 'development',

    // ML Microservices URLs
    services: {
        forecasting: process.env.FORECASTING_SERVICE_URL || 'http://forecasting_service:8001',
        routing: process.env.ROUTING_SERVICE_URL || 'http://routing_service:8002',
        decision: process.env.DECISION_SERVICE_URL || 'http://decision_service:8003'
    },

    // Request timeout (ms)
    requestTimeout: parseInt(process.env.REQUEST_TIMEOUT) || 30000
};
