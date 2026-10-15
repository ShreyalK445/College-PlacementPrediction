import { useState, useRef, useEffect } from 'react';
import './MentorChatView.css';
import { sendMentorMessage } from '../api';

const QUICK_PROMPTS = [
  '✍️ Improve this resume bullet: built a placement prediction web app',
  '💻 Give me 3 technical interview questions for Software Developer',
  '🤝 How should I answer: Tell me about yourself using STAR?',
  '📊 What are the essential skills needed for Data Analyst?',
  '📈 How can I raise my placement readiness score?',
];

const INITIAL_MESSAGES = [
  {
    id: 1,
    role: 'mentor',
    content: `### 👋 Hello! I'm your Placement Mentor.

I can help you prepare for campus placement drives, review resume bullet points, practice technical/behavioral interview questions, and identify skill gaps.

Click any suggested question below or type your query!`,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  },
];

function getNowTime() {
  const d = new Date();
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

export default function MentorChatView({ studentProfile }) {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const msgIdSeq = useRef(100);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function handleSend(textToSend) {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    msgIdSeq.current += 1;
    const userMsg = {
      id: msgIdSeq.current,
      role: 'user',
      content: text,
      time: getNowTime(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await sendMentorMessage(text, studentProfile || {}, history);

      msgIdSeq.current += 1;
      const mentorMsg = {
        id: msgIdSeq.current,
        role: 'mentor',
        content: res.data.reply,
        time: getNowTime(),
      };
      setMessages((prev) => [...prev, mentorMsg]);
    } catch {
      msgIdSeq.current += 1;
      const errorMsg = {
        id: msgIdSeq.current,
        role: 'mentor',
        content: '⚠️ I encountered an issue connecting to the mentor service. Please ensure the backend server is running.',
        time: getNowTime(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  }

  // Simple formatting helper for headers and lists
  function renderFormattedContent(text) {
    const lines = text.split('\n');
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
        {lines.map((line, idx) => {
          if (line.startsWith('### ')) {
            return <h3 key={idx}>{line.replace('### ', '')}</h3>;
          }
          if (line.startsWith('**') && line.endsWith('**')) {
            return <strong key={idx}>{line.replace(/\*\*/g, '')}</strong>;
          }
          if (line.startsWith('- ') || line.startsWith('* ')) {
            return (
              <div key={idx} style={{ display: 'flex', gap: '0.5rem', paddingLeft: '0.5rem' }}>
                <span>•</span>
                <span>{line.replace(/^[-*]\s*/, '')}</span>
              </div>
            );
          }
          if (line.startsWith('> ')) {
            return <blockquote key={idx}>{line.replace('> ', '')}</blockquote>;
          }
          if (line.trim() === '') return <div key={idx} style={{ height: '4px' }} />;
          return <p key={idx} style={{ margin: 0 }}>{line}</p>;
        })}
      </div>
    );
  }

  return (
    <div className="mentor-container animate-fade-in-up">
      <div className="glass-card mentor-chat-card">
        {/* Header */}
        <div className="mentor-chat-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.75rem' }}>🤖</span>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>AI Career Mentor</h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)' }}>
                ● Active Guidance Session
              </span>
            </div>
          </div>
          <button
            type="button"
            className="btn btn-outline"
            style={{ fontSize: '0.75rem', padding: '0.3rem 0.75rem' }}
            onClick={() => setMessages(INITIAL_MESSAGES)}
          >
            Clear Conversation
          </button>
        </div>

        {/* Messages List */}
        <div className="mentor-messages-list">
          {messages.map((m) => (
            <div key={m.id} className={`message-bubble ${m.role}`}>
              {m.role === 'mentor' ? renderFormattedContent(m.content) : m.content}
              <div className="message-meta">{m.time}</div>
            </div>
          ))}

          {loading && (
            <div className="message-bubble mentor" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span className="spinner" />
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Career Mentor is thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Prompts */}
        <div className="quick-prompt-chips">
          {QUICK_PROMPTS.map((p) => (
            <button
              key={p}
              type="button"
              className="prompt-chip"
              onClick={() => handleSend(p.replace(/^[^\w\s]+\s*/, ''))}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-row"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            type="text"
            placeholder="Ask mentor about your resume, interview questions, or skill gaps..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
            Send ➔
          </button>
        </form>
      </div>

      <div style={{ textAlign: 'center', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
        * Career Mentor provides advisory support. Advice should be adapted to specific company criteria.
      </div>
    </div>
  );
}
