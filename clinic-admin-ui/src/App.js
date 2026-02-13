import React, { useEffect, useState } from 'react';
import { fetchLogs, fetchAppointments, fetchPatients, updateAppointmentStatus } from './api';
import Login from './components/Login'; 
import { 
  Activity, Calendar, CheckCircle, XCircle, ClipboardList, 
  Clock, User, Hash, Users, Search, LogOut 
} from 'lucide-react';

function App() {
  const [token, setToken] = useState(localStorage.getItem('admin_token'));
  const [logs, setLogs] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [activeTab, setActiveTab] = useState('appointments');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    setToken(null);
    window.location.reload(); 
  };

  const handleStatusChange = async (id, currentStatus) => {
      // Definining the cycle logic: 
      // If pending -> confirmed
      // If confirmed -> completed
      // If completed -> back to pending
      let nextStatus;
      if (currentStatus === 'pending') nextStatus = 'confirmed';
      else if (currentStatus === 'confirmed') nextStatus = 'completed';
      else nextStatus = 'pending'; 

      try {
          await updateAppointmentStatus(id, nextStatus);
          // Update local state so UI updates without a refresh
          setAppointments(prev => prev.map(a => a.id === id ? { ...a, status: nextStatus } : a));
      } catch (err) {
          console.error("Failed to update status:", err);
      }
    };

  useEffect(() => {
    if (!token) return;

    const loadData = async () => {
      try {
        const [l, a, p] = await Promise.all([fetchLogs(), fetchAppointments(), fetchPatients()]);
        setLogs(l.data.sort((a, b) => b.id - a.id));
        setAppointments(a.data.sort((a, b) => b.id - a.id));
        setPatients(p.data);
      } catch (err) { 
        console.error("Fetch error:", err);
        if (err.response?.status === 401) setToken(null);
      }
      finally { setLoading(false); }
    };
    loadData();
  }, [token]);

  if (!token) {
    return <Login />;
  }

  const filteredAppts = appointments.filter(a => a.id.toString().includes(searchTerm) || a.appointment_date.includes(searchTerm));
  const filteredPatients = patients.filter(p => p.id.toString().includes(searchTerm) || p.full_name.toLowerCase().includes(searchTerm.toLowerCase()));

  const containerStyle = { padding: '40px', fontFamily: '"Inter", sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh' };
  const navStyle = { display: 'flex', gap: '8px', background: '#e2e8f0', padding: '5px', borderRadius: '10px' };
  const btnStyle = (active) => ({ 
    padding: '8px 16px', border: 'none', borderRadius: '8px', cursor: 'pointer', 
    display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600',
    background: active ? '#fff' : 'transparent', color: active ? '#2563eb' : '#64748b',
    boxShadow: active ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
  });
  const logoutBtnStyle = {
    padding: '8px 16px', border: '1px solid #cbd5e1', borderRadius: '8px', cursor: 'pointer',
    display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600',
    background: '#fff', color: '#ef4444', marginLeft: '20px'
  };
  const inputStyle = { padding: '10px 40px 10px 15px', borderRadius: '8px', border: '1px solid #cbd5e1', width: '250px', outline: 'none' };

  if (loading && token) return <div style={containerStyle}>Loading Dashboard...</div>;

  return (
    <div style={containerStyle}>
      <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '30px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h1 style={{ margin: 0 }}>Clinic Admin</h1>
            <button onClick={handleLogout} style={logoutBtnStyle}>
              <LogOut size={18}/> Logout
            </button>
          </div>
          <div style={{ marginTop: '15px', ...navStyle }}>
            <button onClick={() => {setActiveTab('appointments'); setSearchTerm('')}} style={btnStyle(activeTab === 'appointments')}><Calendar size={18}/> Appts</button>
            <button onClick={() => {setActiveTab('patients'); setSearchTerm('')}} style={btnStyle(activeTab === 'patients')}><Users size={18}/> Patients</button>
            <button onClick={() => {setActiveTab('logs'); setSearchTerm('')}} style={btnStyle(activeTab === 'logs')}><ClipboardList size={18}/> Logs</button>
          </div>
        </div>

        {activeTab !== 'logs' && (
          <div style={{ position: 'relative', alignSelf: 'flex-end' }}>
            <input 
              style={inputStyle} 
              placeholder={activeTab === 'appointments' ? "Search Date or ID..." : "Search Name or ID..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search size={18} style={{ position: 'absolute', right: '12px', top: '12px', color: '#94a3b8' }} />
          </div>
        )}
      </header>

      <div style={{ padding: '24px', background: 'white', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
        {activeTab === 'appointments' && (
          <Table headers={['ID', 'Patient', 'Date', 'Time', 'Status']} data={filteredAppts.map(a => [
            `#${a.id}`, 
            a.patient_id, 
            a.appointment_date, 
            a.start_time, 
            <button 
              onClick={() => handleStatusChange(a.id, a.status)}
              style={{
                padding: '4px 10px',
                borderRadius: '20px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 'bold',
                textTransform: 'uppercase',
                backgroundColor: a.status === 'confirmed' ? '#dcfce7' : a.status === 'completed' ? '#e0f2fe' : '#fef3c7',
                color: a.status === 'confirmed' ? '#166534' : a.status === 'completed' ? '#075985' : '#92400e',
              }}
            >
              {a.status}
            </button>
          ])} />
        )}

        {activeTab === 'patients' && (
          <Table headers={['ID', 'Name', 'Email', 'Phone', 'Insurance']} data={filteredPatients.map(p => [
            `#${p.id}`, <strong>{p.full_name}</strong>, p.email, p.phone_number, p.has_insurance ? 'Yes' : 'No'
          ])} />
        )}

        {activeTab === 'logs' && (
          <Table headers={['Time', 'Action', 'Context', 'Decision']} data={logs.map(l => [
            new Date(l.created_at).toLocaleTimeString(), l.agent_action, l.log_context, l.system_decision
          ])} />
        )}
      </div>
    </div>
  );
}

function Table({ headers, data }) {
  const thStyle = { padding: '16px', textAlign: 'left', backgroundColor: '#f1f5f9', borderBottom: '1px solid #e2e8f0' };
  const tdStyle = { padding: '16px', borderBottom: '1px solid #f1f5f9' };
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead><tr>{headers.map(h => <th key={h} style={thStyle}>{h}</th>)}</tr></thead>
      <tbody>
        {data.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j} style={tdStyle}>{cell}</td>)}</tr>)}
      </tbody>
    </table>
  );
}

export default App;