import { DEVASC_DOMAIN_WEIGHTS } from '../constants.js';

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function getTodayKey() {
  return new Date().toISOString().slice(0, 10);
}

export function getDateKeyWithOffset(offsetDays) {
  const date = new Date();
  date.setDate(date.getDate() - offsetDays);
  return date.toISOString().slice(0, 10);
}

export function hashString(value) {
  let hash = 0;
  for (let idx = 0; idx < value.length; idx += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(idx);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function buildFlashMultipleChoiceDeck(cards) {
  const fallbackDistractors = [
    'GET',
    'PUT',
    'DELETE',
    'PATCH',
    'netmiko',
    'ansible',
    'YAML',
    'XML',
  ];

  return cards.map((card) => {
    const distractorPool = [
      ...cards.filter((item) => item.question !== card.question).map((item) => item.answer),
      ...fallbackDistractors,
    ].filter((choice) => choice !== card.answer);

    const uniqueDistractors = [...new Set(distractorPool)]
      .sort((a, b) => hashString(`${card.question}-${a}`) - hashString(`${card.question}-${b}`))
      .slice(0, 3);

    const options = [card.answer, ...uniqueDistractors].sort(
      (a, b) =>
        hashString(`${card.question}-${a}-option`) - hashString(`${card.question}-${b}-option`)
    );

    return {
      ...card,
      options,
      correctOptionIndex: options.findIndex((option) => option === card.answer),
    };
  });
}

export function buildClue(answer, wrongAttempts) {
  const words = answer.split(/\s+/).filter(Boolean);
  const firstLetter = answer[0] ? answer[0].toUpperCase() : '?';

  if (wrongAttempts <= 1) {
    return `Clue: the answer starts with "${firstLetter}" and contains ${words.length} word(s).`;
  }

  const keyword = words.slice(0, 2).join(' ');
  return `Clue: focus on keyword(s) like "${keyword}" and the context of automation best practices.`;
}

export function buildDevascWeightedSession(questions, size) {
  if (!questions.length) return [];

  const byDomain = questions.reduce((acc, question) => {
    if (!acc[question.domain]) acc[question.domain] = [];
    acc[question.domain].push(question);
    return acc;
  }, {});

  const allDomains = Object.keys(byDomain);
  const knownDomains = allDomains.filter((domain) => DEVASC_DOMAIN_WEIGHTS[domain] !== undefined);
  const unknownDomains = allDomains.filter((domain) => DEVASC_DOMAIN_WEIGHTS[domain] === undefined);

  const rawWeights = {};
  if (knownDomains.length > 0) {
    knownDomains.forEach((domain) => {
      rawWeights[domain] = DEVASC_DOMAIN_WEIGHTS[domain];
    });
    if (unknownDomains.length > 0) {
      unknownDomains.forEach((domain) => {
        rawWeights[domain] = 5;
      });
    }
  } else {
    const equalWeight = 100 / Math.max(allDomains.length, 1);
    allDomains.forEach((domain) => {
      rawWeights[domain] = equalWeight;
    });
  }

  const weightedDomains = Object.keys(rawWeights);
  const totalWeight = weightedDomains.reduce((sum, domain) => sum + rawWeights[domain], 0);

  const exactCounts = weightedDomains.map((domain) => {
    const exact = (size * rawWeights[domain]) / totalWeight;
    return {
      domain,
      exact,
      count: Math.floor(exact),
      remainder: exact - Math.floor(exact),
    };
  });

  let assigned = exactCounts.reduce((sum, item) => sum + item.count, 0);
  if (assigned < size) {
    exactCounts
      .sort((a, b) => b.remainder - a.remainder)
      .forEach((item) => {
        if (assigned < size) {
          item.count += 1;
          assigned += 1;
        }
      });
  }

  const domainQueues = exactCounts.reduce((acc, item) => {
    const pool = byDomain[item.domain];
    const generated = Array.from({ length: item.count }, (_, idx) => ({
      ...pool[idx % pool.length],
      instanceId: `${item.domain}-${idx}-${pool[idx % pool.length].prompt}`,
    }));
    acc[item.domain] = generated;
    return acc;
  }, {});

  const session = [];
  while (session.length < size) {
    let pushedThisRound = false;
    weightedDomains.forEach((domain) => {
      if (!domainQueues[domain]?.length || session.length >= size) return;
      session.push(domainQueues[domain].shift());
      pushedThisRound = true;
    });
    if (!pushedThisRound) break;
  }

  return session.slice(0, size).map((question, idx) => ({
    ...question,
    instanceId: `${question.instanceId}-${idx}`,
  }));
}
