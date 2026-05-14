import apiClient from './client';

export const submitRequest = async (data: any) => {
  return await apiClient.post('/requests/', data);
};

export const getRequests = async () => {
  const response = await apiClient.get('/requests/');
  return response.data;
};

export const updateRequestStatus = async (id: str, status: str) => {
  return await apiClient.put(`/requests/${id}/status?status=${status}`);
};
