"""Dashboard builder — generates an interactive priority-focused HTML dashboard."""

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from jinja2 import Template

from .config import cfg

DASHBOARD_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flerken Dashboard</title>
<style>
  :root {
    --bg: #0f1117; --surface: #1a1d27; --surface-2: #242833; --border: #2e3240;
    --text: #e4e4e7; --text-dim: #9ca3af; --text-muted: #6b7280;
    --urgent: #ef4444; --urgent-bg: rgba(239,68,68,0.12); --urgent-border: rgba(239,68,68,0.3);
    --action: #f59e0b; --action-bg: rgba(245,158,11,0.12); --action-border: rgba(245,158,11,0.3);
    --fyi: #3b82f6; --fyi-bg: rgba(59,130,246,0.12); --fyi-border: rgba(59,130,246,0.3);
    --low: #22c55e; --low-bg: rgba(34,197,94,0.12); --low-border: rgba(34,197,94,0.3);
    --spam: #6b7280; --purple: #8b5cf6; --purple-bg: rgba(139,92,246,0.15);
    --escalated: #f97316; --escalated-bg: rgba(249,115,22,0.15);
    --customer: #f472b6; --customer-bg: rgba(244,114,182,0.12); --customer-border: rgba(244,114,182,0.3);
    --internal: #64748b; --internal-bg: rgba(100,116,139,0.12); --internal-border: rgba(100,116,139,0.3);
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }

  .header { background: linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#4c1d95 100%); padding:24px 32px; border-bottom:1px solid var(--border); }
  .header-inner { max-width:1400px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; }
  .brand { display:flex; align-items:center; gap:12px; }
  .brand-icon { width:44px; height:44px; background:rgba(255,255,255,0.10); border-radius:10px; display:flex; align-items:center; justify-content:center; padding:4px; }
  .brand h1 { font-size:22px; font-weight:700; letter-spacing:-0.5px; }
  .brand .subtitle { font-size:13px; color:rgba(255,255,255,0.6); margin-top:2px; }
  .header-meta { text-align:right; font-size:13px; color:rgba(255,255,255,0.6); }
  .header-meta .model { color:rgba(255,255,255,0.8); font-weight:500; }
  .container { max-width:1400px; margin:0 auto; padding:24px 32px; }

  /* Priority Cards */
  .priority-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px; }
  .priority-card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; cursor:pointer; transition:all 0.2s; position:relative; overflow:hidden; }
  .priority-card:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(0,0,0,0.3); }
  .priority-card.active { border-width:2px; }
  .priority-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
  .priority-card.urgent { border-color:var(--urgent-border); } .priority-card.urgent::before { background:var(--urgent); } .priority-card.urgent .card-count { color:var(--urgent); }
  .priority-card.action { border-color:var(--action-border); } .priority-card.action::before { background:var(--action); } .priority-card.action .card-count { color:var(--action); }
  .priority-card.fyi { border-color:var(--fyi-border); } .priority-card.fyi::before { background:var(--fyi); } .priority-card.fyi .card-count { color:var(--fyi); }
  .priority-card.low { border-color:var(--low-border); } .priority-card.low::before { background:var(--low); } .priority-card.low .card-count { color:var(--low); }
  .card-count { font-size:36px; font-weight:800; line-height:1; }
  .card-label { font-size:13px; color:var(--text-dim); margin-top:6px; text-transform:uppercase; letter-spacing:0.5px; font-weight:600; }
  .card-sub { font-size:12px; color:var(--text-muted); margin-top:8px; }

  /* Metrics rows */
  .metrics-row { display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:20px; }
  .metric-card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px; display:flex; align-items:center; gap:12px; }
  .metric-icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0; }
  .metric-icon.replies { background:var(--purple-bg); } .metric-icon.unread { background:var(--urgent-bg); }
  .metric-icon.attach { background:var(--action-bg); } .metric-icon.escalated { background:var(--escalated-bg); }
  .metric-icon.tone { background:rgba(236,72,153,0.15); } .metric-icon.recur { background:rgba(6,182,212,0.15); }
  .metric-value { font-size:22px; font-weight:700; }
  .metric-label { font-size:11px; color:var(--text-dim); margin-top:2px; }

  /* Escalation Alerts */
  .alerts-panel { margin-bottom:20px; }
  .alert-item { background:var(--surface); border:1px solid var(--escalated); border-left:4px solid var(--escalated); border-radius:8px; padding:12px 16px; margin-bottom:8px; display:flex; align-items:flex-start; gap:10px; }
  .alert-icon { font-size:16px; margin-top:2px; }
  .alert-body { flex:1; }
  .alert-title { font-size:13px; font-weight:600; color:var(--escalated); }
  .alert-detail { font-size:12px; color:var(--text-dim); margin-top:2px; }

  /* Topic Clusters */
  .topics-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:10px; margin-bottom:20px; }
  .topic-chip { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:10px 14px; cursor:pointer; transition:all 0.15s; }
  .topic-chip:hover { border-color:var(--purple); background:var(--purple-bg); }
  .topic-name { font-size:12px; font-weight:600; color:var(--text); }
  .topic-count { font-size:11px; color:var(--text-muted); margin-top:2px; }
  .topic-bar { height:4px; border-radius:2px; margin-top:6px; background:var(--surface-2); overflow:hidden; }
  .topic-bar-fill { height:100%; border-radius:2px; }

  /* Main Grid */
  .main-grid { display:grid; grid-template-columns:1fr 400px; gap:24px; }
  .panel { background:var(--surface); border:1px solid var(--border); border-radius:12px; overflow:hidden; }
  .panel-header { padding:14px 20px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; }
  .panel-header h2 { font-size:15px; font-weight:600; }
  .panel-header .count { font-size:12px; color:var(--text-muted); background:var(--surface-2); padding:3px 10px; border-radius:20px; }
  .filter-tabs { display:flex; gap:4px; padding:10px 16px; border-bottom:1px solid var(--border); background:var(--surface-2); overflow-x:auto; }
  .filter-tab { padding:5px 12px; border-radius:8px; font-size:11px; font-weight:600; cursor:pointer; border:none; background:transparent; color:var(--text-dim); transition:all 0.15s; white-space:nowrap; }
  .filter-tab:hover { background:var(--border); color:var(--text); }
  .filter-tab.active { background:var(--purple); color:#fff; }
  .email-list { max-height:620px; overflow-y:auto; }
  .email-item { padding:12px 16px; border-bottom:1px solid var(--border); cursor:pointer; transition:background 0.15s; display:flex; gap:10px; }
  .email-item:hover { background:var(--surface-2); }
  .email-item.selected { background:var(--purple-bg); border-left:3px solid var(--purple); }
  .email-dot { width:10px; height:10px; border-radius:50%; margin-top:5px; flex-shrink:0; }
  .email-dot.urgent { background:var(--urgent); } .email-dot.action_required { background:var(--action); }
  .email-dot.fyi { background:var(--fyi); } .email-dot.low_priority { background:var(--low); } .email-dot.spam { background:var(--spam); }
  .email-content { flex:1; min-width:0; }
  .email-top { display:flex; align-items:center; gap:6px; }
  .email-subject { font-size:13px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; }
  .severity-pill { font-size:10px; font-weight:700; padding:2px 6px; border-radius:4px; flex-shrink:0; }
  .email-meta { font-size:11px; color:var(--text-muted); margin-top:3px; display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
  .email-summary-preview { font-size:12px; color:var(--text-dim); margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .badge { display:inline-block; padding:1px 6px; border-radius:4px; font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:0.3px; }
  .badge-unread { background:var(--urgent-bg); color:var(--urgent); }
  .badge-attach { background:var(--action-bg); color:var(--action); }
  .badge-reply { background:var(--purple-bg); color:var(--purple); }
  .badge-escalated { background:var(--escalated-bg); color:var(--escalated); }
  .badge-tone { background:rgba(236,72,153,0.15); color:#ec4899; }
  .badge-recur { background:rgba(6,182,212,0.15); color:#06b6d4; }
  .badge-customer { background:var(--customer-bg); color:var(--customer); }
  .badge-internal { background:var(--internal-bg); color:var(--internal); }

  /* Audience Group Cards */
  .audience-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-bottom:20px; }
  .audience-card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px; cursor:pointer; transition:all 0.2s; }
  .audience-card:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(0,0,0,0.3); }
  .audience-card.active { border-color:var(--customer); box-shadow:0 0 0 1px var(--customer); }
  .audience-card .aud-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
  .audience-card .aud-label { font-size:14px; font-weight:700; }
  .audience-card .aud-count { font-size:22px; font-weight:800; }
  .audience-card .aud-detail { font-size:11px; color:var(--text-muted); line-height:1.5; }
  .audience-card .aud-bar { height:4px; border-radius:2px; margin-top:10px; overflow:hidden; background:var(--surface-2); }
  .audience-card .aud-bar-fill { height:100%; border-radius:2px; }
  .audience-card.customer-card { border-left:3px solid var(--customer); }
  .audience-card.customer-card .aud-label { color:var(--customer); }
  .audience-card.internal-card { border-left:3px solid var(--internal); }
  .audience-card.internal-card .aud-label { color:var(--internal); }

  /* Detail Panel */
  .detail-panel { position:sticky; top:24px; }
  .detail-empty { padding:40px 20px; text-align:center; color:var(--text-muted); font-size:13px; }
  .detail-content { padding:18px; max-height:620px; overflow-y:auto; }
  .detail-cat { display:inline-block; padding:4px 12px; border-radius:6px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:10px; }
  .detail-cat.urgent { background:var(--urgent-bg); color:var(--urgent); }
  .detail-cat.action_required { background:var(--action-bg); color:var(--action); }
  .detail-cat.fyi { background:var(--fyi-bg); color:var(--fyi); }
  .detail-cat.low_priority { background:var(--low-bg); color:var(--low); }
  .detail-cat.spam { background:rgba(107,114,128,0.15); color:var(--spam); }
  .detail-subject { font-size:16px; font-weight:700; line-height:1.4; margin-bottom:8px; }
  .detail-from { font-size:13px; color:var(--text-dim); margin-bottom:4px; }
  .detail-time { font-size:12px; color:var(--text-muted); margin-bottom:14px; }
  .detail-section { margin-bottom:14px; }
  .detail-section-title { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:6px; }
  .detail-summary { font-size:14px; line-height:1.6; color:var(--text-dim); }
  .detail-reasoning { font-size:13px; line-height:1.5; color:var(--text-muted); font-style:italic; }
  .action-item { font-size:13px; color:var(--purple); padding:4px 0; display:flex; align-items:flex-start; gap:8px; }
  .action-item::before { content:'\\2192'; font-weight:700; flex-shrink:0; }
  .draft-reply-box { background:var(--surface-2); border:1px solid var(--border); border-radius:8px; padding:12px; font-size:13px; line-height:1.6; color:var(--text-dim); white-space:pre-wrap; }

  /* Severity gauge */
  .sev-gauge { display:flex; align-items:center; gap:8px; margin-bottom:14px; }
  .sev-bar-track { flex:1; height:8px; background:var(--surface-2); border-radius:4px; overflow:hidden; }
  .sev-bar-fill { height:100%; border-radius:4px; transition:width 0.3s; }
  .sev-label { font-size:12px; font-weight:700; min-width:32px; text-align:right; }
  .sev-factors { list-style:none; padding:0; }
  .sev-factors li { font-size:12px; color:var(--escalated); padding:3px 0; display:flex; align-items:flex-start; gap:6px; }
  .sev-factors li::before { content:'\\26A0'; flex-shrink:0; }
  .signal-tag { display:inline-block; background:var(--surface-2); border:1px solid var(--border); border-radius:4px; padding:2px 8px; font-size:11px; color:var(--text-dim); margin:2px 4px 2px 0; }

  /* Exec summary */
  .exec-summary { margin-top:24px; }
  .exec-summary .panel-body { padding:20px; font-size:14px; line-height:1.8; color:var(--text-dim); }

  /* Scrollbar */
  ::-webkit-scrollbar { width:6px; } ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; } ::-webkit-scrollbar-thumb:hover { background:var(--text-muted); }

  /* Timeline bar */
  .timeline-bar { display:flex; height:6px; border-radius:3px; overflow:hidden; margin-top:8px; background:var(--surface-2); }
  .timeline-seg { transition:width 0.3s; }
  .timeline-seg.urgent { background:var(--urgent); } .timeline-seg.action { background:var(--action); }
  .timeline-seg.fyi { background:var(--fyi); } .timeline-seg.low { background:var(--low); }

  /* Section headings */
  .section-title { font-size:13px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--text-muted); margin-bottom:10px; display:flex; align-items:center; gap:8px; }
  .section-title span { font-size:11px; font-weight:400; }

  @media (max-width:1024px) { .priority-grid { grid-template-columns:repeat(2,1fr); } .main-grid { grid-template-columns:1fr; } .detail-panel { position:static; } .metrics-row { grid-template-columns:repeat(3,1fr); } }
  @media (max-width:640px) { .priority-grid { grid-template-columns:1fr 1fr; } .metrics-row { grid-template-columns:1fr 1fr; } .container { padding:16px; } }
