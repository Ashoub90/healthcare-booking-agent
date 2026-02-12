import React, { useEffect, useState } from 'react';
import { fetchLogs, fetchAppointments } from './api';
import { 
  Activity, 
  Calendar, 
  CheckCircle, 
  XCircle, 
  ClipboardList, 
  Clock, 
  User,
  Hash
} from 'lucide-react';

function App() {
  const [logs, setLogs] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [activeTab, setActiveTab] = useState('appointments');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [logsRes, apptsRes] = await Promise.all([
          fetchLogs(),
          fetchAppointments()
        ]);
        
        // Sorting logs: newest first based on id
        const sortedLogs = logsRes.data.sort((a, b) => b.id - a.id);
        
        // Sorting appointments: highest ID (latest) first
        const sortedAppts = apptsRes.data.sort((a, b) => b.id - a.id);

        setLogs(sortedLogs);
        setAppointments(sortedAppts);
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Styles
  const containerStyle = { padding: '40px', fontFamily: '"Inter", sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh' };
  const headerStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' };
  const navStyle = { display: 'flex', gap: '12px', background: '#e2e8f0', padding: '6px', borderRadius: '10px' };
  const btnStyle = { padding: '10px 20px', border: 'none', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600' };
  const activeBtnStyle = { ...btnStyle, background: '#ffffff', color: '#2563eb', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' };
  const inactiveBtnStyle = { ...btnStyle, background: 'transparent', color: '#64748b' };
  
  const cardStyle = { padding: '24px', background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e2e8f0' };
  const tableStyle = { width: '100%', borderCollapse: 'collapse' };
  const thStyle = { padding: '16px', textAlign: 'left', backgroundColor: '#f1f5f9', color: '#475569', fontWeight: '600', borderBottom: '1px solid #e2e8f0' };
  const tdStyle = { padding: '16px', borderBottom: '1px solid #f1f5f9', color: '#1e293b', fontSize: '14px' };

  if (loading) return <div style={containerStyle}>Loading Dashboard...</div>;

  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <div>
          <h1 style={{ margin: 0, color: '#0f172a' }}>Clinic Management</h1>
          <p style={{ color: '#64748b', marginTop: '5px' }}>Dashboard Overview</p>
        </div>
        
        <div style={navStyle}>
          <button 
            onClick={() => setActiveTab('appointments')}
            style={activeTab === 'appointments' ? activeBtnStyle : inactiveBtnStyle}
          >
            <Calendar size={18} /> Appointments
          </button>
          <button 
            onClick={() => setActiveTab('logs')}
            style={activeTab === 'logs' ? activeBtnStyle : inactiveBtnStyle}
          >
            <ClipboardList size={18} /> System Logs
          </button>
        </div>
      </header>

      <div style={cardStyle}>
        {activeTab === 'appointments' ? (
          <section>
            <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0 }}>All Appointment Records</h2>
              <span style={{ color: '#64748b', fontSize: '14px' }}>Total: {appointments.length}</span>
            </div>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Appt ID</th>
                  <th style={thStyle}>Patient ID</th>
                  <th style={thStyle}>Date</th>
                  <th style={thStyle}>Time</th>
                  <th style={thStyle}>Status</th>
                  <th style={thStyle}>Google Sync</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((appt) => (
                  <tr key={appt.id}>
                    <td style={tdStyle}>
                       <code style={{ background: '#f1f5f9', padding: '4px 8px', borderRadius: '6px', fontWeight: '600', color: '#475569' }}>
                        #{appt.id}
                       </code>
                    </td>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <User size={14} color="#94a3b8"/> 
                        <strong>{appt.patient_id}</strong>
                      </div>
                    </td>
                    <td style={tdStyle}>{appt.appointment_date}</td>
                    <td style={tdStyle}>{appt.start_time}</td>
                    <td style={tdStyle}>
                      <span style={{ 
                        padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold',
                        backgroundColor: appt.status === 'confirmed' ? '#dcfce7' : '#fef9c3',
                        color: appt.status === 'confirmed' ? '#166534' : '#854d0e'
                      }}>
                        {appt.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      {appt.sync_status === 'synced' ? (
                        <span style={{ color: '#16a34a', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle size={14}/> Synced
                        </span>
                      ) : (
                        <span style={{ color: '#dc2626', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <XCircle size={14}/> Pending
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        ) : (
          <section>
            <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0 }}>System Audit Logs</h2>
              <span style={{ color: '#64748b', fontSize: '14px' }}>Total: {logs.length}</span>
            </div>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Log ID</th>
                  <th style={thStyle}><Clock size={16} /> Time</th>
                  <th style={thStyle}>Action</th>
                  <th style={thStyle}>Context</th>
                  <th style={thStyle}>Decision</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td style={tdStyle}><small style={{color: '#94a3b8'}}>#{log.id}</small></td>
                    <td style={tdStyle}>{new Date(log.created_at).toLocaleString()}</td>
                    <td style={tdStyle}>
                      <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>
                        {log.agent_action}
                      </code>
                    </td>
                    <td style={tdStyle}>{log.log_context}</td>
                    <td style={tdStyle}>{log.system_decision}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;