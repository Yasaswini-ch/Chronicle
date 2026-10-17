import React, { useState, useEffect, useCallback } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';

const ROUND = 8;

export default function QuizView() {
  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [picked, setPicked] = useState(null);
  const [score, setScore] = useState(0);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError(false);
    const seed = Math.floor(Math.random() * 1_000_000);
    fetch(`/api/quiz?n=${ROUND}&seed=${seed}`)
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(q => { setQuestions(q); setIndex(0); setPicked(null); setScore(0); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, []);

  useEffect(() => { load(); }, [load]);

  const q = questions[index];
  const done = questions.length > 0 && index >= questions.length;

  const choose = (i) => {
    if (picked !== null || !q) return;
    setPicked(i);
    if (i === q.answer) setScore(s => s + 1);
  };

  const verdict = (i) => {
    if (picked === null) return '';
    if (i === q.answer) return 'correct';
    return i === picked ? 'wrong' : '';
  };

  return (
    <div style={{ maxWidth: '760px' }}>
      <Reveal style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <SectionIcon name="column" />
          <h2 style={{ fontSize: '1.6rem', margin: 0 }}>Test Yourself</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Eight questions on who was whose parent, what the Romans called the gods, and who appears in which story.
          Every answer comes from the same family records the Oracle uses.
        </p>
      </Reveal>

      {loading && <p style={{ color: 'var(--text-muted)' }}>Preparing questions…</p>}
      {error && (
        <p role="alert" style={{ color: 'var(--accent-garnet)' }}>
          The quiz could not be loaded. <button type="button" className="fig-link" onClick={load}>Try again</button>
        </p>
      )}

      {q && !done && (
        <div className="panel quiz-card" aria-live="polite">
          <div className="quiz-progress">Question {index + 1} of {questions.length} · Score {score}</div>
          <h3 className="quiz-question">{q.question}</h3>
          <div className="quiz-options" role="group" aria-label="Answer choices">
            {q.options.map((opt, i) => (
              <button key={opt} type="button" disabled={picked !== null}
                className={`quiz-option ${verdict(i)}`} onClick={() => choose(i)}>
                {opt}
                {verdict(i) === 'correct' && <span className="sr-only"> (correct)</span>}
                {verdict(i) === 'wrong' && <span className="sr-only"> (your answer, incorrect)</span>}
              </button>
            ))}
          </div>
          {picked !== null && (
            <div className="quiz-feedback">
              <p style={{ margin: '0 0 12px' }}>
                <strong>{picked === q.answer ? 'Correct.' : `Not quite. The answer is ${q.options[q.answer]}.`}</strong>{' '}
                {q.fact}
              </p>
              <button type="button" className="btn-primary" autoFocus onClick={() => { setIndex(index + 1); setPicked(null); }}>
                {index + 1 < questions.length ? 'Next question' : 'See my score'} &rarr;
              </button>
            </div>
          )}
        </div>
      )}

      {done && (
        <div className="panel quiz-card" aria-live="polite">
          <h3 className="quiz-question">You scored {score} out of {questions.length}</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            {score === questions.length ? 'A flawless round. The Oracle bows to you.'
              : score >= questions.length / 2 ? 'Well done. Visit Figures to fill in the gaps.'
              : 'The gods keep their secrets well. Browse Figures and try again.'}
          </p>
          <button type="button" className="btn-primary" autoFocus onClick={load}>New round</button>
        </div>
      )}
    </div>
  );
}
