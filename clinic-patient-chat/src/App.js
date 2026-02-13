import React, { useState, useEffect, useRef } from 'react';
import { sendMessage } from './api';
import { Send, Activity, RefreshCw, User, Bot } from 'lucide-react';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello! I am your Clinic Assistant. How can I help you today?' }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionState, setSessionState] = useState(null);
  const scrollRef = useRef(null);

  const [sessionId] = useState(() => {
    let sid = localStorage.getItem('chat_session_id');
    if (!sid) {
      sid = `sess_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('chat_session_id', sid);
    }
    return sid;
  });

  const handleReset = () => {
    localStorage.removeItem('chat_session_id');
    window.location.reload();
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await sendMessage({
        message: input,
        session_id: sessionId
      });

      const { reply, data } = response.data;
      setMessages(prev => [...prev, { role: 'assistant', text: reply }]);

      if (data && data.session_state) {
        setSessionState(data.session_state);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', text: "I'm having trouble reaching the clinic. Please try again later." }]);
    } finally {
      setIsTyping(false);
    }
  };

  // --- Updated Styles for Vertical Stack ---
  const containerStyle = { display: 'flex', flexDirection: 'column', height: '100vh', background: '#f8fafc', fontFamily: '"Inter", sans-serif' };
  const headerStyle = { padding: '15px 20px', background: '#fff', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' };
  const listStyle = { flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '24px' };
  const inputAreaStyle = { padding: '20px', display: 'flex', gap: '10px', background: 'white', borderTop: '1px solid #e2e8f0' };
  
  const bubbleStyle = (role) => ({
    padding: '16px',
    borderRadius: '12px',
    background: role === 'user' ? '#eff6ff' : '#ffffff',
    color: '#1e293b',
    width: '100%',
    boxSizing: 'border-box',
    fontSize: '14px',
    lineHeight: '1.6',
    border: role === 'user' ? '1px solid #dbeafe' : '1px solid #e2e8f0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  });

  const labelStyle = (role) => ({
    fontSize: '11px',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: role === 'user' ? '#3b82f6' : '#64748b',
    display: 'flex',
    alignItems: 'center',
    gap: '6px'
  });

  const stateBarStyle = { padding: '8px 20px', background: '#f0fdf4', borderBottom: '1px solid #dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', color: '#166534' };

  return (
    <div style={containerStyle}>
      <header style={headerStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '10px', height: '10px', background: '#22c55e', borderRadius: '50%' }}></div>
          <h2 style={{ margin: 0, fontSize: '16px', fontWeight: '700' }}>Clinic Assistant</h2>
        </div>
        <button onClick={handleReset} style={{ display: 'flex', alignItems: 'center', gap: '5px', background: '#fee2e2', color: '#dc2626', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' }}>
          <RefreshCw size={14} /> Restart
        </button>
      </header>

      {sessionState && sessionState.patient_id && (
        <div style={stateBarStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} />
            <span>Identified Patient ID: <strong>{sessionState.patient_id}</strong></span>
          </div>
          <div style={{ fontSize: '10px', fontWeight: '700', color: '#15803d' }}>SECURE SESSION ACTIVE</div>
        </div>
      )}

      <div style={listStyle}>
        {messages.map((msg, i) => (
          <div key={i} style={bubbleStyle(msg.role)}>
            <div style={labelStyle(msg.role)}>
              {msg.role === 'user' ? <User size={12}/> : <Bot size={12}/>}
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
          </div>
        ))}
        {isTyping && (
          <div style={bubbleStyle('assistant')}>
            <div style={labelStyle('assistant')}><Bot size={12}/> Assistant</div>
            <span style={{ fontStyle: 'italic', color: '#94a3b8' }}>Thinking...</span>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div style={inputAreaStyle}>
        <input 
          style={{ flex: 1, padding: '12px', borderRadius: '10px', border: '1px solid #cbd5e1', outline: 'none' }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message here..."
        />
        <button 
          onClick={handleSend} 
          style={{ background: '#2563eb', border: 'none', padding: '10px 15px', borderRadius: '10px', cursor: 'pointer' }}
        >
          <Send size={20} color="white" />
        </button>
      </div>
    </div>
  );
}

export default App;