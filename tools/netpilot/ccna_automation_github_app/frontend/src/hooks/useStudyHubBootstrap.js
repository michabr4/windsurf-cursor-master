import { useEffect, useState } from 'react';
import {
  fetchFlashcards,
  fetchPracticeQuestions,
  fetchSourcePackage,
  fetchStudyPlan,
  fetchWeakAreas,
} from '../api/client';

const DEFAULT_PROFILE = {
  exam_date: '2026-09-01',
  hours_per_week: 8,
  current_level: 'beginner',
};

const SAMPLE_QUIZ_RESULTS = [
  { domain: 'REST APIs', score_percent: 62, attempts: 2 },
  { domain: 'Python for Automation', score_percent: 48, attempts: 3 },
  { domain: 'JSON/Data Modeling', score_percent: 81, attempts: 1 },
];

export function useStudyHubBootstrap() {
  const [sourcePackage, setSourcePackage] = useState(null);
  const [plan, setPlan] = useState(null);
  const [cards, setCards] = useState([]);
  const [practiceQuestions, setPracticeQuestions] = useState([]);
  const [weakAreas, setWeakAreas] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const [pkg, planData, cardData, questionData, weakData] = await Promise.all([
          fetchSourcePackage(),
          fetchStudyPlan(DEFAULT_PROFILE),
          fetchFlashcards(),
          fetchPracticeQuestions(),
          fetchWeakAreas(SAMPLE_QUIZ_RESULTS),
        ]);

        if (cancelled) return;
        setSourcePackage(pkg);
        setPlan(planData);
        setCards(cardData);
        setPracticeQuestions(questionData);
        setWeakAreas(weakData);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load application data.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  return {
    sourcePackage,
    plan,
    cards,
    practiceQuestions,
    weakAreas,
    error,
    loading,
    ready: Boolean(sourcePackage && plan && !loading),
  };
}