</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <div class="brand">
      <div class="brand-icon"><svg viewBox="0 0 100 100" width="36" height="36" xmlns="http://www.w3.org/2000/svg">
        <!-- Flerken: Marvel's alien cat -->
        <!-- Tentacles (behind head) -->
        <path d="M30 75 Q15 90 8 82 Q2 76 18 68" fill="none" stroke="#c084fc" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
        <path d="M70 75 Q85 90 92 82 Q98 76 82 68" fill="none" stroke="#c084fc" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
        <path d="M40 80 Q35 95 25 92" fill="none" stroke="#a855f7" stroke-width="2.5" stroke-linecap="round" opacity="0.5"/>
        <path d="M60 80 Q65 95 75 92" fill="none" stroke="#a855f7" stroke-width="2.5" stroke-linecap="round" opacity="0.5"/>
        <path d="M50 82 Q50 98 45 95" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
        <!-- Ears -->
        <path d="M22 38 L15 12 L38 30 Z" fill="#f97316" stroke="#ea580c" stroke-width="1.5"/>
        <path d="M78 38 L85 12 L62 30 Z" fill="#f97316" stroke="#ea580c" stroke-width="1.5"/>
        <path d="M24 35 L19 17 L36 31 Z" fill="#fb923c" opacity="0.6"/>
        <path d="M76 35 L81 17 L64 31 Z" fill="#fb923c" opacity="0.6"/>
        <!-- Head -->
        <ellipse cx="50" cy="50" rx="32" ry="30" fill="#f97316"/>
        <!-- Tabby stripes -->
        <path d="M50 22 Q50 30 46 35" stroke="#ea580c" stroke-width="2" fill="none" opacity="0.5"/>
        <path d="M50 22 Q50 30 54 35" stroke="#ea580c" stroke-width="2" fill="none" opacity="0.5"/>
        <path d="M42 25 Q40 33 38 38" stroke="#ea580c" stroke-width="1.5" fill="none" opacity="0.4"/>
        <path d="M58 25 Q60 33 62 38" stroke="#ea580c" stroke-width="1.5" fill="none" opacity="0.4"/>
        <!-- Muzzle -->
        <ellipse cx="50" cy="57" rx="16" ry="12" fill="#fed7aa"/>
        <!-- Eyes (cosmic green glow) -->
        <ellipse cx="38" cy="45" rx="7" ry="7.5" fill="#0a0a0a"/>
        <ellipse cx="62" cy="45" rx="7" ry="7.5" fill="#0a0a0a"/>
        <ellipse cx="38" cy="45" rx="5" ry="6" fill="#22c55e"/>
        <ellipse cx="62" cy="45" rx="5" ry="6" fill="#22c55e"/>
        <!-- Slit pupils -->
        <ellipse cx="38" cy="45" rx="2" ry="5.5" fill="#0a0a0a"/>
        <ellipse cx="62" cy="45" rx="2" ry="5.5" fill="#0a0a0a"/>
        <!-- Eye shine -->
        <circle cx="36" cy="43" r="1.5" fill="#fff" opacity="0.9"/>
        <circle cx="60" cy="43" r="1.5" fill="#fff" opacity="0.9"/>
        <!-- Cosmic eye glow -->
        <ellipse cx="38" cy="45" rx="9" ry="9.5" fill="none" stroke="#4ade80" stroke-width="1" opacity="0.3"/>
        <ellipse cx="62" cy="45" rx="9" ry="9.5" fill="none" stroke="#4ade80" stroke-width="1" opacity="0.3"/>
        <!-- Nose -->
        <path d="M48 54 L50 56.5 L52 54 Z" fill="#f472b6"/>
        <!-- Mouth -->
        <path d="M50 56.5 Q46 61 42 59" fill="none" stroke="#92400e" stroke-width="1.2" stroke-linecap="round"/>
        <path d="M50 56.5 Q54 61 58 59" fill="none" stroke="#92400e" stroke-width="1.2" stroke-linecap="round"/>
        <!-- Whiskers -->
        <line x1="32" y1="54" x2="12" y2="50" stroke="#fdba74" stroke-width="1" opacity="0.7"/>
        <line x1="32" y1="57" x2="10" y2="58" stroke="#fdba74" stroke-width="1" opacity="0.7"/>
        <line x1="32" y1="60" x2="14" y2="66" stroke="#fdba74" stroke-width="1" opacity="0.7"/>
        <line x1="68" y1="54" x2="88" y2="50" stroke="#fdba74" stroke-width="1" opacity="0.7"/>
        <line x1="68" y1="57" x2="90" y2="58" stroke="#fdba74" stroke-width="1" opacity="0.7"/>
        <line x1="68" y1="60" x2="86" y2="66" stroke="#fdba74" stroke-width="1" opacity="0.7"/>
      </svg></div>
      <div>
        <h1>Flerken Dashboard</h1>
        <div class="subtitle">Email Triage &amp; Priority Intelligence</div>
      </div>
    </div>
    <div class="header-meta">
      <div>{{ timestamp }}</div>
      <div class="model">{{ model_name }} &middot; {{ total_emails }} emails &middot; Avg severity {{ avg_severity }}/100</div>
    </div>
  </div>
