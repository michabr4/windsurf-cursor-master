/* AI Factory Framework — Role & Framework Data */

const FRAMEWORK = {
  title: "AI Factory Framework",
  subtitle: "Transforming Cisco CX into an Agent-Powered Operating Model",
  tagline: "Every role evolves. Every process accelerates. Every customer wins.",

  pillars: [
    {
      id: "evolution",
      icon: "arrow-up-circle",
      title: "Role Evolution",
      color: "blue",
      headline: "From Doers to Designers",
      description: "Every CX role evolves from executing tasks manually to designing, building, and supervising AI agents that perform those tasks. People become agent architects and orchestrators.",
      keyShift: "Manual Executor → Agent Designer & Orchestrator",
      outcomes: [
        "People focus on judgment, relationships, and strategy",
        "Repetitive work is handled by purpose-built agents",
        "Career paths expand into agent design and AI ops",
        "Domain expertise becomes the blueprint for agent behavior"
      ]
    },
    {
      id: "productivity",
      icon: "zap",
      title: "Productivity Multiplier",
      color: "purple",
      headline: "Same People, 10x Impact",
      description: "AI agents amplify each role's capacity — reducing cycle times, eliminating bottlenecks, and unlocking throughput that was previously impossible with manual processes alone.",
      keyShift: "Linear Capacity → Exponential Throughput",
      outcomes: [
        "Cycle time reduced by 40-80% on key workflows",
        "Each person effectively manages 3-5x their current portfolio",
        "Zero-lag handoffs between process stages",
        "Data-driven decisions replace gut-feel prioritization"
      ]
    },
    {
      id: "operating-model",
      icon: "factory",
      title: "New Operating Model",
      color: "emerald",
      headline: "The AI Factory IS the CX Model",
      description: "The entire CX organization operates as an AI Factory — roles are redefined around the agent lifecycle. Every team member participates in a continuous loop of identifying, building, deploying, governing, and scaling agents.",
      keyShift: "Functional Silos → Agent Lifecycle Teams",
      outcomes: [
        "Unified operating model across all CX functions",
        "Continuous improvement driven by agent performance data",
        "Governance built into every stage, not bolted on after",
        "Scalable: what works for one customer works for thousands"
      ]
    }
  ],

  lifecycle: [
    {
      stage: "Identify",
      icon: "search",
      color: "sky",
      description: "Spot agent opportunities in daily workflows",
      activities: [
        "Map manual, repetitive tasks in your role",
        "Calculate time spent and cycle-time impact",
        "Prioritize by ROI and feasibility",
        "Document the current process as an agent spec"
      ],
      who: "Everyone — domain experts see what AI builders can't"
    },
    {
      stage: "Build",
      icon: "hammer",
      color: "blue",
      description: "Design and develop the agent",
      activities: [
        "Define agent inputs, logic, and outputs",
        "Choose tools and integrations (APIs, data sources)",
        "Build with human-in-the-loop checkpoints",
        "Test against real scenarios from your workflow"
      ],
      who: "Agent builders + domain experts as co-designers"
    },
    {
      stage: "Deploy",
      icon: "rocket",
      color: "indigo",
      description: "Put the agent to work in production",
      activities: [
        "Start with draft-first / human-approved outputs",
        "Run parallel: agent + human for validation period",
        "Monitor accuracy, speed, and user trust",
        "Iterate based on real-world feedback"
      ],
      who: "Delivery leads + the humans the agent supports"
    },
    {
      stage: "Govern",
      icon: "shield-check",
      color: "violet",
      description: "Ensure quality, security, and compliance",
      activities: [
        "Set approval gates for agent actions",
        "Track agent decisions and audit trail",
        "Define escalation paths for edge cases",
        "Review performance weekly with stakeholders"
      ],
      who: "CX leaders + security/compliance partners"
    },
    {
      stage: "Scale",
      icon: "trending-up",
      color: "purple",
      description: "Expand what works across the org",
      activities: [
        "Package successful agents as templates",
        "Share across teams and geographies",
        "Chain agents together for end-to-end automation",
        "Feed learnings back into the Identify stage"
      ],
      who: "AI Factory program team + CX leadership"
    }
  ],

  maturityLevels: [
    {
      level: 1,
      name: "Manual",
      color: "slate",
      description: "All work done by humans, no agent involvement",
      characteristics: [
        "Processes live in email, spreadsheets, and tribal knowledge",
        "Cycle times are long and unpredictable",
        "Quality depends entirely on individual skill",
        "No systematic measurement of process performance"
      ]
    },
    {
      level: 2,
      name: "Assisted",
      color: "blue",
      description: "Agents help with specific tasks, humans drive",
      characteristics: [
        "AI tools used for research, drafting, summarization",
        "Humans review and approve all agent outputs",
        "Some tasks are faster, but workflows are still manual",
        "First KPIs being tracked (cycle time, accuracy)"
      ]
    },
    {
      level: 3,
      name: "Augmented",
      color: "violet",
      description: "Agents handle workflows, humans supervise",
      characteristics: [
        "Multi-step agent chains execute end-to-end processes",
        "Human-in-the-loop gates at critical decision points",
        "Measurable cycle-time reduction (40%+)",
        "Agent performance dashboards in active use"
      ]
    },
    {
      level: 4,
      name: "Autonomous",
      color: "emerald",
      description: "Agents operate independently with governance",
      characteristics: [
        "Agents run full workflows with exception-only human review",
        "Self-improving through feedback loops and metrics",
        "80%+ cycle-time reduction on automated processes",
        "Organization operates as a true AI Factory"
      ]
    }
  ]
};

