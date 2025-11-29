import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem('token');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

// Authentication APIs
export const authAPI = {
    register: (userData) => api.post('/register', userData),
    login: (credentials) => api.post('/login', credentials),
    checkProtected: () => api.get('/protected')
};

// Forecasting APIs
export const forecastAPI = {
    getDemandForecast: (data) => api.post('/api/forecast/demand', data)
};

// Routing APIs
export const routingAPI = {
    getOptimalRoute: (data) => api.post('/api/routing/optimal-route', data)
};

// Decision APIs
export const decisionAPI = {
    getRecommendation: (data) => api.post('/api/decision/recommend', data)
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
