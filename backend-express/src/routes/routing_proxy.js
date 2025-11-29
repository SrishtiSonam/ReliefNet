const express = require('express');
const axios = require('axios');
const config = require('../config');

const router = express.Router();

// POST /api/routing/optimal-route - Proxy to routing service
router.post('/optimal-route', async (req, res) => {
    const startTime = Date.now();

    try {
        console.log('[Routing Proxy] Forwarding request to routing service...');
        console.log('[Routing Proxy] Request body:', JSON.stringify(req.body, null, 2));

        // Forward request to FastAPI routing service
        const response = await axios.post(
            `${config.services.routing}/routing/optimal-route`,
            req.body,
            {
                timeout: config.requestTimeout,
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        const duration = Date.now() - startTime;
        console.log(`[Routing Proxy] Request completed in ${duration}ms`);

        res.json(response.data);
    } catch (error) {
        const duration = Date.now() - startTime;
        console.error(`[Routing Proxy] Error after ${duration}ms:`, error.message);

        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'Routing service unavailable',
                message: 'Unable to connect to routing service. Please try again later.'
            });
        }

        if (error.response) {
            // FastAPI service returned an error
            return res.status(error.response.status).json({
                error: 'Routing service error',
                message: error.response.data.detail || error.response.data.message || 'Unknown error',
                details: error.response.data
            });
        }

        if (error.code === 'ECONNABORTED') {
            return res.status(504).json({
                error: 'Request timeout',
                message: 'Routing service took too long to respond'
            });
        }

        res.status(500).json({
            error: 'Proxy error',
            message: 'Failed to communicate with routing service',
            details: error.message
        });
    }
});

module.exports = router;
