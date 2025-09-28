const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:8000'],
    credentials: true
}));
app.use(express.json());
app.use(express.static('public'));

// Simple in-memory session storage (replace with proper auth in production)
const sessions = new Map();
const auditLogs = [];

// Helper functions
const generateId = () => Math.random().toString(36).substr(2, 9);

const logActivity = (user, action, details) => {
    const logEntry = {
        id: generateId(),
        user: user || 'anonymous',
        timestamp: new Date().toISOString(),
        action,
        details,
        ip: 'localhost' // In real app, get from req.ip
    };
    auditLogs.push(logEntry);
    console.log(`[AUDIT] ${user}: ${action}`, details);
    return logEntry;
};

// Routes
app.get('/', (req, res) => {
    res.json({ message: 'SDPDIAP Backend Service', status: 'running' });
});

// Simple auth endpoints
app.post('/api/auth/login', (req, res) => {
    const { username, password } = req.body;
    
    // Simple validation (replace with proper auth)
    if (username && password) {
        const sessionId = generateId();
        const user = { username, role: 'operator' };
        
        sessions.set(sessionId, user);
        logActivity(username, 'login', { sessionId });
        
        res.json({ 
            success: true, 
            sessionId, 
            user: { username: user.username, role: user.role }
        });
    } else {
        res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
});

app.post('/api/auth/logout', (req, res) => {
    const { sessionId } = req.body;
    const user = sessions.get(sessionId);
    
    if (user) {
        sessions.delete(sessionId);
        logActivity(user.username, 'logout', { sessionId });
    }
    
    res.json({ success: true });
});

// Middleware to check authentication
const requireAuth = (req, res, next) => {
    const sessionId = req.headers.authorization?.replace('Bearer ', '');
    const user = sessions.get(sessionId);
    
    if (!user) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    req.user = user;
    next();
};

// Audit log endpoints
app.get('/api/audit-logs', requireAuth, (req, res) => {
    const { limit = 50, offset = 0 } = req.query;
    
    const logs = auditLogs
        .slice(-limit - offset, -offset || undefined)
        .reverse();
    
    res.json({
        logs,
        total: auditLogs.length,
        limit: parseInt(limit),
        offset: parseInt(offset)
    });
});

app.post('/api/audit-log', requireAuth, (req, res) => {
    const { action, details, constraints, preOptObj, postOptObj } = req.body;
    
    const logEntry = logActivity(req.user.username, action, {
        ...details,
        constraints,
        pre_opt_obj: preOptObj,
        post_opt_obj: postOptObj
    });
    
    res.json({ success: true, logEntry });
});

// Session management
app.get('/api/session/current', requireAuth, (req, res) => {
    res.json({
        user: req.user,
        timestamp: new Date().toISOString()
    });
});

// Configuration endpoints
app.get('/api/config', requireAuth, (req, res) => {
    const config = {
        mlServiceUrl: 'http://localhost:8000',
        mapConfig: {
            center: [28.6139, 77.2090], // Delhi coordinates
            zoom: 10,
            tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        },
        fleetConfig: [
            { class: "small_truck", capacity: 100, speed: 40, range_km: 500, count: 5 },
            { class: "uav_light", capacity: 10, speed: 60, range_km: 50, count: 8 }
        ],
        districts: [
            { id: "D001", name: "Central", coords: [28.6139, 77.2090] },
            { id: "D002", name: "North", coords: [28.6448, 77.2167] },
            { id: "D003", name: "South", coords: [28.5832, 77.2275] },
            { id: "D004", name: "East", coords: [28.6139, 77.2455] },
            { id: "D005", name: "West", coords: [28.6139, 77.1724] }
        ]
    };
    
    res.json(config);
});

// File upload/download endpoints
app.post('/api/scenarios/upload', requireAuth, async (req, res) => {
    try {
        const { name, scenario } = req.body;
        const filename = `${name.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
        const filepath = path.join(__dirname, 'data', 'scenarios', filename);
        
        await fs.mkdir(path.dirname(filepath), { recursive: true });
        await fs.writeFile(filepath, JSON.stringify(scenario, null, 2));
        
        logActivity(req.user.username, 'scenario_upload', { filename });
        
        res.json({ success: true, filename });
    } catch (error) {
        console.error('Scenario upload error:', error);
        res.status(500).json({ error: 'Failed to upload scenario' });
    }
});

app.get('/api/scenarios', requireAuth, async (req, res) => {
    try {
        const scenariosDir = path.join(__dirname, 'data', 'scenarios');
        
        try {
            const files = await fs.readdir(scenariosDir);
            const scenarios = [];
            
            for (const file of files) {
                if (file.endsWith('.json')) {
                    const filepath = path.join(scenariosDir, file);
                    const content = await fs.readFile(filepath, 'utf8');
                    const scenario = JSON.parse(content);
                    
                    scenarios.push({
                        filename: file,
                        name: scenario.name || file.replace('.json', ''),
                        description: scenario.description || 'No description'
                    });
                }
            }
            
            res.json({ scenarios });
        } catch (dirError) {
            // Directory doesn't exist, return empty list
            res.json({ scenarios: [] });
        }
    } catch (error) {
        console.error('Scenarios list error:', error);
        res.status(500).json({ error: 'Failed to list scenarios' });
    }
});

// Experiments and results
app.get('/api/experiments', requireAuth, async (req, res) => {
    try {
        const experimentsDir = path.join(__dirname, '..', 'artifacts', 'experiments');
        
        try {
            const files = await fs.readdir(experimentsDir);
            const experiments = files
                .filter(file => file.endsWith('.csv'))
                .map(file => {
                    const parts = file.replace('.csv', '').split('_');
                    return {
                        filename: file,
                        policy: parts[1] || 'unknown',
                        timestamp: parts.slice(2).join('_') || 'unknown',
                        path: path.join(experimentsDir, file)
                    };
                });
            
            res.json({ experiments });
        } catch (dirError) {
            res.json({ experiments: [] });
        }
    } catch (error) {
        console.error('Experiments list error:', error);
        res.status(500).json({ error: 'Failed to list experiments' });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        sessions: sessions.size,
        auditLogs: auditLogs.length
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(500).json({ 
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
app.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
    
    // Log initial activity
    logActivity('system', 'server_start', { port: PORT });
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down backend server...');
    logActivity('system', 'server_shutdown', { reason: 'SIGINT' });
    process.exit(0);
});