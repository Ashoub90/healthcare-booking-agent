import axios from 'axios';

const api = axios.create({
  // Since you added the "proxy" to package.json, 
  // we use '/' so the proxy handles the localhost:8000 part.
  baseURL: '/', 
});

export const fetchLogs = () => api.get('/logs/');
export const fetchAppointments = () => api.get('/appointments/');
export const fetchPatients = () => api.get('/patients/');

export default api;