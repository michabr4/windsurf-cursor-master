export const SHOW_EXTENDED_LANDSCAPE = false;

export const navItems = [
  { id: 'study', label: 'Automation Study Hub' },
  ...(SHOW_EXTENDED_LANDSCAPE
    ? [
        { id: 'exec', label: 'Executive Summary' },
        { id: 'arch', label: 'Architecture Map' },
        { id: 'integration', label: 'Integration Blueprint' },
        { id: 'launch', label: 'Launch Plan' },
        { id: 'risk', label: 'Risk Matrix' },
      ]
    : []),
];

export const FLASH_HELP_VIDEOS = {
  'REST APIs': 'https://www.youtube.com/watch?v=-mN3VyJuCjM',
  'Python for Automation': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
  'JSON/Data Modeling': 'https://www.youtube.com/watch?v=iiADhChRriM',
};

export const DEVASC_DOMAIN_WEIGHTS = {
  'DEVASC 1.0 Software Development and Design': 15,
  'DEVASC 2.0 Understanding and Using APIs': 20,
  'DEVASC 3.0 Cisco Platforms and Development': 15,
  'DEVASC 4.0 Application Deployment and Security': 20,
  'DEVASC 5.0 Infrastructure and Automation': 30,
};

export const CCNA_AUTOMATION_RESOURCES = {
  ccnaAutomationTrack:
    'https://developer.cisco.com/learning/tracks/network-programmability-basics/',
  devnetAssociate:
    'https://www.cisco.com/site/us/en/learn/training-certifications/certifications/devnet/devnet-associate.html',
  ciscoAutomation: 'https://developer.cisco.com/learning/modules/intro-to-automation/',
};

export const CCNA_COMPONENT_MAP = {
  'DEVASC 1.0 Software Development and Design': {
    componentCode: '1.0',
    componentLabel: 'DEVASC Software Development and Design',
    objective: 'Apply software development fundamentals for network automation tools',
    officialLink: CCNA_AUTOMATION_RESOURCES.devnetAssociate,
  },
  'DEVASC 2.0 Understanding and Using APIs': {
    componentCode: '2.0',
    componentLabel: 'DEVASC Understanding and Using APIs',
    objective: 'Use API requests, response handling, and automation data exchange patterns',
    officialLink: CCNA_AUTOMATION_RESOURCES.ciscoAutomation,
  },
  'DEVASC 3.0 Cisco Platforms and Development': {
    componentCode: '3.0',
    componentLabel: 'DEVASC Cisco Platforms and Development',
    objective: 'Apply automation workflows with Cisco platform capabilities',
    officialLink: CCNA_AUTOMATION_RESOURCES.ccnaAutomationTrack,
  },
  'DEVASC 4.0 Application Deployment and Security': {
    componentCode: '4.0',
    componentLabel: 'DEVASC Application Deployment and Security',
    objective: 'Apply secure deployment and lifecycle controls for automation apps',
    officialLink: CCNA_AUTOMATION_RESOURCES.devnetAssociate,
  },
  'DEVASC 5.0 Infrastructure and Automation': {
    componentCode: '5.0',
    componentLabel: 'DEVASC Infrastructure and Automation',
    objective: 'Explain how automation impacts network management workflows',
    officialLink: CCNA_AUTOMATION_RESOURCES.ccnaAutomationTrack,
  },
};

export const STUDY_TABS = [
  { id: 'mission', label: 'Mission Control', mobileLabel: 'Mission' },
  { id: 'flashcards', label: 'Flashcard Forge', mobileLabel: 'Cards' },
  { id: 'quiz', label: 'Quiz Arena', mobileLabel: 'Quiz' },
];

export const EXAM_QUESTION_COUNT = 50;
export const EXAM_DURATION_SECONDS = 45 * 60;

export const SESSION_KEY = 'automation_study_hub_state_v2';
export const LEGACY_SESSION_KEYS = ['ccna_training_hub_state_v1'];

export const githubWorkflow = [
  'Create issue and define acceptance criteria',
  'Create feature branch from main',
  'Implement and commit automation script changes',
  'Open pull request with test evidence',
  'Run CI checks and fix failures',
  'Squash merge and tag release notes',
];

export const labMissions = [
  {
    id: 'lab-1',
    title: 'API Device Inventory Sync',
    objective: 'Use a REST endpoint to collect device data and normalize JSON fields.',
    reward: '+120 XP',
  },
  {
    id: 'lab-2',
    title: 'GitHub Actions Validation',
    objective: 'Create a workflow that lints Python scripts and validates sample payloads.',
    reward: '+150 XP',
  },
  {
    id: 'lab-3',
    title: 'Config Drift Auto-Remediation',
    objective: 'Detect drift from intended state and generate rollback commands safely.',
    reward: '+180 XP',
  },
];
