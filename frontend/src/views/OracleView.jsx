import React, { useState, useEffect, useRef } from 'react';
import Reveal from '../components/Reveal';
import { THEME } from '../data/theme';
import renderMarkdownLite from '../utils/markdown';
import './OracleView.css';

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
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `s${Date.now().toString(36)}${Math.random().toString(36).slice(2, 12)}`
  );

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [messages, loading]);

  const quickPrompts = [
    { label: 'Prometheus & Fire', query: 'Summarize the myth of Prometheus' },
    { label: "Zeus's children", query: "Who are Zeus's children?" },
    { label: 'Who is Athena?', query: 'Who is Athena?' },
    { label: 'Athena vs Arachne', query: 'Compare Athena and Arachne' },
    { label: 'Turned into a tree', query: 'Which myths have someone turned into a tree?' },
    { label: 'Stories of hubris', query: 'Which myths are about hubris?' },
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
    /* Full-bleed .section-dark band with an in-band heading block. */
    <section
      className="section-dark oracle-view-section"
      style={{ backgroundImage: `url(${THEME.oracleBg})` }}
    >
      {/* Dimmed atmospheric background overlay */}
      <div className="oracle-view-overlay" aria-hidden="true" />

      {/* Rotating Sun medallion in top right */}
      <div className="oracle-view-sun" aria-hidden="true">
        <img
          src={THEME.oracleSun}
          alt=""
          className="oracle-view-sun-img"
          loading="lazy"
        />
      </div>

      <div className="oracle-view-container">
        <div className="oracle-heading">
          <div className="label oracle-heading-label">THE ORACLE</div>
          <h1 className="oracle-heading-title">Ask what the myths remember</h1>
          <p className="oracle-heading-intro">
            Bring your questions to the stories, figures, and patterns preserved in Chronicle.
            The Oracle can trace lineages, retell myths, compare characters, and uncover recurring themes.
          </p>
        </div>

        {/* Quick Prompts: pill chips in a wrapping row */}
        <div className="oracle-prompts-row" role="group" aria-label="Quick questions">
          {quickPrompts.map((p, i) => (
            <Reveal key={i} delay={i * 40}>
              <button
                type="button"
                onClick={() => handleSend(p.query)}
                className="oracle-prompt-chip"
              >
                ✦ {p.label}
              </button>
            </Reveal>
          ))}
        </div>

        {/* The Chat Parchment Card — torn-edge mask */}
        <Reveal className="oracle-chat-card">
          <div className="oracle-chat-header">
            <img src={THEME.oracleSun} alt="" className="oracle-chat-header-sun" aria-hidden="true" />
            <div>
              <div className="oracle-chat-header-name">The Oracle of Chronicle</div>
              <div className="oracle-chat-header-sub">Keeper of the myths, answers drawn from the archive</div>
            </div>
          </div>
          <div
            className="oracle-messages-area"
            role="log"
            aria-live="polite"
            aria-label="Conversation with the Oracle"
          >
            {messages.map((m, idx) => {
              const isUser = m.role === 'user';
              return (
                <div
                  key={idx}
                  className={`oracle-msg-row ${isUser ? 'user' : 'assistant'}`}
                >
                  <div className="oracle-msg-sender">
                    {isUser ? 'You' : 'Oracle'}
                  </div>

                  {isUser ? (
                    <div className="oracle-bubble-user">
                      {m.content}
                    </div>
                  ) : (
                    <div className="oracle-bubble-assistant">
                      {renderMarkdownLite(m.content)}

                      {/* Attached Lore Dossier Card — shared .card style */}
                      {m.storyCard && (
                        <div className="card oracle-story-card">
                          <div className="oracle-story-card-header">
                            <h4 className="oracle-story-card-title">{m.storyCard.title}</h4>
                            {m.storyCard.theme && (
                              <span className="badge-theme">{m.storyCard.theme}</span>
                            )}
                          </div>
                          {m.storyCard.summary && (
                            <p className="oracle-story-card-summary">
                              {m.storyCard.summary}
                            </p>
                          )}
                          {onSelectMyth && m.storyCard.title && (
                            <button
                              type="button"
                              onClick={() => onSelectMyth(m.storyCard.id || m.storyCard.title)}
                              className="btn-dark"
                              style={{ fontSize: '0.72rem', padding: '6px 14px' }}
                            >
                              Read Full Story in Anthology
                            </button>
                          )}
                        </div>
                      )}

                      {/* Follow-up suggestion chips — only under the latest oracle answer */}
                      {idx === messages.length - 1 && !loading && m.suggestions && m.suggestions.length > 0 && (
                        <div className="oracle-suggestions-row" aria-label="Suggested follow-up questions">
                          {m.suggestions.slice(0, 4).map(s => (
                            <button
                              key={s}
                              type="button"
                              className="oracle-suggestion-chip"
                              onClick={() => handleSend(s)}
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            {/* Three-dot typing indicator while awaiting response */}
            {loading && (
              <div className="oracle-msg-row assistant" role="status" aria-label="Oracle is thinking">
                <div className="oracle-msg-sender">Oracle of Chronicle</div>
                <div className="oracle-typing-indicator" aria-hidden="true">
                  <span className="oracle-typing-dot" />
                  <span className="oracle-typing-dot" />
                  <span className="oracle-typing-dot" />
                </div>
              </div>
            )}

            <div ref={endRef} />
          </div>

          {/* Input Bar: rounded input with round dark submit button */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="oracle-input-bar"
          >
            <input
              type="text"
              aria-label="Ask the Oracle a question"
              maxLength={500}
              placeholder="What do you seek guidance on?"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
              className="oracle-text-input"
            />
            <button
              type="submit"
              className="oracle-submit-button"
              disabled={loading || !inputValue.trim()}
              aria-label="Submit question"
            >
              <span className="oracle-submit-arrow" aria-hidden="true">
                →
              </span>
            </button>
          </form>
        </Reveal>
      </div>
    </section>
  );
}
