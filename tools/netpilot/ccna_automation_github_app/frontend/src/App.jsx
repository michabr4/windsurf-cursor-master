import * as React from 'react';
import {
  CCNA_AUTOMATION_RESOURCES,
  CCNA_COMPONENT_MAP,
  EXAM_DURATION_SECONDS,
  EXAM_QUESTION_COUNT,
  FLASH_HELP_VIDEOS,
  SHOW_EXTENDED_LANDSCAPE,
  STUDY_TABS,
  githubWorkflow,
  labMissions,
  navItems,
} from './constants';
import { usePersistedStudyState } from './hooks/usePersistedStudyState';
import { useStudyHubBootstrap } from './hooks/useStudyHubBootstrap';
import {
  buildClue,
  buildDevascWeightedSession,
  buildFlashMultipleChoiceDeck,
  clamp,
  getDateKeyWithOffset,
  getTodayKey,
  hashString,
} from './utils/studyUtils';

const { useEffect, useMemo, useRef } = React;

export default function App() {
  const {
    sourcePackage,
    plan,
    cards,
    practiceQuestions,
    weakAreas,
    error,
    loading,
    ready,
  } = useStudyHubBootstrap();

  const {
    activeStudyTab,
    setActiveStudyTab,
    flashIndex,
    setFlashIndex,
    flashSelections,
    setFlashSelections,
    flashChecked,
    setFlashChecked,
    flashWrongCounts,
    setFlashWrongCounts,
    confidenceLog,
    setConfidenceLog,
    quizAnswers,
    setQuizAnswers,
    quizSubmitted,
    setQuizSubmitted,
    quizReviewMode,
    setQuizReviewMode,
    quizIndex,
    setQuizIndex,
    examMode,
    setExamMode,
    examActive,
    setExamActive,
    examSecondsLeft,
    setExamSecondsLeft,
    difficultyLevel,
    setDifficultyLevel,
    workflowStep,
    workflowScore,
    completedMissions,
    setCompletedMissions,
    dailyStreak,
    streakFreeze,
    setStreakFreeze,
    streakHistory,
    achievementHistory,
    setAchievementHistory,
  } = usePersistedStudyState();

  const flashTouchStartRef = useRef(null);
  const quizTouchStartRef = useRef(null);

  const adaptiveQuestions = useMemo(() => {
    if (!practiceQuestions.length) return [];
    if (difficultyLevel === 'foundation') return practiceQuestions;
    if (difficultyLevel === 'applied') return practiceQuestions;
    return [...practiceQuestions].reverse();
  }, [practiceQuestions, difficultyLevel]);

  const quizQuestions = useMemo(() => {
    if (!adaptiveQuestions.length) return [];
    const sessionSize = EXAM_QUESTION_COUNT;
    return buildDevascWeightedSession(adaptiveQuestions, sessionSize);
  }, [adaptiveQuestions]);

  const devascSessionMix = useMemo(() => {
    const counts = quizQuestions.reduce((acc, question) => {
      acc[question.domain] = (acc[question.domain] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(counts)
      .map(([domain, count]) => ({
        domain,
        count,
        percent: Math.round((count / Math.max(quizQuestions.length, 1)) * 100),
      }))
      .sort((a, b) => a.domain.localeCompare(b.domain));
  }, [quizQuestions]);

  useEffect(() => {
    if (!examMode || !examActive || quizSubmitted) return undefined;
    const timer = window.setInterval(() => {
      setExamSecondsLeft((prev) => {
        if (prev <= 1) {
          window.clearInterval(timer);
          setExamActive(false);
          setQuizSubmitted(true);
          setQuizReviewMode(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [examMode, examActive, quizSubmitted]);

  const answeredQuizCount = quizQuestions.reduce((count, _, idx) => {
    return quizAnswers[idx] === undefined ? count : count + 1;
  }, 0);
  const correctQuizCount = quizQuestions.reduce((count, q, idx) => {
    return quizAnswers[idx] === q.correct_option_index ? count + 1 : count;
  }, 0);

  const baseMastery = weakAreas.length
    ? clamp(
        Math.round(
          ((weakAreas.length - weakAreas.reduce((acc, item) => acc + item.weakness_score, 0)) /
            weakAreas.length) *
            100
        ),
        0,
        100
      )
    : 65;

  const quizMastery = quizQuestions.length
    ? Math.round((correctQuizCount / quizQuestions.length) * 100)
    : 0;

  const ccnaComponentResults = useMemo(() => {
    const bucket = new Map();

    quizQuestions.forEach((question, idx) => {
      const componentMeta =
        CCNA_COMPONENT_MAP[question.domain] || {
          componentCode: '6.0',
          componentLabel: 'CCNA Automation and Programmability',
          objective: 'Review automation and programmability objective alignment',
          officialLink: CCNA_AUTOMATION_RESOURCES.ccnaAutomationTrack,
        };

      const key = `${componentMeta.componentCode}-${componentMeta.objective}`;
      const entry = bucket.get(key) || {
        ...componentMeta,
        total: 0,
        answered: 0,
        correct: 0,
      };

      entry.total += 1;
      if (quizAnswers[idx] !== undefined) entry.answered += 1;
      if (quizAnswers[idx] === question.correct_option_index) entry.correct += 1;

      bucket.set(key, entry);
    });

    return [...bucket.values()]
      .map((entry) => ({
        ...entry,
        percentCorrect: entry.total ? Math.round((entry.correct / entry.total) * 100) : 0,
      }))
      .sort((a, b) => a.componentCode.localeCompare(b.componentCode));
  }, [quizQuestions, quizAnswers]);

  const ccnaImprovementSuggestions = useMemo(() => {
    return ccnaComponentResults
      .filter((entry) => entry.percentCorrect < 80)
      .map((entry) => ({
        ...entry,
        suggestion:
          'Run timed CLI/API scenario reps, validate pre/post state, and document rollback steps to improve live execution confidence.',
      }));
  }, [ccnaComponentResults]);

  const confidenceValues = Object.values(confidenceLog);
  const confidenceMastery = confidenceValues.length
    ? Math.round(
        (confidenceValues.reduce((acc, level) => {
          if (level === 'high') return acc + 100;
          if (level === 'medium') return acc + 70;
          return acc + 40;
        }, 0) /
          (confidenceValues.length * 100)) *
          100
      )
    : 0;

  const missionProgress = Math.round(
    (Object.keys(completedMissions).length / Math.max(labMissions.length, 1)) * 100
  );

  const overallMastery = Math.round(
    (baseMastery * 0.35 + quizMastery * 0.35 + confidenceMastery * 0.2 + missionProgress * 0.1) / 1
  );

  const totalXp =
    Object.keys(completedMissions).length * 160 +
    correctQuizCount * 45 +
    confidenceValues.filter((v) => v === 'high').length * 20 +
    workflowScore * 35 +
    dailyStreak * 10;

  const achievements = useMemo(
    () => [
      {
        id: 'ach-first-quiz',
        title: 'Quiz Rookie',
        unlocked: answeredQuizCount >= 1,
      },
      {
        id: 'ach-quiz-master',
        title: 'Quiz Master',
        unlocked: correctQuizCount >= Math.max(2, Math.floor(quizQuestions.length * 0.8)),
      },
      {
        id: 'ach-lab-runner',
        title: 'Lab Runner',
        unlocked: Object.keys(completedMissions).length >= 2,
      },
      {
        id: 'ach-github-flow',
        title: 'GitHub Flow Hero',
        unlocked: workflowStep >= githubWorkflow.length - 1,
      },
      {
        id: 'ach-streak',
        title: 'Consistency Champion',
        unlocked: dailyStreak >= 5,
      },
    ],
    [
      answeredQuizCount,
      correctQuizCount,
      quizQuestions.length,
      completedMissions,
      workflowStep,
      dailyStreak,
    ]
  );

  useEffect(() => {
    setAchievementHistory((prevHistory) => {
      const existing = new Set(prevHistory.map((item) => item.id));
      const additions = achievements
        .filter((achievement) => achievement.unlocked && !existing.has(achievement.id))
        .map((achievement) => ({
          id: achievement.id,
          title: achievement.title,
          unlockedAt: new Date().toISOString(),
        }));

      if (!additions.length) return prevHistory;
      return [...prevHistory, ...additions];
    });
  }, [achievements]);

  const streakHeatmapDays = useMemo(
    () => Array.from({ length: 21 }, (_, idx) => getDateKeyWithOffset(20 - idx)),
    []
  );

  const recentBadgeHistory = useMemo(
    () =>
      [...achievementHistory]
        .filter((item) => item && typeof item.unlockedAt === 'string')
        .sort((a, b) => b.unlockedAt.localeCompare(a.unlockedAt))
        .slice(0, 6),
    [achievementHistory]
  );

  const flashDeck = useMemo(() => buildFlashMultipleChoiceDeck(cards), [cards]);

  const currentFlashCard = flashDeck[flashIndex] || null;

  const activeQuizQuestion = quizQuestions[quizIndex] || null;

  const currentFlashSelection = currentFlashCard
    ? flashSelections[currentFlashCard.question]
    : undefined;
  const currentFlashCheckState = currentFlashCard ? flashChecked[currentFlashCard.question] : undefined;
  const currentFlashWrongAttempts = currentFlashCard
    ? flashWrongCounts[currentFlashCard.question] || 0
    : 0;

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
      .toString()
      .padStart(2, '0');
    const secs = Math.floor(seconds % 60)
      .toString()
      .padStart(2, '0');
    return `${mins}:${secs}`;
  };

  const resetQuiz = () => {
    setQuizAnswers({});
    setQuizSubmitted(false);
    setQuizReviewMode(false);
    setQuizIndex(0);
    setDifficultyLevel('foundation');
    if (examMode) {
      setExamSecondsLeft(EXAM_DURATION_SECONDS);
      setExamActive(false);
    }
  };

  const finalizeQuiz = () => {
    const today = getTodayKey();
    setStreakHistory((prevHistory) => ({
      ...prevHistory,
      [today]: (prevHistory[today] || 0) + 1,
    }));
    setQuizSubmitted(true);
    setExamActive(false);

    const ratio = quizQuestions.length ? correctQuizCount / quizQuestions.length : 0;
    if (ratio >= 0.8) {
      setDifficultyLevel('challenge');
    } else if (ratio >= 0.5) {
      setDifficultyLevel('applied');
    } else {
      setDifficultyLevel('foundation');
    }
  };

  const handleGradeQuiz = () => {
    setQuizReviewMode(false);
    finalizeQuiz();
  };

  const handleSubmitAll = () => {
    setQuizReviewMode(true);
    finalizeQuiz();
  };

  const startTimedExam = () => {
    setExamMode(true);
    setExamActive(true);
    setExamSecondsLeft(EXAM_DURATION_SECONDS);
    setQuizSubmitted(false);
    setQuizReviewMode(false);
    setQuizAnswers({});
    setQuizIndex(0);
  };

  const switchToPracticeQuiz = () => {
    setExamMode(false);
    setExamActive(false);
    setExamSecondsLeft(EXAM_DURATION_SECONDS);
    setQuizSubmitted(false);
    setQuizReviewMode(false);
    setQuizAnswers({});
    setQuizIndex(0);
  };

  const handleFlashSwipeStart = (event) => {
    flashTouchStartRef.current = event.changedTouches[0].clientX;
  };

  const handleFlashSwipeEnd = (event) => {
    if (flashTouchStartRef.current === null || !cards.length) return;
    const deltaX = event.changedTouches[0].clientX - flashTouchStartRef.current;
    if (Math.abs(deltaX) > 45) {
      setFlashIndex((prev) => {
        if (deltaX < 0) return (prev + 1) % cards.length;
        return (prev - 1 + cards.length) % cards.length;
      });
    }
    flashTouchStartRef.current = null;
  };

  const handleCheckFlashAnswer = () => {
    if (!currentFlashCard) return;
    if (currentFlashSelection === undefined) return;

    const isCorrect = currentFlashSelection === currentFlashCard.correctOptionIndex;
    setFlashChecked((prev) => ({
      ...prev,
      [currentFlashCard.question]: isCorrect ? 'correct' : 'wrong',
    }));

    if (!isCorrect) {
      setFlashWrongCounts((prev) => ({
        ...prev,
        [currentFlashCard.question]: (prev[currentFlashCard.question] || 0) + 1,
      }));
    }
  };

  const handleQuizSwipeStart = (event) => {
    quizTouchStartRef.current = event.changedTouches[0].clientX;
  };

  const handleQuizSwipeEnd = (event) => {
    if (quizTouchStartRef.current === null || !quizQuestions.length) return;
    const deltaX = event.changedTouches[0].clientX - quizTouchStartRef.current;
    if (Math.abs(deltaX) > 45) {
      setQuizIndex((prev) => {
        if (deltaX < 0) return (prev + 1) % quizQuestions.length;
        return (prev - 1 + quizQuestions.length) % quizQuestions.length;
      });
    }
    quizTouchStartRef.current = null;
  };

  if (error) {
    return <main className="app-shell error">{error}</main>;
  }

  if (loading || !ready) {
    return (
      <main className="app-shell loading">Loading Automation + GitHub Training Hub...</main>
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>{sourcePackage.title}</h1>
        <p>Automation + GitHub + Python Skills Simulator</p>
      </header>

      <div className="layout">
        <aside className="sidebar">
          {navItems.map((item) => (
            <a key={item.id} href={`#${item.id}`}>
              {item.label}
            </a>
          ))}
        </aside>

        <main className="content">
          {SHOW_EXTENDED_LANDSCAPE && (
            <section id="exec" className="card">
              <h2>Executive Summary</h2>
              <p>{sourcePackage.platform_vision}</p>
              <div className="metric-grid">
                {sourcePackage.metrics.map((metric) => (
                  <article key={metric.label} className="metric-card">
                    <div className="metric-value">{metric.value}</div>
                    <div className="metric-label">{metric.label}</div>
                  </article>
                ))}
              </div>
            </section>
          )}

          {SHOW_EXTENDED_LANDSCAPE && (
            <section id="arch" className="card">
              <h2>Architecture Map</h2>
              <p>Subsystems extracted from the source architecture package:</p>
              <div className="chip-row">
                {sourcePackage.subsystems.map((subsystem) => (
                  <span key={subsystem} className="chip">
                    {subsystem}
                  </span>
                ))}
              </div>
            </section>
          )}

          {SHOW_EXTENDED_LANDSCAPE && (
            <section id="integration" className="card">
              <h2>Integration Blueprint</h2>
              <div className="table-wrap">
                <table>
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
                    {sourcePackage.integration_matrix.map((row) => (
                      <tr key={`${row.source_target}-${row.protocol}`}>
                        <td>{row.source_target}</td>
                        <td>{row.protocol}</td>
                        <td>{row.format}</td>
                        <td>{row.auth}</td>
                        <td>{row.latency_sla}</td>
                        <td>{row.pattern}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section id="study" className="card">
            <h2>Automation Study Hub</h2>
            <p>{plan.summary}</p>
            <div className="focus-callout">
              <strong>Focused Mode:</strong> Study and testing modules are prioritized.
              {!SHOW_EXTENDED_LANDSCAPE && (
                <span>
                  {' '}
                  Architecture and launch planning views are hidden until fully developed.
                </span>
              )}
            </div>

            <div className="mission-strip">
              <div>
                <p className="label">Overall Mastery</p>
                <h3>{overallMastery}%</h3>
              </div>
              <div>
                <p className="label">XP Earned</p>
                <h3>{totalXp}</h3>
              </div>
              <div>
                <p className="label">Workflow Streak</p>
                <h3>{workflowScore}</h3>
              </div>
              <div>
                <p className="label">Missions Complete</p>
                <h3>
                  {Object.keys(completedMissions).length}/{labMissions.length}
                </h3>
              </div>
              <div>
                <p className="label">Adaptive Level</p>
                <h3>{difficultyLevel}</h3>
              </div>
              <div>
                <p className="label">Daily Streak</p>
                <h3>{dailyStreak} 🔥</h3>
                <button
                  type="button"
                  onClick={() => setStreakFreeze((prevFreeze) => prevFreeze + 1)}
                  className="tiny-btn"
                >
                  + Freeze
                </button>
              </div>
            </div>

            <div className="tab-row">
              {STUDY_TABS.map((tab) => (
                <button
                  key={tab.id}
                  className={activeStudyTab === tab.id ? 'active' : ''}
                  onClick={() => setActiveStudyTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="study-mobile-tabs" aria-label="Study tab quick navigation">
              {STUDY_TABS.map((tab) => (
                <button
                  key={tab.id}
                  className={activeStudyTab === tab.id ? 'active' : ''}
                  onClick={() => setActiveStudyTab(tab.id)}
                >
                  {tab.mobileLabel}
                </button>
              ))}
            </div>

            {activeStudyTab === 'mission' && (
              <div className="study-grid">
                <article className="subcard">
                  <h3>Adaptive Weekly Plan</h3>
                  <div className="button-row">
                    <button
                      onClick={() => {
                        setActiveStudyTab('quiz');
                        setQuizIndex(0);
                        setQuizReviewMode(false);
                      }}
                    >
                      Start Practice
                    </button>
                    <button
                      onClick={() => {
                        setActiveStudyTab('quiz');
                        startTimedExam();
                      }}
                    >
                      Start Timed Exam
                    </button>
                  </div>
                  {plan.weekly_plan.map((week) => (
                    <div key={week.week} className="week-row">
                      <strong>Week {week.week}</strong>
                      <p>{week.focus_domains.join(' · ')}</p>
                    </div>
                  ))}
                </article>

                <article className="subcard">
                  <h3>Learning Context Snapshot</h3>
                  <p className="label">These references are used in quiz rationale</p>
                  <ul className="context-list">
                    {sourcePackage.integration_matrix.slice(0, 3).map((row) => (
                      <li key={`${row.source_target}-${row.protocol}`}>
                        <strong>{row.source_target}</strong> · {row.protocol} · {row.pattern}
                      </li>
                    ))}
                    {sourcePackage.risks.slice(0, 2).map((risk) => (
                      <li key={risk.risk}>
                        <strong>Risk:</strong> {risk.risk} → {risk.mitigation}
                      </li>
                    ))}
                  </ul>
                </article>

                <article className="subcard">
                  <h3>Weak Areas Radar</h3>
                  {weakAreas.map((area) => (
                    <div key={area.domain} className="weak-row">
                      <span>{area.domain}</span>
                      <div className="bar">
                        <span
                          style={{ width: `${Math.round((1 - area.weakness_score) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </article>

                <article className="subcard">
                  <h3>Lab Missions</h3>
                  {labMissions.map((mission) => (
                    <label key={mission.id} className="mission-item">
                      <input
                        type="checkbox"
                        checked={Boolean(completedMissions[mission.id])}
                        onChange={(e) => {
                          const today = getTodayKey();
                          setStreakHistory((prevHistory) => ({
                            ...prevHistory,
                            [today]: (prevHistory[today] || 0) + 1,
                          }));
                          setCompletedMissions((prev) => ({
                            ...prev,
                            [mission.id]: e.target.checked,
                          }));
                        }}
                      />
                      <span>
                        <strong>{mission.title}</strong>
                        <small>{mission.objective}</small>
                        <em>{mission.reward}</em>
                      </span>
                    </label>
                  ))}
                </article>

                <article className="subcard">
                  <h3>Achievements</h3>
                  <div className="achievement-list">
                    {achievements.map((achievement) => (
                      <div
                        key={achievement.id}
                        className={achievement.unlocked ? 'achievement unlocked' : 'achievement'}
                      >
                        <span>{achievement.unlocked ? '🏆' : '🔒'}</span>
                        <strong>{achievement.title}</strong>
                      </div>
                    ))}
                  </div>
                  <p className="label">Streak freeze tokens: {streakFreeze}</p>
                </article>

                <article className="subcard">
                  <h3>Streak Heatmap (21 days)</h3>
                  <div className="heatmap-grid">
                    {streakHeatmapDays.map((dayKey) => {
                      const intensity = Math.min(streakHistory[dayKey] || 0, 4);
                      return (
                        <div
                          key={dayKey}
                          className={`heat-cell lvl-${intensity}`}
                          title={`${dayKey}: ${streakHistory[dayKey] || 0} activities`}
                        />
                      );
                    })}
                  </div>
                  <p className="label">Darker cells = more daily practice actions</p>
                </article>

                <article className="subcard">
                  <h3>Badge Timeline</h3>
                  {recentBadgeHistory.length === 0 ? (
                    <p className="label">No badges unlocked yet.</p>
                  ) : (
                    <div className="timeline-list">
                      {recentBadgeHistory.map((item) => (
                        <div key={item.id} className="timeline-item">
                          <span>🏆</span>
                          <div>
                            <strong>{item.title}</strong>
                            <p>{new Date(item.unlockedAt).toLocaleString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              </div>
            )}

            {activeStudyTab === 'flashcards' && currentFlashCard && (
              <div className="study-grid">
                <article
                  className="subcard flashcard-panel swipe-panel"
                  onTouchStart={handleFlashSwipeStart}
                  onTouchEnd={handleFlashSwipeEnd}
                >
                  <h3>Flashcard Forge</h3>
                  <p className="label">
                    Card {flashIndex + 1} of {flashDeck.length}
                  </p>
                  <p className="label">Multiple-choice drill · swipe left/right on mobile</p>
                  <p>
                    <strong>Q:</strong> {currentFlashCard.question}
                  </p>
                  {currentFlashCard.options.map((option, optionIdx) => (
                    <label key={`${currentFlashCard.question}-${option}`} className="flash-option">
                      <input
                        type="radio"
                        name={`flash-${flashIndex}`}
                        checked={currentFlashSelection === optionIdx}
                        onChange={() => {
                          setFlashSelections((prev) => ({
                            ...prev,
                            [currentFlashCard.question]: optionIdx,
                          }));
                          setFlashChecked((prev) => ({
                            ...prev,
                            [currentFlashCard.question]: null,
                          }));
                        }}
                      />
                      {option}
                    </label>
                  ))}

                  {currentFlashCheckState === 'correct' && (
                    <p className="feedback good">Correct ✅ Great recall for this concept.</p>
                  )}

                  {currentFlashCheckState === 'wrong' && (
                    <>
                      <p className="feedback">
                        Not quite — review the clue and try again. Wrong attempts: {currentFlashWrongAttempts}
                      </p>
                      <p className="option-rationale">
                        {buildClue(currentFlashCard.answer, currentFlashWrongAttempts)}
                      </p>
                      {currentFlashWrongAttempts >= 2 && (
                        <p className="video-link-row">
                          Need a quick explainer?{' '}
                          <a
                            href={
                              FLASH_HELP_VIDEOS[currentFlashCard.domain] ||
                              'https://www.youtube.com/watch?v=rfscVS0vtbw'
                            }
                            target="_blank"
                            rel="noreferrer"
                          >
                            Watch a short help clip
                          </a>
                        </p>
                      )}
                    </>
                  )}

                  <div className="button-row">
                    <button onClick={handleCheckFlashAnswer}>Check Answer</button>
                    <button
                      onClick={() => {
                        setFlashIndex((prev) => (prev + 1) % Math.max(flashDeck.length, 1));
                      }}
                    >
                      Next Card
                    </button>
                  </div>
                  <div className="button-row compact">
                    <button
                      onClick={() =>
                        setConfidenceLog((prev) => ({ ...prev, [currentFlashCard.question]: 'low' }))
                      }
                    >
                      Low Confidence
                    </button>
                    <button
                      onClick={() =>
                        setConfidenceLog((prev) => ({ ...prev, [currentFlashCard.question]: 'medium' }))
                      }
                    >
                      Medium
                    </button>
                    <button
                      onClick={() =>
                        setConfidenceLog((prev) => ({ ...prev, [currentFlashCard.question]: 'high' }))
                      }
                    >
                      High
                    </button>
                  </div>
                </article>
              </div>
            )}

            {activeStudyTab === 'quiz' && (
              <div className="study-grid">
                <article
                  className="subcard swipe-panel"
                  onTouchStart={handleQuizSwipeStart}
                  onTouchEnd={handleQuizSwipeEnd}
                >
                  <h3>Quiz Arena (Policy-Safe)</h3>
                  {practiceQuestions[0] && <p>{practiceQuestions[0].policy_note}</p>}
                  <p className="label">Feedback includes option-level rationale + architecture references</p>
                  <p className="label">Swipe left/right to navigate quiz items</p>
                  <div className="button-row">
                    {examMode ? (
                      <>
                        <button onClick={switchToPracticeQuiz}>Exit Timed Mode</button>
                        <button
                          onClick={() => {
                            setExamActive((prev) => !prev);
                          }}
                        >
                          {examActive ? 'Pause Timer' : 'Resume Timer'}
                        </button>
                      </>
                    ) : (
                      <button onClick={startTimedExam}>Start 45m Timed Exam (50 Questions)</button>
                    )}
                  </div>
                  <p className="label">
                    {examMode
                      ? `Timed Exam · ${formatDuration(examSecondsLeft)} remaining`
                      : 'Practice Mode'}
                  </p>
                  <p className="label">Session Type: 50-question Cisco 200-901 DEVASC practice set</p>
                  <p className="label">
                    Domain Mix:{' '}
                    {devascSessionMix
                      .map((item) => `${item.domain} (${item.count}/${item.percent}%)`)
                      .join(' · ')}
                  </p>
                  <p className="label">
                    Progress: Q {Math.min(quizIndex + 1, Math.max(quizQuestions.length, 1))}/
                    {quizQuestions.length}
                  </p>
                  {activeQuizQuestion && (
                    <div
                      key={
                        activeQuizQuestion.instanceId || `${activeQuizQuestion.prompt}-${quizIndex}`
                      }
                      className="quiz-item"
                    >
                      <p>
                        <strong>{quizIndex + 1}.</strong> {activeQuizQuestion.prompt}
                      </p>
                      {activeQuizQuestion.options.map((opt, optIdx) => (
                        <label key={`${opt}-${optIdx}`}>
                          <input
                            type="radio"
                            name={`q-${quizIndex}`}
                            checked={quizAnswers[quizIndex] === optIdx}
                            onChange={() =>
                              setQuizAnswers((prev) => ({
                                ...prev,
                                [quizIndex]: optIdx,
                              }))
                            }
                          />
                          {opt}
                        </label>
                      ))}
                      {quizSubmitted && (
                        <>
                          <p className="feedback">
                            {quizAnswers[quizIndex] === activeQuizQuestion.correct_option_index
                              ? 'Correct ✅'
                              : 'Review ❗'}{' '}
                            {activeQuizQuestion.explanation}
                          </p>
                          {quizAnswers[quizIndex] !== undefined &&
                            activeQuizQuestion.distractor_rationales?.[quizAnswers[quizIndex]] && (
                              <p className="option-rationale">
                                {activeQuizQuestion.distractor_rationales[quizAnswers[quizIndex]]}
                              </p>
                            )}
                          {Array.isArray(activeQuizQuestion.references) &&
                            activeQuizQuestion.references.length > 0 && (
                              <ul className="refs-list">
                                {activeQuizQuestion.references.map((reference) => (
                                  <li key={reference}>{reference}</li>
                                ))}
                              </ul>
                            )}
                        </>
                      )}
                    </div>
                  )}
                  {quizSubmitted && quizReviewMode && (
                    <div className="quiz-review">
                      <h4>Review Mode</h4>
                      {quizQuestions.map((question, idx) => {
                        const isCorrect = quizAnswers[idx] === question.correct_option_index;
                        return (
                          <div
                            key={question.instanceId || `${question.prompt}-${idx}`}
                            className="review-item"
                          >
                            <p>
                              <strong>Q{idx + 1}:</strong> {question.prompt}
                            </p>
                            <p className={isCorrect ? 'feedback good' : 'feedback'}>
                              {isCorrect ? 'Correct ✅' : 'Incorrect ❌'}
                            </p>
                            <p className="label">{question.explanation}</p>
                            {quizAnswers[idx] !== undefined &&
                              question.distractor_rationales?.[quizAnswers[idx]] && (
                                <p className="option-rationale">
                                  {question.distractor_rationales[quizAnswers[idx]]}
                                </p>
                              )}
                            {Array.isArray(question.references) && question.references.length > 0 && (
                              <ul className="refs-list">
                                {question.references.map((reference) => (
                                  <li key={reference}>{reference}</li>
                                ))}
                              </ul>
                            )}
                            <button onClick={() => setQuizIndex(idx)}>Open This Question</button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                  <div className="button-row">
                    <button onClick={handleGradeQuiz}>Grade Quiz</button>
                    <button onClick={handleSubmitAll}>Submit All + Review</button>
                    <button
                      onClick={() =>
                        setQuizIndex(
                          (prev) =>
                            (prev - 1 + Math.max(quizQuestions.length, 1)) %
                            Math.max(quizQuestions.length, 1)
                        )
                      }
                    >
                      Previous Question
                    </button>
                    <button
                      onClick={() =>
                        setQuizIndex((prev) => (prev + 1) % Math.max(quizQuestions.length, 1))
                      }
                    >
                      Next Question
                    </button>
                    <button onClick={resetQuiz}>Reset</button>
                  </div>
                  <p>
                    Score: {correctQuizCount}/{quizQuestions.length} · Answered {answeredQuizCount}
                  </p>
                  {quizSubmitted && (
                    <div className="quiz-breakdown">
                      <h4>CCNA Automation / DevNet Breakdown</h4>
                      <p className="label">
                        Percent correct mapped to Cisco automation objective areas.
                      </p>
                      <div className="table-wrap">
                        <table>
                          <thead>
                            <tr>
                              <th>Component</th>
                              <th>Objective</th>
                              <th>Correct</th>
                              <th>Percent</th>
                              <th>Cisco Source</th>
                            </tr>
                          </thead>
                          <tbody>
                            {ccnaComponentResults.map((entry) => (
                              <tr key={`${entry.componentCode}-${entry.objective}`}>
                                <td>
                                  {entry.componentCode} · {entry.componentLabel}
                                </td>
                                <td>{entry.objective}</td>
                                <td>
                                  {entry.correct}/{entry.total}
                                </td>
                                <td>{entry.percentCorrect}%</td>
                                <td>
                                  <a href={entry.officialLink} target="_blank" rel="noreferrer">
                                    View Cisco Objective
                                  </a>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <h4>Improvement Plan for Live Scenarios</h4>
                      {ccnaImprovementSuggestions.length === 0 ? (
                        <p className="feedback good">
                          Strong component alignment. Keep drilling timed live-lab scenarios.
                        </p>
                      ) : (
                        <ul className="improvement-list">
                          {ccnaImprovementSuggestions.map((item) => (
                            <li key={`improve-${item.componentCode}-${item.objective}`}>
                              <strong>
                                {item.componentCode} · {item.componentLabel} ({item.percentCorrect}%)
                              </strong>{' '}
                              {item.suggestion}{' '}
                              <a href={item.officialLink} target="_blank" rel="noreferrer">
                                Cisco objective link
                              </a>
                            </li>
                          ))}
                        </ul>
                      )}

                      <div className="resource-links">
                        <a
                          href={CCNA_AUTOMATION_RESOURCES.ccnaAutomationTrack}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Cisco CCNA Automation Learning Track
                        </a>
                        <a
                          href={CCNA_AUTOMATION_RESOURCES.devnetAssociate}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Cisco DevNet Associate Certification
                        </a>
                        <a
                          href={CCNA_AUTOMATION_RESOURCES.ciscoAutomation}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Cisco Automation Fundamentals
                        </a>
                      </div>
                    </div>
                  )}
                  <div className="quiz-sticky-nav">
                    <button
                      onClick={() =>
                        setQuizIndex(
                          (prev) =>
                            (prev - 1 + Math.max(quizQuestions.length, 1)) %
                            Math.max(quizQuestions.length, 1)
                        )
                      }
                    >
                      Prev
                    </button>
                    <span>
                      Q {Math.min(quizIndex + 1, Math.max(quizQuestions.length, 1))}/
                      {quizQuestions.length}
                    </span>
                    <button
                      onClick={() =>
                        setQuizIndex((prev) => (prev + 1) % Math.max(quizQuestions.length, 1))
                      }
                    >
                      Next
                    </button>
                  </div>
                </article>
              </div>
            )}

            <div className="study-note">More advanced simulators will be re-enabled as they mature.</div>
          </section>

          {SHOW_EXTENDED_LANDSCAPE && (
            <section id="launch" className="card">
              <h2>Launch Plan</h2>
              <div className="phase-grid">
                {sourcePackage.launch_phases.map((phase) => (
                  <article key={phase.phase} className="subcard">
                    <h3>{phase.phase}</h3>
                    <p>{phase.timeline}</p>
                    <small>{phase.exit_criteria}</small>
                  </article>
                ))}
              </div>
            </section>
          )}

          {SHOW_EXTENDED_LANDSCAPE && (
            <section id="risk" className="card">
              <h2>Risk Matrix</h2>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Risk</th>
                      <th>Likelihood</th>
                      <th>Impact</th>
                      <th>Mitigation</th>
                      <th>Owner</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sourcePackage.risks.map((risk) => (
                      <tr key={risk.risk}>
                        <td>{risk.risk}</td>
                        <td>{risk.likelihood}</td>
                        <td>{risk.impact}</td>
                        <td>{risk.mitigation}</td>
                        <td>{risk.owner}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
