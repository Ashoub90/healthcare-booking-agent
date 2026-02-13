import axios from 'axios';

const api = axios.create({
  // The proxy in package.json handles the localhost:8000 redirect
  baseURL: '/', 
});

export const fetchLogs = () => api.get('/logs/');
export const fetchAppointments = () => api.get('/appointments/');

export default api;