</div>

<div class="container">

  <div class="timeline-bar" title="Priority distribution">
    <div class="timeline-seg urgent" style="width:{{ pct_urgent }}%"></div>
    <div class="timeline-seg action" style="width:{{ pct_action }}%"></div>
    <div class="timeline-seg fyi" style="width:{{ pct_fyi }}%"></div>
    <div class="timeline-seg low" style="width:{{ pct_low }}%"></div>
  </div>
  <div style="height:16px"></div>

  <!-- Priority Cards -->
  <div class="priority-grid">
    <div class="priority-card urgent active" onclick="filterBy('urgent')">
      <div class="card-count">{{ counts.urgent }}</div>
      <div class="card-label">Urgent</div>
      <div class="card-sub">Needs attention now</div>
    </div>
    <div class="priority-card action" onclick="filterBy('action_required')">
      <div class="card-count">{{ counts.action_required }}</div>
      <div class="card-label">Action Required</div>
      <div class="card-sub">Respond within 1-2 days</div>
    </div>
    <div class="priority-card fyi" onclick="filterBy('fyi')">
      <div class="card-count">{{ counts.fyi }}</div>
      <div class="card-label">FYI</div>
      <div class="card-sub">Good to know</div>
    </div>
    <div class="priority-card low" onclick="filterBy('low_priority')">
      <div class="card-count">{{ counts.low_priority }}</div>
      <div class="card-label">Low Priority</div>
      <div class="card-sub">Can wait</div>
    </div>
  </div>

  <!-- Extended Metrics -->
  <div class="metrics-row">
    <div class="metric-card">
      <div class="metric-icon replies">&#9993;</div>
      <div><div class="metric-value">{{ needs_reply }}</div><div class="metric-label">Need replies &middot; {{ draft_count }} drafts</div></div>
    </div>
    <div class="metric-card">
      <div class="metric-icon unread">&#128308;</div>
      <div><div class="metric-value">{{ unread_count }}</div><div class="metric-label">Unread</div></div>
    </div>
    <div class="metric-card">
      <div class="metric-icon attach">&#128206;</div>
      <div><div class="metric-value">{{ attachment_count }}</div><div class="metric-label">Attachments</div></div>
    </div>
    <div class="metric-card">
      <div class="metric-icon escalated">&#9888;</div>
      <div><div class="metric-value">{{ escalated_count }}</div><div class="metric-label">Escalated by AI</div></div>
    </div>
    <div class="metric-card">
      <div class="metric-icon tone">&#128483;</div>
      <div><div class="metric-value">{{ hot_tone_count }}</div><div class="metric-label">Hot tone detected</div></div>
    </div>
    <div class="metric-card">
      <div class="metric-icon recur">&#128257;</div>
      <div><div class="metric-value">{{ recurring_topics }}</div><div class="metric-label">Recurring topics</div></div>
    </div>
  </div>

  <!-- Escalation Alerts -->
  {% if alerts %}
  <div class="section-title">&#9888; Escalation Alerts <span>(severity raised by AI reasoning)</span></div>
  <div class="alerts-panel">
    {% for alert in alerts %}
    <div class="alert-item">
      <div class="alert-icon">&#128293;</div>
      <div class="alert-body">
        <div class="alert-title">{{ alert.subject }}</div>
        <div class="alert-detail">{{ alert.factors | join(' | ') }}</div>
      </div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <!-- Topic Clusters -->
  {% if topic_clusters %}
  <div class="section-title">&#128279; Topic Clusters <span>(recurring threads)</span></div>
  <div class="topics-grid">
    {% for topic in topic_clusters %}
    <div class="topic-chip" onclick="filterByTopic('{{ topic.key }}')">
      <div class="topic-name">{{ topic.key }}</div>
      <div class="topic-count">{{ topic.count }} email{{ 's' if topic.count > 1 else '' }} &middot; max severity {{ topic.max_severity }}</div>
      <div class="topic-bar"><div class="topic-bar-fill" style="width:{{ topic.bar_pct }}%;background:{{ topic.color }}"></div></div>
    </div>
    {% endfor %}
  </div>
  {% endif %}

  <!-- Audience Grouping -->
  <div class="section-title">&#127919; Audience Grouping <span>(customer vs internal)</span></div>
  <div class="audience-grid">
    {% for cust in customer_cards %}
    <div class="audience-card customer-card" onclick="filterByAudience('{{ cust.name }}')">
      <div class="aud-header">
        <div class="aud-label">{{ cust.name }}</div>
        <div class="aud-count">{{ cust.count }}</div>
      </div>
      <div class="aud-detail">
        {{ cust.urgent }} urgent &middot; {{ cust.action }} action &middot; avg severity {{ cust.avg_severity }}/100
      </div>
      <div class="aud-bar"><div class="aud-bar-fill" style="width:{{ cust.avg_severity }}%;background:var(--customer)"></div></div>
    </div>
    {% endfor %}
    <div class="audience-card internal-card" onclick="filterByAudience('internal')">
      <div class="aud-header">
        <div class="aud-label">Internal</div>
        <div class="aud-count">{{ internal_count }}</div>
      </div>
      <div class="aud-detail">
        {{ internal_urgent }} urgent &middot; {{ internal_action }} action &middot; avg severity {{ internal_avg_severity }}/100
      </div>
      <div class="aud-bar"><div class="aud-bar-fill" style="width:{{ internal_avg_severity }}%;background:var(--internal)"></div></div>
    </div>
  </div>

  <!-- Main Content -->
  <div class="main-grid">
    <div class="panel">
      <div class="panel-header">
        <h2>Triaged Emails</h2>
        <span class="count" id="visible-count">{{ total_emails }} emails</span>
      </div>
      <div class="filter-tabs">
        <button class="filter-tab active" onclick="filterBy('all')">All</button>
        <button class="filter-tab" onclick="filterBy('urgent')">Urgent ({{ counts.urgent }})</button>
        <button class="filter-tab" onclick="filterBy('action_required')">Action ({{ counts.action_required }})</button>
        <button class="filter-tab" onclick="filterBy('fyi')">FYI ({{ counts.fyi }})</button>
        <button class="filter-tab" onclick="filterBy('low_priority')">Low ({{ counts.low_priority }})</button>
        <button class="filter-tab" onclick="filterBy('escalated')">Escalated ({{ escalated_count }})</button>
        <button class="filter-tab" onclick="filterBy('needs_reply')">Needs Reply ({{ needs_reply }})</button>
        <button class="filter-tab" onclick="filterByAudience('customer')">Customer ({{ customer_total }})</button>
        <button class="filter-tab" onclick="filterByAudience('internal')">Internal ({{ internal_count }})</button>
      </div>
      <div class="email-list" id="email-list">
        {% for item in triaged %}
        <div class="email-item" data-idx="{{ loop.index0 }}" data-cat="{{ item.triage.category }}" data-topic="{{ item.triage.topic_key }}" data-reply="{{ item.triage.needs_reply }}" data-escalated="{{ 'yes' if item.triage.severity_factors else 'no' }}" data-audience="{{ item.triage.audience or 'internal' }}" data-customer="{{ item.triage.customer_name or '' }}" onclick="selectEmail({{ loop.index0 }})">
          <div class="email-dot {{ item.triage.category }}"></div>
          <div class="email-content">
            <div class="email-top">
              <div class="email-subject">{{ item.email.subject }}</div>
              <div class="severity-pill" style="background:{{ 'var(--urgent-bg)' if item.triage.severity_score >= 70 else 'var(--action-bg)' if item.triage.severity_score >= 50 else 'var(--surface-2)' }};color:{{ 'var(--urgent)' if item.triage.severity_score >= 70 else 'var(--action)' if item.triage.severity_score >= 50 else 'var(--text-muted)' }}">{{ item.triage.severity_score }}</div>
            </div>
            <div class="email-meta">
              <span>{{ item.email.from_name or item.email.from }}</span>
              <span>&middot;</span>
              <span>{{ item.email.received[:16] }}</span>
              {% if not item.email.is_read %}<span class="badge badge-unread">NEW</span>{% endif %}
              {% if item.email.has_attachments %}<span class="badge badge-attach">FILE</span>{% endif %}
              {% if item.triage.needs_reply %}<span class="badge badge-reply">REPLY</span>{% endif %}
              {% if item.triage.severity_factors %}<span class="badge badge-escalated">ESCALATED</span>{% endif %}
              {% if item.triage.tone in ['frustrated','escalating','urgent'] %}<span class="badge badge-tone">{{ item.triage.tone }}</span>{% endif %}
              {% if item.triage.recurrence_count >= 2 %}<span class="badge badge-recur">{{ item.triage.recurrence_count }}x</span>{% endif %}
              {% if item.triage.customer_name %}<span class="badge badge-customer">{{ item.triage.customer_name }}</span>{% elif item.triage.audience == 'internal' %}<span class="badge badge-internal">INTERNAL</span>{% endif %}
            </div>
            <div class="email-summary-preview">{{ item.triage.summary }}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>

    <!-- Detail Panel -->
    <div class="panel detail-panel" id="detail-panel">
      <div class="panel-header"><h2>Email Detail</h2></div>
      <div class="detail-empty" id="detail-empty">Click an email to view triage details</div>
      <div class="detail-content" id="detail-content" style="display:none"></div>
    </div>
  </div>

  <!-- Executive Summary -->
  <div class="exec-summary panel" style="margin-top:24px;">
    <div class="panel-header"><h2>Executive Summary</h2><span class="count">AI-generated</span></div>
    <div class="panel-body">{{ executive_summary | replace('\\n', '<br>') }}</div>
  </div>
