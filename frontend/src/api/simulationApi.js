// ─── src/api/simulationApi.js ─────────────────────────────────────────────────
import axios from "axios";
const BASE = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export const runSimulation   = (config) => axios.post(`${BASE}/simulations`, config);
export const getSimulations  = ()       => axios.get(`${BASE}/simulations`);
export const getSimStatus    = (id)     => axios.get(`${BASE}/simulations/${id}/status`);