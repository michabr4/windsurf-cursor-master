import { useEffect, useMemo, useState } from 'react';
import { EXAM_DURATION_SECONDS, STUDY_TABS } from '../constants';
import { getTodayKey } from '../utils/studyUtils';
import { readSessionState, writeSessionState } from '../utils/session';

export function usePersistedStudyState() {
  const persisted = useMemo(() => readSessionState(), []);

  const [activeStudyTab, setActiveStudyTab] = useState(
    STUDY_TABS.some((tab) => tab.id === persisted.activeStudyTab) ? persisted.activeStudyTab : 'mission'
  );
  const [flashIndex, setFlashIndex] = useState(persisted.flashIndex || 0);
  const [flashSelections, setFlashSelections] = useState(persisted.flashSelections || {});
  const [flashChecked, setFlashChecked] = useState(persisted.flashChecked || {});
  const [flashWrongCounts, setFlashWrongCounts] = useState(persisted.flashWrongCounts || {});
  const [confidenceLog, setConfidenceLog] = useState(persisted.confidenceLog || {});
  const [quizAnswers, setQuizAnswers] = useState(persisted.quizAnswers || {});
  const [quizSubmitted, setQuizSubmitted] = useState(Boolean(persisted.quizSubmitted));
  const [quizReviewMode, setQuizReviewMode] = useState(Boolean(persisted.quizReviewMode));
  const [quizIndex, setQuizIndex] = useState(persisted.quizIndex || 0);
  const [examMode, setExamMode] = useState(Boolean(persisted.examMode));
  const [examActive, setExamActive] = useState(Boolean(persisted.examActive));
  const [examSecondsLeft, setExamSecondsLeft] = useState(
    persisted.examSecondsLeft || EXAM_DURATION_SECONDS
  );
  const [difficultyLevel, setDifficultyLevel] = useState(persisted.difficultyLevel || 'foundation');
  const [workflowStep] = useState(persisted.workflowStep || 0);
  const [workflowScore] = useState(persisted.workflowScore || 0);
  const [completedMissions, setCompletedMissions] = useState(persisted.completedMissions || {});
  const [dailyStreak, setDailyStreak] = useState(persisted.dailyStreak || 1);
  const [lastActiveDate, setLastActiveDate] = useState(persisted.lastActiveDate || getTodayKey());
  const [streakFreeze, setStreakFreeze] = useState(persisted.streakFreeze || 1);
  const [streakHistory, setStreakHistory] = useState(persisted.streakHistory || {});
  const [achievementHistory, setAchievementHistory] = useState(persisted.achievementHistory || []);

  useEffect(() => {
    if (STUDY_TABS.some((tab) => tab.id === activeStudyTab)) return;
    setActiveStudyTab('mission');
  }, [activeStudyTab]);

  useEffect(() => {
    writeSessionState({
      activeStudyTab,
      flashIndex,
      flashSelections,
      flashChecked,
      flashWrongCounts,
      confidenceLog,
      quizAnswers,
      quizSubmitted,
      quizReviewMode,
      quizIndex,
      examMode,
      examActive,
      examSecondsLeft,
      difficultyLevel,
      workflowStep,
      workflowScore,
      completedMissions,
      dailyStreak,
      lastActiveDate,
      streakFreeze,
      streakHistory,
      achievementHistory,
    });
  }, [
    activeStudyTab,
    flashIndex,
    flashSelections,
    flashChecked,
    flashWrongCounts,
    confidenceLog,
    quizAnswers,
    quizSubmitted,
    quizReviewMode,
    quizIndex,
    examMode,
    examActive,
    examSecondsLeft,
    difficultyLevel,
    workflowStep,
    workflowScore,
    completedMissions,
    dailyStreak,
    lastActiveDate,
    streakFreeze,
    streakHistory,
    achievementHistory,
  ]);

  useEffect(() => {
    const today = getTodayKey();
    if (today === lastActiveDate) return;

    const prev = new Date(lastActiveDate);
    const cur = new Date(today);
    const dayDiff = Math.round((cur.getTime() - prev.getTime()) / (1000 * 60 * 60 * 24));

    if (dayDiff === 1) {
      setDailyStreak((prevStreak) => prevStreak + 1);
    } else if (dayDiff > 1) {
      if (streakFreeze > 0) {
        setStreakFreeze((prevFreeze) => prevFreeze - 1);
      } else {
        setDailyStreak(1);
      }
    }

    setLastActiveDate(today);
  }, [lastActiveDate, streakFreeze]);

  useEffect(() => {
    const today = getTodayKey();
    setStreakHistory((prevHistory) => {
      if (prevHistory[today]) return prevHistory;
      return { ...prevHistory, [today]: 1 };
    });
  }, []);

  return {
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
    setDailyStreak,
    lastActiveDate,
    streakFreeze,
    setStreakFreeze,
    streakHistory,
    achievementHistory,
    setAchievementHistory,
  };
}