const CX_ROLES = [
  {
    id: "cxm",
    title: "Customer Experience Manager",
    abbrev: "CXM",
    icon: "heart-handshake",
    color: "blue",
    currentState: {
      summary: "Plays a pivotal role in driving successful adoption and utilization of Cisco technologies and services. Serves as the primary CX point-of-contact for assigned accounts — orchestrating value realization, managing escalations, facilitating business reviews, and aligning cross-functional CX resources to accelerate customer outcomes and growth.",
      painPoints: [
        "Juggling dozens of accounts with no real-time visibility into customer health",
        "Reactive firefighting — issues surface through complaints, not early signals",
        "Hours spent manually compiling business reviews and status updates",
        "Cross-functional coordination across CEs, PMs, and CDAs relies on email and meetings"
      ]
    },
    factoryState: {
      newRole: "Customer Experience Architect",
      summary: "Orchestrates AI agents that continuously monitor customer health, predict risk, synthesize cross-functional intelligence, and draft proactive engagement — freeing the CXM to focus on strategic relationships and customer outcomes.",
      agents: [
        { name: "Customer Health Pulse", desc: "Aggregates telemetry, support cases, adoption signals, and engagement data into a real-time health score per account" },
        { name: "Business Review Generator", desc: "Auto-compiles quarterly and executive business reviews from usage data, delivery milestones, and outcomes" },
        { name: "Proactive Outreach Drafter", desc: "Drafts personalized customer communications based on health signals (human approves before send)" },
        { name: "Cross-Functional Coordinator", desc: "Synthesizes status from CE, PM, and CDA workstreams into a unified customer view and flags gaps" }
      ],
      kpis: [
        { metric: "Time to Risk Detection", before: "Weeks", after: "Hours" },
        { metric: "Business Review Prep", before: "8-12 hours", after: "30 min review" },
        { metric: "Accounts per CXM", before: "15-25", after: "40-60" },
        { metric: "Proactive vs Reactive Ratio", before: "20/80", after: "70/30" }
      ]
    },
    maturityPath: "Manual account management → AI-assisted health monitoring → Agent-driven engagement → Autonomous experience orchestration"
  },
  {
    id: "htom",
    title: "High Touch Operations Manager",
    abbrev: "HTOM",
    icon: "settings",
    color: "violet",
    currentState: {
      summary: "Acts as a strategic support consultant for Cisco's highest-value customers — establishing deep relationships with senior-level operations executives, proactively addressing business and operational constraints, leading cross-functional teams to resolve critical incidents, presenting monthly and quarterly reviews, and reviewing historic customer data to identify trends and enable problem management.",
      painPoints: [
        "Manually tracking SLAs and deliverables across multiple concurrent engagements",
        "Resource coordination across global time zones is error-prone and slow",
        "Operational status reporting consumes days of effort each cycle",
        "Early warning signs of delivery risk are missed until they become escalations"
      ]
    },
    factoryState: {
      newRole: "Operations Intelligence Lead",
      summary: "Architects agents that automate operational oversight — real-time SLA tracking, predictive resource optimization, delivery risk detection, and automated stakeholder reporting across the high-touch portfolio.",
      agents: [
        { name: "SLA Sentinel", desc: "Real-time SLA monitoring with automatic alerting when thresholds approach breach across all active engagements" },
        { name: "Resource Optimizer", desc: "Analyzes workload, skills, availability, and time zones to recommend optimal resource allocation" },
        { name: "Ops Status Generator", desc: "Auto-compiles operational status reports from project tools, delivery milestones, and team inputs" },
        { name: "Delivery Risk Radar", desc: "Scans engagement patterns, resource gaps, and SLA trends to flag delivery risks before they materialize" }
      ],
      kpis: [
        { metric: "Status Report Creation", before: "1-2 days", after: "Auto-generated" },
        { metric: "SLA Breach Detection", before: "Post-breach", after: "Predictive" },
        { metric: "Resource Utilization", before: "65%", after: "85%+" },
        { metric: "Delivery Risk Lead Time", before: "Days", after: "Weeks ahead" }
      ]
    },
    maturityPath: "Manual tracking → AI-assisted monitoring → Agent-driven operations → Autonomous delivery orchestration"
  },
  {
    id: "pm",
    title: "Customer Project Manager",
    abbrev: "PM",
    icon: "gantt-chart",
    color: "sky",
    currentState: {
      summary: "Leads cross-functional project teams responsible for delivering Cisco professional services to enterprise customers — managing project scope, schedule, budget, risk, resource coordination, and stakeholder communication throughout the full delivery lifecycle from initiation through closure.",
      painPoints: [
        "Project plans go stale within days of creation as realities shift",
        "Manual dependency tracking across CEs, CDAs, and customer teams leads to missed handoffs",
        "Stakeholder updates are time-consuming, repetitive, and often inconsistent",
        "Lessons learned from past projects rarely get captured or reused systematically"
      ]
    },
    factoryState: {
      newRole: "Delivery Intelligence Manager",
      summary: "Designs agents that keep project plans alive in real time, automate stakeholder communication at the right level of detail, predict schedule risks from historical patterns, and systematically harvest lessons learned.",
      agents: [
        { name: "Living Plan Agent", desc: "Continuously updates project plans based on actual progress, dependency shifts, and team velocity" },
        { name: "Stakeholder Communicator", desc: "Drafts tailored project updates — executive summary for leaders, technical detail for CEs and CDAs" },
        { name: "Schedule Risk Predictor", desc: "Analyzes historical Cisco delivery patterns to predict delays and recommend mitigations" },
        { name: "Lessons Learned Harvester", desc: "Auto-captures project outcomes, decisions, and reusable patterns for future engagements" }
      ],
      kpis: [
        { metric: "Plan Accuracy", before: "Degrades weekly", after: "Real-time accurate" },
        { metric: "Stakeholder Update Time", before: "3-5 hrs/week", after: "15 min review" },
        { metric: "On-Time Delivery Rate", before: "70%", after: "90%+" },
        { metric: "Knowledge Reuse", before: "Ad hoc", after: "Systematic" }
      ]
    },
    maturityPath: "Static plans → AI-assisted updates → Agent-driven project management → Autonomous delivery orchestration"
  },
  {
    id: "cda",
    title: "Customer Delivery Architect",
    abbrev: "CDA",
    icon: "blocks",
    color: "emerald",
    currentState: {
      summary: "Leads all technical cross-architecture activities and deliverables across the CX services solution portfolio. Works as a trusted advisor from technical staff to CXO level — ensuring Cisco strategy conforms to customer requirements, providing thought leadership in emerging technologies, and identifying challenges and growth opportunities where Cisco solutions can drive business value.",
      painPoints: [
        "Recreating similar architecture designs from scratch for each engagement",
        "Keeping up with rapidly evolving Cisco product capabilities and compatibility",
        "Design validation and documentation takes weeks of manual effort",
        "Technical debt from inconsistent design patterns across engagements"
      ]
    },
    factoryState: {
      newRole: "Delivery Architecture Intelligence Lead",
      summary: "Leverages agents that accelerate solution architecture through pattern matching against proven designs, automated compatibility validation, intelligent design documentation, and continuous Cisco product intelligence.",
      agents: [
        { name: "Architecture Pattern Matcher", desc: "Matches customer requirements against proven Cisco design patterns and past successful implementations" },
        { name: "Compatibility Validator", desc: "Automatically validates designs against Cisco compatibility matrices, EOL data, and known constraints" },
        { name: "Design Doc Generator", desc: "Creates comprehensive HLD/LLD documents from structured inputs and validated architecture patterns" },
        { name: "Product Intelligence Feed", desc: "Continuously monitors Cisco product updates, release notes, bugs, and feature changes relevant to active designs" }
      ],
      kpis: [
        { metric: "Architecture Design Time", before: "2-4 weeks", after: "2-3 days" },
        { metric: "Design Rework Rate", before: "30%", after: "< 10%" },
        { metric: "Pattern Reuse", before: "Informal", after: "80% from library" },
        { metric: "Product Knowledge Currency", before: "Quarterly refresh", after: "Real-time" }
      ]
    },
    maturityPath: "Manual design → AI-assisted validation → Agent-driven architecture generation → Autonomous solution engineering"
  },
  {
    id: "ce",
    title: "Consulting Engineer",
    abbrev: "CE",
    icon: "wrench",
    color: "red",
    currentState: {
      summary: "A technical consulting specialist engaging directly with customers to help them adopt the Cisco products and solutions they purchase — enabling solution architecture with proven business outcomes, performing implementation and configuration, troubleshooting complex issues, and delivering knowledge transfer that drives customer loyalty, satisfaction, and technology-led growth.",
      painPoints: [
        "Repetitive configuration and implementation tasks consume time better spent on complex problems",
        "Troubleshooting often starts from scratch — knowledge trapped in individual expertise",
        "Context is lost during engagement handoffs between CEs or from CE to TAC",
        "Documentation of implementation decisions and configurations is inconsistent"
      ]
    },
    factoryState: {
      newRole: "Consulting Intelligence Engineer",
      summary: "Builds and oversees agents that accelerate implementation, automate routine configurations, maintain full engagement context across handoffs, and mine technical knowledge for reuse — letting the CE focus on the complex, high-judgment work.",
      agents: [
        { name: "Config Accelerator", desc: "Generates validated configuration templates based on customer requirements and Cisco best practices" },
        { name: "Diagnostic Accelerator", desc: "Analyzes logs, configs, and symptoms to suggest probable causes and resolution steps from Cisco knowledge" },
        { name: "Engagement Context Keeper", desc: "Maintains full technical narrative across handoffs — no customer or teammate starts from zero" },
        { name: "Implementation Pattern Miner", desc: "Captures implementation decisions and outcomes to build a reusable knowledge base of what works" }
      ],
      kpis: [
        { metric: "Routine Config Time", before: "Hours per device", after: "Minutes (template-based)" },
        { metric: "Troubleshooting Start Time", before: "From scratch", after: "Contextual head start" },
        { metric: "Handoff Context Loss", before: "Frequent", after: "Near zero" },
        { metric: "Knowledge Reuse Rate", before: "Low / tribal", after: "80%+ systematic" }
      ]
    },
    maturityPath: "Manual implementation → AI-assisted configuration → Agent-driven delivery → Autonomous technical operations"
  },
  {
    id: "sdm",
    title: "Service Delivery Manager",
    abbrev: "SDM",
    icon: "truck",
    color: "indigo",
    currentState: {
      summary: "Sets the strategic services direction and builds trusted advisor relationships with customers, focused on outcomes. Partners with senior leaders across Delivery, Customer Success, Sales, Operations, and Engineering to operationally manage professional services engagements — ensuring contracted services are delivered on time while coordinating across CEs, CDAs, and PMs as the single point of accountability for delivery quality.",
      painPoints: [
        "Manually tracking delivery milestones, entitlements, and consumption across multiple service contracts",
        "Coordinating delivery teams (CEs, CDAs, PMs) across engagements without real-time visibility",
        "Customer communication about delivery status is reactive and labor-intensive",
        "Service gaps and underutilization of contracted entitlements go undetected until reviews"
      ]
    },
    factoryState: {
      newRole: "Service Delivery Intelligence Lead",
      summary: "Orchestrates agents that provide real-time delivery visibility, automate entitlement tracking, predict service gaps before they impact customers, and draft proactive delivery communications — letting the SDM focus on strategic service optimization and customer outcomes.",
      agents: [
        { name: "Delivery Tracker", desc: "Real-time dashboard of all active service deliveries, milestones, and entitlement consumption across the SDM's portfolio" },
        { name: "Entitlement Monitor", desc: "Tracks contracted vs. consumed services and flags underutilization or overrun before they become issues" },
        { name: "Service Gap Predictor", desc: "Analyzes delivery patterns, resource availability, and contract timelines to predict gaps and recommend corrective actions" },
        { name: "Delivery Comms Drafter", desc: "Auto-generates customer-facing delivery status updates and service reports (human approves before send)" }
      ],
      kpis: [
        { metric: "Delivery Visibility", before: "Weekly manual checks", after: "Real-time dashboard" },
        { metric: "Entitlement Utilization", before: "Discovered at QBR", after: "Continuously tracked" },
        { metric: "Service Gap Detection", before: "Reactive", after: "Predictive (weeks ahead)" },
        { metric: "Status Report Time", before: "4-6 hours/cycle", after: "Auto-generated" }
      ]
    },
    maturityPath: "Manual service tracking → AI-assisted monitoring → Agent-driven delivery management → Autonomous service orchestration"
  },
  {
    id: "cpm",
    title: "Customer Program Manager",
    abbrev: "CPM",
    icon: "layout-dashboard",
    color: "orange",
    currentState: {
      summary: "Leads cross-functional teams responsible for major customer lifecycle management and technology refresh programs. Aligns CXMs, PMs, CEs, and CDAs around customer outcomes — managing executive reporting, tracking program-level KPIs, contributing to the Program Manager role community, and ensuring strategic initiatives deliver measurable business results at scale.",
      painPoints: [
        "Program status is assembled manually from multiple workstreams and tools",
        "Cross-team dependencies tracked in the CPM's head or scattered spreadsheets",
        "Executive reporting is a recurring time sink that pulls focus from strategy",
        "Impact measurement across the program portfolio is lagging and approximate"
      ]
    },
    factoryState: {
      newRole: "AI Factory Program Lead",
      summary: "Manages the AI Factory program itself — orchestrates the agent portfolio across CX functions, tracks transformation KPIs, governs the agent lifecycle, and auto-generates executive impact reports.",
      agents: [
        { name: "Program Pulse Dashboard", desc: "Real-time program status aggregated from all CX workstreams, tools, and team updates automatically" },
        { name: "Dependency Tracker", desc: "Maps and monitors cross-team dependencies with automatic risk flagging on blockers across CXM, PM, CE, CDA" },
        { name: "Executive Report Generator", desc: "Auto-compiles executive-ready program reports with KPIs, risks, milestones, and recommendations" },
        { name: "Portfolio Impact Measurer", desc: "Continuously tracks cycle-time reductions, throughput gains, and ROI across the AI Factory agent portfolio" }
      ],
      kpis: [
        { metric: "Program Status Compilation", before: "1-2 days/cycle", after: "Always current" },
        { metric: "Dependency Visibility", before: "Tribal knowledge", after: "Real-time mapped" },
        { metric: "Executive Report Time", before: "4-8 hours", after: "Auto-generated" },
        { metric: "Impact Measurement", before: "Quarterly estimates", after: "Continuous, precise" }
      ]
    },
    maturityPath: "Manual program tracking → AI-assisted reporting → Agent-driven program management → Autonomous portfolio orchestration"
  },
  {
    id: "cx-leader",
    title: "CX Leadership",
    abbrev: "CXL",
    icon: "crown",
    color: "yellow",
    currentState: {
      summary: "Sets Cisco CX strategy, manages P&L, and drives organizational effectiveness across the full CX portfolio. Responsible for ensuring the CX organization delivers measurable customer and business outcomes at scale — aligning CXM, HTOM, PM, CDA, CE, SDM, and CPM functions toward unified customer success.",
      painPoints: [
        "Visibility into real-time org performance is limited to periodic reports",
        "Strategic decisions based on lagging indicators and anecdotal feedback",
        "Scaling delivery capacity means scaling headcount linearly",
        "Innovation happens in pockets, not systematically across the organization"
      ]
    },
    factoryState: {
      newRole: "AI Factory Executive",
      summary: "Leads the AI Factory transformation — sets the vision for agent-powered CX, governs the portfolio, makes investment decisions based on real-time agent performance data, and scales CX impact exponentially without linear headcount growth.",
      agents: [
        { name: "Org Performance Dashboard", desc: "Real-time organizational KPIs across all CX functions — CXM, HTOM, PM, CDA, CE, SDM, CPM — powered by agent and human performance data" },
        { name: "Strategic Signal Aggregator", desc: "Synthesizes customer sentiment, market trends, product signals, and internal metrics into strategic insights" },
        { name: "Investment Recommender", desc: "Analyzes agent ROI data to recommend where to invest next in the AI Factory portfolio" },
        { name: "Innovation Pipeline Monitor", desc: "Tracks agent ideas from identification through deployment, ensuring systematic innovation flow across the CX org" }
      ],
      kpis: [
        { metric: "Decision Latency", before: "Weekly/Monthly cycles", after: "Real-time insights" },
        { metric: "Revenue per CX FTE", before: "Linear growth", after: "Exponential via agents" },
        { metric: "Innovation Throughput", before: "Ad hoc", after: "Systematic pipeline" },
        { metric: "Customer Outcome Velocity", before: "Quarterly measured", after: "Continuously tracked" }
      ]
    },
    maturityPath: "Intuition-driven → Data-assisted decisions → Agent-informed strategy → AI Factory-powered leadership"
  }
];

