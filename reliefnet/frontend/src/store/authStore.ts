// reliefnet/frontend/src/store/authStore.ts
import { create } from 'zustand';

interface AuthState {
  user: any | null;
  token: string | null;
  setAuth: (user: any, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('reliefnet_token'),
  setAuth: (user, token) => {
    localStorage.setItem('reliefnet_token', token);
    set({ user, token });
  },
  logout: () => {
    localStorage.removeItem('reliefnet_token');
    set({ user: null, token: null });
  },
}));
