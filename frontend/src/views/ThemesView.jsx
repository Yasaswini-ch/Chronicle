import React, { useState, useEffect } from 'react';
import Reveal from '../components/Reveal';
import SectionIcon from '../components/SectionIcon';

export default function ThemesView() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/analytics')
      .then(res => res.json())
      .then(data => {
        setAnalytics(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load analytics:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: '40px', textAlign: 'center' }}>Loading corpus analytics...</div>;
  }

  const leaderboard = analytics?.leaderboard || {};
  const mostMentioned = leaderboard.most_mentioned || { character: 'None', count: 0 };
  const mostConnected = leaderboard.most_connected || { character: 'None', connections: 0 };
  const mostDiverse = leaderboard.most_thematic_diversity || { character: 'None', num_themes: 0, themes: [] };
  const topCharacters = leaderboard.leaderboard || [];

  const themeCounts = analytics?.theme_distribution || {};
  const totalMyths = analytics?.total_myths || 1;
  const sortedThemes = Object.entries(themeCounts).sort((a, b) => b[1] - a[1]);

  return (
    <div>
      <Reveal style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <SectionIcon name="bars" />
          <h2 style={{ fontSize: '1.6rem', margin: 0 }}>What Shows Up Most</h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Who gets talked about most, which themes dominate, and how dense the whole collection really is —
          at a glance.
        </p>
      </Reveal>

      {/* Prominence Cards (2x2 layout, no three in a row) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        <Reveal className="card">
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)' }}>
            Most Frequent Figure
          </div>
          <div style={{ fontSize: '1.4rem', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 600 }}>
            {mostMentioned.character}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Appears across {mostMentioned.count} classical narratives
          </div>
        </Reveal>

        <Reveal delay={60} className="card">
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)' }}>
            Most Connected Figure
          </div>
          <div style={{ fontSize: '1.4rem', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 600 }}>
            {mostConnected.character}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            {mostConnected.connections} family, rivalry & alliance ties
          </div>
        </Reveal>

        <Reveal delay={120} className="card">
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)' }}>
            Most Thematically Versatile
          </div>
          <div style={{ fontSize: '1.4rem', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 600 }}>
            {mostDiverse.character}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Shows up across {mostDiverse.num_themes} themes: {(mostDiverse.themes || []).join(', ')}
          </div>
        </Reveal>

        <Reveal delay={180} className="card">
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1.5px', color: 'var(--accent-gold)' }}>
            Total Length
          </div>
          <div style={{ fontSize: '1.4rem', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 600 }}>
            {analytics?.total_words ? analytics.total_words.toLocaleString() : '12,000+'} Words
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            About {Math.round((analytics?.total_words || 0) / totalMyths)} words per myth, unabridged
          </div>
        </Reveal>
      </div>

      {/* Thematic Frequency Bars */}
      <div className="grid-2" style={{ gap: '32px' }}>
        <Reveal className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Which Themes Dominate</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {sortedThemes.map(([theme, count]) => {
              const pct = Math.round((count / totalMyths) * 100);
              return (
                <div key={theme}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '4px' }}>
                    <span style={{ textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-primary)' }}>
                      {theme}
                    </span>
                    <span style={{ color: 'var(--accent-gold)' }}>
                      {count} myths ({pct}%)
                    </span>
                  </div>
                  <div style={{ height: '8px', background: 'var(--bg-surface-elevated)', width: '100%' }}>
                    <div
                      className="theme-bar-fill"
                      style={{
                        height: '100%',
                        width: `${pct}%`,
                        background: 'var(--accent-slate)',
                        borderRight: '2px solid var(--accent-gold)',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Reveal>

        {/* Character Prominence Table */}
        <Reveal delay={120} className="card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '16px' }}>Who Shows Up Most</h3>
          <div style={{ maxHeight: '380px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '8px 4px', fontSize: '0.75rem', textTransform: 'uppercase' }}>Figure</th>
                  <th style={{ padding: '8px 4px', fontSize: '0.75rem', textTransform: 'uppercase' }}>Mentions</th>
                  <th style={{ padding: '8px 4px', fontSize: '0.75rem', textTransform: 'uppercase' }}>Connections</th>
                  <th style={{ padding: '8px 4px', fontSize: '0.75rem', textTransform: 'uppercase' }}>Themes</th>
                </tr>
              </thead>
              <tbody>
                {topCharacters.slice(0, 10).map((c, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '8px 4px', fontWeight: 600, color: 'var(--text-primary)' }}>{c.character}</td>
                    <td style={{ padding: '8px 4px', color: 'var(--text-secondary)' }}>{c.mentions}</td>
                    <td style={{ padding: '8px 4px', color: 'var(--text-secondary)' }}>{c.connections}</td>
                    <td style={{ padding: '8px 4px', color: 'var(--accent-gold)', fontSize: '0.8rem' }}>
                      {(c.themes || []).join(', ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>
      </div>
    </div>
  );
}
