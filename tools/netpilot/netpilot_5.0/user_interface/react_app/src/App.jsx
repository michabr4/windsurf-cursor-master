import { useMemo, useState } from 'react';
import netpilotData from './generated/netpilotData.json';

const views = [
  { key: 'dashboard', label: 'Learner Dashboard' },
  { key: 'lesson', label: 'Lesson Viewer' },
  { key: 'examPrep', label: 'Exam Prep Center' },
  { key: 'architecture', label: 'Architecture Package' }
];

function Card({ title, children }) {
  return (
    <section className="card">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function BulletList({ items = [] }) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function normalizeData(data) {
  return {
    dashboard: {
      title: data.dashboard?.title,
      purpose: data.dashboard?.purpose,
      components: data.dashboard?.dashboard_components || []
    },
    lesson: {
      title: data.lesson?.title,
      purpose: data.lesson?.purpose,
      features: data.lesson?.features || []
    },
    examPrep: {
      title: data.examPrep?.title,
      purpose: data.examPrep?.purpose,
      components: data.examPrep?.components || []
    },
    recommendationEngine: {
      title: data.recommendationEngine?.title,
      purpose: data.recommendationEngine?.purpose,
      types: data.recommendationEngine?.recommendation_types || []
    },
    readinessEngine: {
      title: data.readinessEngine?.title,
      purpose: data.readinessEngine?.purpose,
      range: data.readinessEngine?.readiness_score_range || '0–100'
    },
    architecturePackage: {
      title: data.architecturePackage?.title || 'NetPilot 5.0 Architecture Package',
      platformVision: data.architecturePackage?.platformVision || '',
      metrics: data.architecturePackage?.metrics || [],
      integrationMatrix: data.architecturePackage?.integrationMatrix || []
    }
  };
}

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const data = useMemo(() => normalizeData(netpilotData), []);

  const masteryPct = 74;
  const readinessScore = 81;

  return (
    <>
      <div className="bg-orb orb-a" />
      <div className="bg-orb orb-b" />

      <header className="topbar">
        <div className="brand">
          <span className="brand-dot" />
          <div>
            <h1>NetPilot 5.0</h1>
            <p>Learner Experience React App</p>
          </div>
        </div>
        <div className="status-pill">Adaptive Session · Active</div>
      </header>

      <main className="layout">
        <nav className="side-nav">
          {views.map((view) => (
            <button
              key={view.key}
              className={`nav-btn ${activeView === view.key ? 'active' : ''}`}
              onClick={() => setActiveView(view.key)}
            >
              {view.label}
            </button>
          ))}
        </nav>

        <section className="content">
          {activeView === 'dashboard' && (
            <article>
              <div className="view-head">
                <h2>{data.dashboard.title}</h2>
                <p>{data.dashboard.purpose}</p>
              </div>

              <div className="cards grid-3">
                <Card title="Skill Mastery">
                  <div className="meter"><span style={{ width: `${masteryPct}%` }} /></div>
                  <small>Overall mastery: {masteryPct}%</small>
                </Card>

                <Card title="Exam Readiness">
                  <div className="score">{readinessScore}</div>
                  <small>{data.readinessEngine.title}</small>
                  <small>Score range: {data.readinessEngine.range}</small>
                </Card>

                <Card title="Dashboard Components">
                  <BulletList items={data.dashboard.components.slice(0, 5)} />
                </Card>
              </div>

              <div className="cards grid-2">
                <Card title="Recommendation Signals">
                  <p>{data.recommendationEngine.purpose}</p>
                  <BulletList items={data.recommendationEngine.types} />
                </Card>
                <Card title="Recent Activity (Demo)">
                  <ul>
                    <li>Completed: Interface Reliability Patterns</li>
                    <li>Lab Run: Autonomous Interface Optimization</li>
                    <li>Readiness delta: +4 this week</li>
                  </ul>
                </Card>
              </div>
            </article>
          )}

          {activeView === 'lesson' && (
            <article>
              <div className="view-head">
                <h2>{data.lesson.title}</h2>
                <p>{data.lesson.purpose}</p>
              </div>
              <div className="cards grid-2">
                <Card title="Lesson Features">
                  <BulletList items={data.lesson.features} />
                </Card>
                <Card title="Embedded Experience (Demo)">
                  <ul>
                    <li>Interactive checkpoint quiz</li>
                    <li>Inline notes and bookmarks</li>
                    <li>Skill mapping highlight: interface_resilience</li>
                  </ul>
                </Card>
              </div>
            </article>
          )}

          {activeView === 'examPrep' && (
            <article>
              <div className="view-head">
                <h2>{data.examPrep.title}</h2>
                <p>{data.examPrep.purpose}</p>
              </div>
              <div className="cards grid-2">
                <Card title="Preparation Components">
                  <BulletList items={data.examPrep.components} />
                </Card>
                <Card title="Readiness Guidance (Demo)">
                  <p>{data.readinessEngine.purpose}</p>
                  <div className="meter"><span style={{ width: `${readinessScore}%` }} /></div>
                  <small>Current readiness estimate: {readinessScore}/100</small>
                </Card>
              </div>
            </article>
          )}

          {activeView === 'architecture' && (
            <article>
              <div className="view-head">
                <h2>{data.architecturePackage.title}</h2>
                <p>{data.architecturePackage.platformVision}</p>
              </div>

              <div className="cards grid-3">
                {data.architecturePackage.metrics.slice(0, 6).map((metric) => (
                  <Card key={metric.label} title={metric.label}>
                    <div className="score">{metric.value}</div>
                  </Card>
                ))}
              </div>

              <Card title="Integration Matrix">
                <div className="table-wrap">
                  <table className="matrix-table">
                    <thead>
                      <tr>
                        <th>Source → Target</th>
                        <th>Protocol</th>
                        <th>Format</th>
                        <th>Auth</th>
                        <th>Latency SLA</th>
                        <th>Pattern</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.architecturePackage.integrationMatrix.map((row) => (
                        <tr key={`${row.sourceTarget}-${row.protocol}`}>
                          <td>{row.sourceTarget}</td>
                          <td>{row.protocol}</td>
                          <td>{row.format}</td>
                          <td>{row.auth}</td>
                          <td>{row.latencySla}</td>
                          <td>{row.pattern}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </article>
          )}
        </section>
      </main>
    </>
  );
}
