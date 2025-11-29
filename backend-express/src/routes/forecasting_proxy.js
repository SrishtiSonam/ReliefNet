const express = require('express');
const axios = require('axios');
const config = require('../config');

const router = express.Router();

// POST /api/forecast/demand - Proxy to forecasting service
router.post('/demand', async (req, res) => {
    const startTime = Date.now();

    try {
        console.log('[Forecasting Proxy] Forwarding request to forecasting service...');
        console.log('[Forecasting Proxy] Request body:', JSON.stringify(req.body, null, 2));

        // Forward request to FastAPI forecasting service
        const response = await axios.post(
            `${config.services.forecasting}/forecast/demand`,
            req.body,
            {
                timeout: config.requestTimeout,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        const duration = Date.now() - startTime;
        console.log(`[Forecasting Proxy] Request completed in ${duration}ms`);

        res.json(response.data);
    } catch (error) {
        const duration = Date.now() - startTime;
        console.error(`[Forecasting Proxy] Error after ${duration}ms:`, error.message);

        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'Forecasting service unavailable',
                message: 'Unable to connect to forecasting service. Please try again later.'
            });
        }

        if (error.response) {
            // FastAPI service returned an error
            return res.status(error.response.status).json({
                error: 'Forecasting service error',
                message: error.response.data.detail || error.response.data.message || 'Unknown error',
                details: error.response.data
            });
        }

        if (error.code === 'ECONNABORTED') {
            return res.status(504).json({
                error: 'Request timeout',
                message: 'Forecasting service took too long to respond'
            });
        }

        res.status(500).json({
            error: 'Proxy error',
            message: 'Failed to communicate with forecasting service',
            details: error.message
        });
    }
});

module.exports = router;
