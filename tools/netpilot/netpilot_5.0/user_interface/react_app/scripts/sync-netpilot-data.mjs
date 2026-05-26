import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '../../../..');

const sources = {
  dashboard: 'netpilot_5.0/user_interface/learner_ui/LEARNER_DASHBOARD.txt',
  lesson: 'netpilot_5.0/user_interface/learner_ui/LESSON_VIEWER.txt',
  examPrep: 'netpilot_5.0/user_interface/learner_ui/EXAM_PREP_CENTER.txt',
  recommendationEngine: 'netpilot_5.0/training_engine/recommendation_engine/RECOMMENDATION_CORE.txt',
  readinessEngine: 'netpilot_5.0/training_engine/readiness_scoring/READINESS_ENGINE.txt'
};

const architecturePackagePath = '/Users/michabr4/Downloads/NetPilot-5.0-Architecture-Package.html';

function parseStructuredDoc(content) {
  const lines = content.split(/\r?\n/);
  const title = lines[0]?.trim() || '';
  const parsed = { title };

  let currentSection = null;
  for (let i = 1; i < lines.length; i += 1) {
    const raw = lines[i].trim();
    if (!raw) {
      continue;
    }

    if (raw.endsWith(':')) {
      currentSection = raw.slice(0, -1).trim();
      continue;
    }

    if (raw.startsWith('- ') && currentSection) {
      const key = currentSection.replace(/\s+/g, '_').toLowerCase();
      parsed[key] ||= [];
      parsed[key].push(raw.slice(2).trim());
      continue;
    }

    if (currentSection) {
      const key = currentSection.replace(/\s+/g, '_').toLowerCase();
      if (!parsed[key]) {
        parsed[key] = raw;
      }
    }
  }

  return parsed;
}

function stripTags(text) {
  return text.replace(/<[^>]*>/g, '').trim();
}

function decodeEntities(text) {
  return text
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function parseArchitecturePackage(content) {
  const title = decodeEntities((content.match(/<title>([^<]+)<\/title>/i)?.[1] || '').trim());

  const platformVision = decodeEntities(
    stripTags(content.match(/<h3[^>]*>\s*Platform Vision\s*<\/h3>[\s\S]*?<p[^>]*>([\s\S]*?)<\/p>/i)?.[1] || '')
  );

  const metrics = [];
  const metricRegex = /<div[^>]*class="[^"]*metric-val[^"]*"[^>]*>([\s\S]*?)<\/div>[\s\S]*?<div[^>]*class="[^"]*metric-label[^"]*"[^>]*>([\s\S]*?)<\/div>/gi;
  let metricMatch;
  while ((metricMatch = metricRegex.exec(content)) !== null) {
    metrics.push({
      value: decodeEntities(stripTags(metricMatch[1])),
      label: decodeEntities(stripTags(metricMatch[2]))
    });
  }

  const integrationMatrix = [];
  const rowRegex = /<tr[^>]*class="[^"]*hover:bg-white\//gi;
  const rows = content.split(rowRegex).slice(1, 9);

  rows.forEach((row) => {
    const tdMatches = [...row.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/gi)].map((m) => decodeEntities(stripTags(m[1])));
    if (tdMatches.length >= 6) {
      integrationMatrix.push({
        sourceTarget: tdMatches[0],
        protocol: tdMatches[1],
        format: tdMatches[2],
        auth: tdMatches[3],
        latencySla: tdMatches[4],
        pattern: tdMatches[5]
      });
    }
  });

  return {
    title,
    platformVision,
    metrics,
    integrationMatrix
  };
}

const data = Object.fromEntries(
  Object.entries(sources).map(([key, relativePath]) => {
    const absolutePath = path.join(repoRoot, relativePath);
    const content = readFileSync(absolutePath, 'utf8');
    return [key, parseStructuredDoc(content)];
  })
);

if (existsSync(architecturePackagePath)) {
  const architectureContent = readFileSync(architecturePackagePath, 'utf8');
  data.architecturePackage = parseArchitecturePackage(architectureContent);
} else {
  data.architecturePackage = {
    title: 'NetPilot 5.0 Architecture Package',
    platformVision: '',
    metrics: [],
    integrationMatrix: []
  };
}

const outputPath = path.join(__dirname, '../src/generated/netpilotData.json');
writeFileSync(outputPath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
console.log(`Synced NetPilot data -> ${outputPath}`);
