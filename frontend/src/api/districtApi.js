// ─── src/api/districtApi.js ───────────────────────────────────────────────────
import axios from "axios";
const BASE = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export const getDistricts  = ()     => axios.get(`${BASE}/districts`);
export const getDFSI       = ()     => axios.get(`${BASE}/districts/dfsi`);
export const getDistrictDemand = (name, hrs) =>
  axios.get(`${BASE}/districts/${name}/demand`, { params: { period_hours: hrs } });
