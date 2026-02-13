import axios from 'axios';

const api = axios.create({
  // The proxy in package.json handles the localhost:8000 redirect
  baseURL: '/', 
});

// --- AUTH INTERCEPTOR ---
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- RESPONSE INTERCEPTOR ---
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('admin_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// --- DASHBOARD API CALLS ---
export const fetchLogs = () => api.get('/logs/');
export const fetchAppointments = () => api.get('/appointments/');
export const fetchPatients = () => api.get('/patients/');

// --- AUTH CALL ---
// Updated: Removed the manual Content-Type header so Axios auto-detects it.
export const loginUser = (formData) => api.post('/token', formData);

export const updateAppointmentStatus = (id, status) => 
    api.patch(`/appointments/${id}/status?new_status=${status}`);

export default api;