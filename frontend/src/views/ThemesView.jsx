import React, { useState, useEffect } from 'react';
import PageHeader from '../components/PageHeader';
import Reveal from '../components/Reveal';
import { themeColor } from '../utils/colors';
import { THEME } from '../data/theme';
import './ThemesView.css';

export default function ThemesView({ subTabs }) {
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
    return (
      <div className="page-surface">
        <PageHeader
          label="BY THE NUMBERS"
          title="What Shows Up Most"
          intro="Who gets talked about most, which themes dominate, and how dense the whole collection really is — at a glance."
          image={THEME.treeBg}
        />
        <div className="section-dark">
          <div className="tv-container">
            <div className="tv-loading">Loading corpus analytics…</div>
          </div>
        </div>
      </div>
    );
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
    <div className="page-surface">
      <PageHeader
        label="BY THE NUMBERS"
        title="What Shows Up Most"
        intro="Who gets talked about most, which themes dominate, and how dense the whole collection really is — at a glance."
        image={THEME.treeBg}
      >
        {subTabs}
      </PageHeader>

      <div className="section-dark">
        <div className="tv-container">

          {/* Four stat tiles */}
          <div className="tv-stats-grid">
            <Reveal className="tv-stat-tile">
              <div className="tv-stat-number">{mostMentioned.count}</div>
              <div className="tv-stat-label">Most frequent figure</div>
              <div className="tv-stat-name">{mostMentioned.character}</div>
              <div className="tv-stat-detail">
                Appears across {mostMentioned.count} classical narratives
              </div>
            </Reveal>

            <Reveal delay={60} className="tv-stat-tile">
              <div className="tv-stat-number">{mostConnected.connections}</div>
              <div className="tv-stat-label">Most connected figure</div>
              <div className="tv-stat-name">{mostConnected.character}</div>
              <div className="tv-stat-detail">
                Family, rivalry &amp; alliance ties across the myths
              </div>
            </Reveal>

            <Reveal delay={120} className="tv-stat-tile">
              <div className="tv-stat-number">{mostDiverse.num_themes}</div>
              <div className="tv-stat-label">Most thematically versatile</div>
              <div className="tv-stat-name">{mostDiverse.character}</div>
              <div className="tv-stat-detail">
                Shows up across {(mostDiverse.themes || []).join(', ')}
              </div>
            </Reveal>

            <Reveal delay={180} className="tv-stat-tile">
              <div className="tv-stat-number">
                {analytics?.total_words ? analytics.total_words.toLocaleString() : '12,000+'}
              </div>
              <div className="tv-stat-label">Total corpus words</div>
              <div className="tv-stat-name">Unabridged corpus</div>
              <div className="tv-stat-detail">
                About {Math.round((analytics?.total_words || 0) / totalMyths)} words per myth
              </div>
            </Reveal>
          </div>

          {/* Two-column analytical section */}
          <div className="tv-columns-grid">

            {/* Which themes dominate — horizontal bars */}
            <Reveal className="tv-panel">
              <h3 className="tv-panel-title">Which themes dominate</h3>
              <div className="tv-bars-list">
                {sortedThemes.map(([theme, count]) => {
                  const pct = Math.round((count / totalMyths) * 100);
                  const color = themeColor(theme);
                  return (
                    <div key={theme} className="tv-bar-row">
                      <div className="tv-bar-meta">
                        <span className="tv-bar-name">
                          {theme.charAt(0).toUpperCase() + theme.slice(1).toLowerCase()}
                        </span>
                        <span className="tv-bar-count">{count}</span>
                      </div>
                      <div className="tv-bar-track">
                        <div
                          className="tv-bar-fill"
                          style={{ width: `${pct}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Reveal>

            {/* Who shows up most — table with chips */}
            <Reveal delay={120} className="tv-panel">
              <h3 className="tv-panel-title">Who shows up most</h3>
              <div className="tv-table-scroll">
                <table className="tv-table">
                  <thead>
                    <tr className="tv-thead-row">
                      <th className="tv-th">Figure</th>
                      <th className="tv-th">Mentions</th>
                      <th className="tv-th">Connections</th>
                      <th className="tv-th">Themes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topCharacters.slice(0, 10).map((c, i) => (
                      <tr key={i} className="tv-tr">
                        <td className="tv-td tv-td--name">{c.character}</td>
                        <td className="tv-td tv-td--num">{c.mentions}</td>
                        <td className="tv-td tv-td--num">{c.connections}</td>
                        <td className="tv-td tv-td--themes">
                          <div className="tv-chip-row">
                            {(c.themes || []).map(t => (
                              <span
                                key={t}
                                className="tv-theme-chip"
                                style={{ borderColor: themeColor(t), color: themeColor(t) }}
                              >
                                {t.charAt(0).toUpperCase() + t.slice(1).toLowerCase()}
                              </span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Reveal>

          </div>
        </div>
      </div>
    </div>
  );
}
