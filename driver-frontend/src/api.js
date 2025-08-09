import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE });

// --- tokens in localStorage ---
export const setCeoToken = (t) => localStorage.setItem("ceoToken", t || "");
export const getCeoToken = () => localStorage.getItem("ceoToken") || "";
export const setStaffToken = (t) => localStorage.setItem("staffToken", t || "");
export const getStaffToken = () => localStorage.getItem("staffToken") || "";
export const clearTokens = () => { setCeoToken(""); setStaffToken(""); };

export const ping = () => api.get("/ping");

export const loginCEO = (email, password) =>
  api.post("/login", new URLSearchParams({ username: email, password }));

export const companyMe = (token) =>
  api.get("/company/me", { headers: { Authorization: `Bearer ${token}` } });

export const inviteStaff = (token, payload) =>
  api.post("/invite-user", payload, { headers: { Authorization: `Bearer ${token}` } });

export const loginStaff = (email, password) =>
  api.post("/staff-login", new URLSearchParams({ username: email, password }));

export const createDriver = (token, payload) =>
  api.post("/drivers", payload, { headers: { Authorization: `Bearer ${token}` } });

export const searchDrivers = (token, name) =>
  api.get(`/drivers/search?name=${encodeURIComponent(name)}`, { headers: { Authorization: `Bearer ${token}` } });

export const rateDriver = (token, payload) =>
  api.post("/ratings", payload, { headers: { Authorization: `Bearer ${token}` } });

export const getDriverRatings = (token, id) =>
  api.get(`/drivers/${id}/ratings`, { headers: { Authorization: `Bearer ${token}` } });
