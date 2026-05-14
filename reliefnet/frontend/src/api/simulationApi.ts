// reliefnet/frontend/src/api/simulationApi.ts
import apiClient from './client';

export const runSimulation = async (data: any) => {
  const response = await apiClient.post('/simulation/run', data);
  return response.data;
};

export const getSimulation = async (id: string) => {
  const response = await apiClient.get(`/simulation/${id}`);
  return response.data;
};
