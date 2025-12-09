import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getDashboard = (role) => api.get(`/dashboard?role=${role}`);
export const getForecast = (district, days = 7) => api.get(`/forecast?district=${district}&days=${days}`);
export const optimizeAllocation = (data) => api.post('/optimize_allocation', data);
export const getExplanation = (districtId) => api.get(`/explain_allocation?district_id=${districtId}`);
export const getPublicRequests = (status = null) => {
    const url = status ? `/public_requests?status=${status}` : '/public_requests';
    return api.get(url);
};
export const createPublicRequest = (data) => api.post('/public_requests', data);
export const getRoadblocks = () => api.get('/roadblocks');
export const createRoadblock = (data) => api.post('/roadblocks', data);
export const getVehicles = () => api.get('/vehicles');
export const getDistrictsGeo = () => api.get('/districts_geo');
export const planMission = (data) => api.post('/mission/plan', data);

export const connectWebSocket = (onMessage) => {
    const ws = new WebSocket('ws://localhost:8000/ws/vehicles');

    ws.onopen = () => {
        console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
    };

    return ws;
};

export default api;
