// reliefnet/frontend/src/store/districtStore.ts
import { create } from 'zustand';
import { getDistricts } from '../api/districtApi';

interface DistrictState {
  districts: any[];
  isLoading: boolean;
  fetchDistricts: (params?: any) => Promise<void>;
}

export const useDistrictStore = create<DistrictState>((set) => ({
  districts: [],
  isLoading: false,
  fetchDistricts: async (params) => {
    set({ isLoading: true });
    try {
      const data = await getDistricts(params);
      set({ districts: data, isLoading: false });
    } catch (error) {
      console.error('Failed to fetch districts', error);
      set({ isLoading: false });
    }
  },
}));