</div>

<script>
const DATA = {{ data_json }};

function sevColor(s) { return s>=70?'var(--urgent)':s>=50?'var(--action)':s>=30?'var(--fyi)':'var(--low)'; }

function selectEmail(idx) {
  document.querySelectorAll('.email-item').forEach(el => el.classList.remove('selected'));
  document.querySelector(`.email-item[data-idx="${idx}"]`)?.classList.add('selected');
  const d=DATA[idx], e=d.email, t=d.triage;
  let html=`
    <span class="detail-cat ${t.category}">${t.category.replace(/_/g,' ')}</span>
    ${t.original_category && t.original_category!==t.category ? `<span style="font-size:11px;color:var(--escalated);margin-left:6px">was: ${t.original_category.replace(/_/g,' ')}</span>` : ''}
    <div class="detail-subject">${e.subject}</div>
    <div class="detail-from">From: ${e.from_name||e.from} &lt;${e.from}&gt;</div>
    <div class="detail-time">${e.received} &middot; Importance: ${e.importance} &middot; Tone: <strong>${t.tone||'neutral'}</strong></div>

    <div class="sev-gauge">
      <div class="sev-bar-track"><div class="sev-bar-fill" style="width:${t.severity_score||0}%;background:${sevColor(t.severity_score||0)}"></div></div>
      <div class="sev-label" style="color:${sevColor(t.severity_score||0)}">${t.severity_score||0}</div>
    </div>`;

  if(t.severity_factors&&t.severity_factors.length){
    html+=`<div class="detail-section"><div class="detail-section-title">Severity Factors</div><ul class="sev-factors">`;
    t.severity_factors.forEach(f=>{html+=`<li>${f}</li>`;});
    html+=`</ul></div>`;
  }

  html+=`<div class="detail-section"><div class="detail-section-title">AI Summary</div><div class="detail-summary">${t.summary}</div></div>`;

  if(t.escalation_signals&&t.escalation_signals.length){
    html+=`<div class="detail-section"><div class="detail-section-title">Escalation Signals</div><div>`;
    t.escalation_signals.forEach(s=>{html+=`<span class="signal-tag">${s}</span>`;});
    html+=`</div></div>`;
  }

  if(t.action_items&&t.action_items.length){
    html+=`<div class="detail-section"><div class="detail-section-title">Action Items</div>`;
    t.action_items.forEach(a=>{html+=`<div class="action-item">${a}</div>`;});
    html+=`</div>`;
  }
  if(t.draft_reply){html+=`<div class="detail-section"><div class="detail-section-title">Draft Reply</div><div class="draft-reply-box">${t.draft_reply}</div></div>`;}
  if(t.reasoning){html+=`<div class="detail-section"><div class="detail-section-title">AI Reasoning</div><div class="detail-reasoning">${t.reasoning}</div></div>`;}

  let meta=[];
  if(t.audience==='customer'&&t.customer_name) meta.push(`<span style="color:var(--customer);font-weight:600">Customer: ${t.customer_name}</span>`);
  else meta.push(`<span style="color:var(--internal)">Internal</span>`);
  if(t.recurrence_count>1) meta.push(`Topic seen ${t.recurrence_count}x`);
  if(t.sender_frequency>1) meta.push(`Sender sent ${t.sender_frequency} emails`);
  if(t.topic_key) meta.push(`Topic: ${t.topic_key}`);
  if(t.urgency_score) meta.push(`Urgency: ${t.urgency_score}/10`);
  if(meta.length){html+=`<div class="detail-section"><div class="detail-section-title">Metadata</div><div style="font-size:12px;color:var(--text-muted)">${meta.join(' &middot; ')}</div></div>`;}

  document.getElementById('detail-empty').style.display='none';
  const dc=document.getElementById('detail-content');
  dc.style.display='block'; dc.innerHTML=html;
}

