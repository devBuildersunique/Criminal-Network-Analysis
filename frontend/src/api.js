import axios from "axios";

const BASE = "http://localhost:8000";

const api = axios.create({ baseURL: BASE, timeout: 30000 });

export const analyzeCase = (text) =>
  api.post("/analyze-case", { text }).then((r) => r.data);

export const getDemoText = () =>
  api.get("/demo-text").then((r) => r.data.text);

export const getEntity = (id) =>
  api.get(`/entity/${id}`).then((r) => r.data);

export const getEntityHistory = (id) =>
  api.get(`/entity/${id}/history`).then((r) => r.data);

export const checkHealth = () =>
  api.get("/health").then((r) => r.data).catch(() => null);
