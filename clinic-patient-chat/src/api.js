import axios from 'axios';

const api = axios.create({
  // The proxy in package.json handles the localhost:8000 redirect
  baseURL: '/', 
});

const getSessionId = () => {
  let sid = localStorage.getItem('chat_session_id');
  if (!sid) {
    sid = `sess_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('chat_session_id', sid);
  }
  return sid;
};

// Use the 'api' instance we created above
export const sendMessage = (payload) => {
    return api.post('/chat/', payload); 
};

export default api;