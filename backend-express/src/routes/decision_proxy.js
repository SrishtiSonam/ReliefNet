const express = require('express');
const axios = require('axios');
const config = require('../config');

const router = express.Router();

// POST /api/decision/recommend - Proxy to decision service
router.post('/recommend', async (req, res) => {
    const startTime = Date.now();

    try {
        console.log('[Decision Proxy] Forwarding request to decision service...');
        console.log('[Decision Proxy] Request body:', JSON.stringify(req.body, null, 2));

        // Forward request to FastAPI decision service
        const response = await axios.post(
            `${config.services.decision}/decision/recommend`,
            req.body,
            {
                timeout: config.requestTimeout,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        const duration = Date.now() - startTime;
        console.log(`[Decision Proxy] Request completed in ${duration}ms`);

        res.json(response.data);
    } catch (error) {
        const duration = Date.now() - startTime;
        console.error(`[Decision Proxy] Error after ${duration}ms:`, error.message);

        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'Decision service unavailable',
                message: 'Unable to connect to decision service. Please try again later.'
            });
        }

        if (error.response) {
            // FastAPI service returned an error
            return res.status(error.response.status).json({
                error: 'Decision service error',
                message: error.response.data.detail || error.response.data.message || 'Unknown error',
                details: error.response.data
            });
        }

        if (error.code === 'ECONNABORTED') {
            return res.status(504).json({
                error: 'Request timeout',
                message: 'Decision service took too long to respond'
            });
        }

        res.status(500).json({
            error: 'Proxy error',
            message: 'Failed to communicate with decision service',
            details: error.message
        });
    }
});

module.exports = router;