function filterBy(cat) {
  document.querySelectorAll('.filter-tab').forEach(t=>t.classList.remove('active'));
  if(event&&event.target) event.target.classList.add('active');
  const items=document.querySelectorAll('.email-item');
  let visible=0;
  items.forEach(el=>{
    let show=cat==='all'
      ||(cat==='needs_reply'&&el.dataset.reply==='True')
      ||(cat==='escalated'&&el.dataset.escalated==='yes')
      ||(el.dataset.cat===cat);
    el.style.display=show?'flex':'none';
    if(show)visible++;
  });
  document.getElementById('visible-count').textContent=visible+' email'+(visible!==1?'s':'');
  document.querySelectorAll('.priority-card').forEach(c=>c.classList.remove('active'));
  const m={urgent:'urgent',action_required:'action',fyi:'fyi',low_priority:'low'};
  if(m[cat]) document.querySelector(`.priority-card.${m[cat]}`)?.classList.add('active');
}

function filterByAudience(audience) {
  const items=document.querySelectorAll('.email-item');
  let visible=0;
  items.forEach(el=>{
    let show=false;
    if(audience==='customer') show=el.dataset.audience==='customer';
    else if(audience==='internal') show=el.dataset.audience==='internal';
    else show=el.dataset.customer===audience;
    el.style.display=show?'flex':'none';
    if(show)visible++;
  });
  document.getElementById('visible-count').textContent=visible+' email'+(visible!==1?'s':'')+' ('+audience+')';
  document.querySelectorAll('.filter-tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.audience-card').forEach(c=>c.classList.remove('active'));
  const clicked=document.querySelector(`.audience-card[onclick*="${audience}"]`);
  if(clicked) clicked.classList.add('active');
}

