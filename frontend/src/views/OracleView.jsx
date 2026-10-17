import React, { useState, useEffect, useRef } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';
import renderMarkdownLite from '../utils/markdown';

export default function OracleView({ onSelectMyth, initialQuery, onInitialQueryConsumed }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Greetings, seeker of ancient lore. I am your guide through the classical Greek canon. ' +
        'Inquire about any deity or mortal, request full myth narrations, trace ancestral relationships, ' +
        'compare two figures, or explore recurring themes and story patterns such as hubris, transformation, and the journey to the underworld.',
      storyCard: null,
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);
  // One id per page load so the API can resolve follow-ups ("tell me more")
  // without sharing conversation memory between visitors.
  const sessionIdRef = useRef(
    (typeof crypto !== 'undefined' && crypto.randomUUID)
      ? crypto.randomUUID()
      : `s${Date.now().toString(36)}${Math.random().toString(36).slice(2, 12)}`
  );

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [messages, loading]);

  const quickPrompts = [
    { label: 'Myth: Prometheus & Fire', query: 'Summarize the myth of Prometheus' },
    { label: "Family: Zeus's children", query: "Who are Zeus's children?" },
    { label: 'Deity: Who is Athena?', query: 'Who is Athena?' },
    { label: 'Compare: Athena vs Arachne', query: 'Compare Athena and Arachne' },
    { label: 'Pattern: turned into a tree', query: 'Which myths have someone turned into a tree?' },
    { label: 'Theme: stories of hubris', query: 'Which myths are about hubris?' },
  ];

  const handleSend = async (queryText) => {
    const text = queryText || inputValue;
    if (!text.trim() || loading) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, session_id: sessionIdRef.current }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.response || 'I could not decipher that mythological query.',
          storyCard: data.story_card,
          suggestions: Array.isArray(data.suggestions) ? data.suggestions : [],
        },
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'The ancient scrolls could not be reached at this moment.',
          storyCard: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      handleSend(initialQuery);
      if (onInitialQueryConsumed) onInitialQueryConsumed();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuery]);

  return (
    <div className="oracle-delphi-bg" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <Reveal className="oracle-intro-reveal" style={{ marginBottom: '24px', display: 'flex', alignItems: 'flex-start', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <SectionIcon name="eye" />
            <h2 style={{ fontSize: '1.6rem', margin: 0 }}>Ask The Oracle</h2>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Don&apos;t know where to start? Just ask in plain English — &quot;who is Medusa?&quot; or
            &quot;what happened to Icarus?&quot; — and the Oracle will answer and point you to the full story.
          </p>
        </div>
        <img src="/images/decor/sun-cloud-relief.png" alt="" aria-hidden="true" className="oracle-sun-decor" />
      </Reveal>

      {/* Quick Starter Prompts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px', marginBottom: '20px' }} className="oracle-prompts">
        {quickPrompts.map((p, i) => (
          <Reveal
            key={i}
            delay={i * 60}
            as="button"
            onClick={() => handleSend(p.query)}
            className="btn-secondary"
            style={{ fontSize: '0.75rem', padding: '8px 12px', textAlign: 'left' }}
          >
            {p.label}
          </Reveal>
        ))}
      </div>

      {/* Dialogue Thread */}
      <div
        className="panel"
        style={{
          marginBottom: '20px',
          minHeight: '420px',
          maxHeight: '620px',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
      <div
        style={{
          padding: '24px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          flex: 1,
          minHeight: 0,
        }}
        role="log"
        aria-live="polite"
        aria-label="Conversation with the Oracle"
      >
        {messages.map((m, idx) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={idx}
              className="chat-bubble-in oracle-message"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-end' : 'flex-start',
              }}
            >
              <div
                style={{
                  fontSize: '0.72rem',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  color: isUser ? 'var(--text-muted)' : 'var(--accent-gold)',
                  marginBottom: '4px',
                }}
              >
                {isUser ? 'Seeker' : 'Oracle of Chronicle'}
              </div>
              <div
                className="oracle-bubble"
                style={{
                  maxWidth: '85%',
                  background: isUser ? 'var(--bg-surface-elevated)' : 'var(--bg-surface)',
                  border: isUser ? '1px solid var(--border-strong)' : '1px solid var(--border-subtle)',
                  padding: '14px 18px',
                  lineHeight: '1.6',
                  color: 'var(--text-primary)',
                }}
              >
                {renderMarkdownLite(m.content)}

                {/* Attached Lore Dossier Card */}
                {m.storyCard && (
                  <div
                    style={{
                      marginTop: '16px',
                      paddingTop: '12px',
                      borderTop: '1px solid var(--border-subtle)',
                      background: 'rgba(0,0,0,0.045)',
                      padding: '12px',
                    }}
                  >
                    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '6px 12px', marginBottom: '8px' }}>
                      <strong style={{ color: 'var(--text-primary)' }}>{m.storyCard.title}</strong>
                      <span className="badge-theme">{m.storyCard.theme}</span>
                    </div>
                    {m.storyCard.summary && (
                      <p style={{ fontSize: '0.85rem', fontStyle: 'italic', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                        {m.storyCard.summary}
                      </p>
                    )}
                    {onSelectMyth && m.storyCard.title && (
                      <button
                        onClick={() => onSelectMyth(m.storyCard.id || m.storyCard.title)}
                        className="btn-primary"
                        style={{ fontSize: '0.7rem', padding: '4px 10px' }}
                      >
                        Read Full Story in Anthology &rarr;
                      </button>
                    )}
                  </div>
                )}
              </div>
              {!isUser && idx === messages.length - 1 && !loading && m.suggestions && m.suggestions.length > 0 && (
                <div className="oracle-suggestions" aria-label="Suggested follow-up questions">
                  {m.suggestions.slice(0, 4).map((s) => (
                    <button key={s} type="button" className="oracle-chip" onClick={() => handleSend(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
        {loading && (
          <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.85rem' }}>
            Consulting the ancient scrolls...
          </div>
        )}
        <div ref={endRef} />
      </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={{ display: 'flex', gap: '8px' }}
      >
        <input
          type="text"
          aria-label="Ask the Oracle a question"
          maxLength={500}
          placeholder="Ask about a myth, god or family…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          style={{ flex: 1 }}
          disabled={loading}
        />
        <button type="submit" className="btn-primary" disabled={loading || !inputValue.trim()}>
          Inquire
        </button>
      </form>
    </div>
  );
}
