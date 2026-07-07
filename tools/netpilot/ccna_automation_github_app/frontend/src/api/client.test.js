import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchFlashcards, fetchStudyPlan } from './client.js';

describe('api client', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('fetchStudyPlan posts profile JSON', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ summary: 'ok', weekly_plan: [] }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const profile = { exam_date: '2026-09-01', hours_per_week: 8, current_level: 'beginner' };
    await fetchStudyPlan(profile);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/plan'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(profile),
      })
    );
  });

  it('fetchFlashcards requests domain query when provided', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [],
    });
    vi.stubGlobal('fetch', fetchMock);

    await fetchFlashcards('REST APIs');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/flashcards\?domain=REST/)
    );
  });
});