function filterByTopic(key) {
  const items=document.querySelectorAll('.email-item');
  let visible=0;
  items.forEach(el=>{
    let show=el.dataset.topic===key;
    el.style.display=show?'flex':'none';
    if(show)visible++;
  });
  document.getElementById('visible-count').textContent=visible+' email'+(visible!==1?'s':'')+' (topic: '+key+')';
  document.querySelectorAll('.filter-tab').forEach(t=>t.classList.remove('active'));
}

document.addEventListener('DOMContentLoaded',()=>{
  const first=document.querySelector('.email-item');
  if(first) selectEmail(parseInt(first.dataset.idx));
});
</script>
</body>
</html>
""")


def build_dashboard(triaged: list[dict[str, Any]], executive_summary: str) -> str:
    """Generate an interactive HTML dashboard from triaged email data."""
    counts = {"urgent": 0, "action_required": 0, "fyi": 0, "low_priority": 0, "spam": 0}
    needs_reply = 0
    draft_count = 0
    unread_count = 0
    attachment_count = 0
    escalated_count = 0
    hot_tone_count = 0
    total_severity = 0
    topic_data: dict[str, dict] = {}
    alerts: list[dict] = []

    for item in triaged:
        t = item["triage"]
        e = item["email"]
        cat = t.get("category", "low_priority")
        counts[cat] = counts.get(cat, 0) + 1

        if t.get("needs_reply"):
            needs_reply += 1
        if t.get("draft_reply"):
            draft_count += 1
        if not e.get("is_read"):
            unread_count += 1
        if e.get("has_attachments"):
            attachment_count += 1
        if t.get("severity_factors"):
            escalated_count += 1
            alerts.append({
                "subject": e.get("subject", ""),
                "factors": t["severity_factors"],
            })
        if t.get("tone") in ("frustrated", "escalating", "urgent"):
            hot_tone_count += 1

        sev = t.get("severity_score", 0)
        total_severity += sev

        tk = t.get("topic_key", "unknown")
        if tk not in topic_data:
            topic_data[tk] = {"count": 0, "max_severity": 0}
        topic_data[tk]["count"] += 1
        topic_data[tk]["max_severity"] = max(topic_data[tk]["max_severity"], sev)

    total = len(triaged) or 1
    avg_severity = round(total_severity / total)
    recurring_topics = sum(1 for v in topic_data.values() if v["count"] >= 2)

    # ── Audience / Customer grouping ──
    customer_data: dict[str, dict] = {}
    internal_items: list[dict] = []
    for item in triaged:
        t = item["triage"]
        audience = t.get("audience", "internal")
        cust = t.get("customer_name")
        if audience == "customer" and cust:
            if cust not in customer_data:
                customer_data[cust] = {"count": 0, "urgent": 0, "action": 0, "sev_total": 0}
            customer_data[cust]["count"] += 1
            customer_data[cust]["sev_total"] += t.get("severity_score", 0)
            cat = t.get("category", "low_priority")
            if cat == "urgent":
                customer_data[cust]["urgent"] += 1
            elif cat == "action_required":
                customer_data[cust]["action"] += 1
        else:
            internal_items.append(item)

    customer_cards = []
    for name, info in sorted(customer_data.items(), key=lambda x: -x[1]["sev_total"]):
        customer_cards.append({
            "name": name,
            "count": info["count"],
            "urgent": info["urgent"],
            "action": info["action"],
            "avg_severity": round(info["sev_total"] / info["count"]) if info["count"] else 0,
        })

    customer_total = sum(c["count"] for c in customer_cards)
    internal_count = len(internal_items)
    internal_urgent = sum(1 for i in internal_items if i["triage"].get("category") == "urgent")
    internal_action = sum(1 for i in internal_items if i["triage"].get("category") == "action_required")
    internal_sev = sum(i["triage"].get("severity_score", 0) for i in internal_items)
    internal_avg_severity = round(internal_sev / internal_count) if internal_count else 0

    # Build topic clusters for display (only show topics with 2+ emails or high severity)
    topic_clusters = []
    for key, info in sorted(topic_data.items(), key=lambda x: (-x[1]["max_severity"], -x[1]["count"])):
        if info["count"] >= 2 or info["max_severity"] >= 60:
            ms = info["max_severity"]
            color = "var(--urgent)" if ms >= 70 else "var(--action)" if ms >= 50 else "var(--fyi)" if ms >= 30 else "var(--low)"
            topic_clusters.append({
                "key": key,
                "count": info["count"],
                "max_severity": ms,
                "bar_pct": ms,
                "color": color,
            })

    now = datetime.now(timezone.utc).strftime("%A, %B %d %Y at %H:%M UTC")

    return DASHBOARD_TEMPLATE.render(
        timestamp=now,
        model_name=cfg.LLM_MODEL,
        total_emails=len(triaged),
        counts=counts,
        avg_severity=avg_severity,
        pct_urgent=round(counts["urgent"] / total * 100),
        pct_action=round(counts["action_required"] / total * 100),
        pct_fyi=round(counts["fyi"] / total * 100),
        pct_low=round(counts["low_priority"] / total * 100),
        needs_reply=needs_reply,
        draft_count=draft_count,
        unread_count=unread_count,
        attachment_count=attachment_count,
        escalated_count=escalated_count,
        hot_tone_count=hot_tone_count,
        recurring_topics=recurring_topics,
        alerts=alerts,
        topic_clusters=topic_clusters,
        customer_cards=customer_cards,
        customer_total=customer_total,
        internal_count=internal_count,
        internal_urgent=internal_urgent,
        internal_action=internal_action,
        internal_avg_severity=internal_avg_severity,
        triaged=triaged,
        executive_summary=executive_summary,
        data_json=json.dumps(triaged, default=str),
    )