const ASSESSMENT_QUESTIONS = [
  {
    id: "q1",
    question: "How are repetitive tasks handled in your team today?",
    options: [
      { value: 1, label: "Entirely manual — people do everything by hand" },
      { value: 2, label: "Some AI tools used ad hoc (ChatGPT, Copilot, etc.)" },
      { value: 3, label: "Structured agents handle specific workflows with oversight" },
      { value: 4, label: "Agents run most workflows autonomously with governance" }
    ]
  },
  {
    id: "q2",
    question: "How does your team track and measure process performance?",
    options: [
      { value: 1, label: "We don't systematically measure cycle times" },
      { value: 2, label: "Some metrics tracked manually in spreadsheets" },
      { value: 3, label: "Dashboards track key metrics, some auto-updated" },
      { value: 4, label: "Real-time performance data drives continuous optimization" }
    ]
  },
  {
    id: "q3",
    question: "How does knowledge get shared and reused across your team?",
    options: [
      { value: 1, label: "Tribal knowledge — it lives in people's heads" },
      { value: 2, label: "Some documentation exists but it's often outdated" },
      { value: 3, label: "Knowledge base actively maintained and used by agents" },
      { value: 4, label: "Agents automatically capture, update, and surface knowledge" }
    ]
  },
  {
    id: "q4",
    question: "What's your team's comfort level with AI-assisted workflows?",
    options: [
      { value: 1, label: "Skeptical or unfamiliar — limited exposure" },
      { value: 2, label: "Curious and experimenting — some early adopters" },
      { value: 3, label: "Actively using AI in daily work with clear guidelines" },
      { value: 4, label: "AI-first mindset — team designs and builds agents" }
    ]
  },
  {
    id: "q5",
    question: "How are customer interactions and engagement managed?",
    options: [
      { value: 1, label: "Reactive — we respond when customers reach out" },
      { value: 2, label: "Some proactive outreach based on manual triggers" },
      { value: 3, label: "Agents surface signals and draft proactive actions" },
      { value: 4, label: "Agents orchestrate proactive engagement at scale" }
    ]
  },
  {
    id: "q6",
    question: "How does your organization approach process improvement?",
    options: [
      { value: 1, label: "Rarely — processes stay the same for long periods" },
      { value: 2, label: "Occasionally — improvements happen after pain is felt" },
      { value: 3, label: "Regularly — dedicated effort to identify and automate" },
      { value: 4, label: "Continuously — agent performance data drives ongoing optimization" }
    ]
  }
];
