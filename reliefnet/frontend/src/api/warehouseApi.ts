// reliefnet/frontend/src/api/warehouseApi.ts
import apiClient from './client';

export const getWarehouses = async () => {
  const response = await apiClient.get('/warehouses');
  return response.data;
};

// reliefnet/frontend/src/api/simulationApi.ts
export const runSimulation = async (data: any) => {
  const response = await apiClient.post('/simulation/run', data);
  return response.data;
};

export const getSimulation = async (id: string) => {
  const response = await apiClient.get(`/simulation/${id}`);
  return response.data;
};

// reliefnet/frontend/src/api/allocationApi.ts
export const optimizeAllocation = async (runId: string) => {
  const response = await apiClient.post(`/allocation/optimize/${runId}`);
  return response.data;
};
