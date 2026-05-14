// reliefnet/frontend/src/api/allocationApi.ts
import apiClient from './client';

export const optimizeAllocation = async (runId: string, config: any) => {
  const response = await apiClient.post(`/allocation/optimize/${runId}`, config);
  return response.data;
};

export const getAllocation = async (id: string) => {
  const response = await apiClient.get(`/allocation/${id}`);
  return response.data;
};

export const dispatchAllocation = async (id: string, planPayload: any) => {
  const response = await apiClient.post(`/allocation/${id}/dispatch`, planPayload);
  return response.data;
};
