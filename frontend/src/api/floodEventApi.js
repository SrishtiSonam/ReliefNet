// ─── src/api/floodEventApi.js ─────────────────────────────────────────────────
import axios from "axios";
const BASE = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export const getFloodEvents   = (params) => axios.get(`${BASE}/flood-events`, { params });
export const getKerala2018    = ()        => axios.get(`${BASE}/flood-events/kerala-2018`);
export const getFloodInventory = (params) => axios.get(`${BASE}/flood-events/inventory`, { params });

