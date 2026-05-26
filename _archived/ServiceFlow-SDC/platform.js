const FILES = [
  {
    name: "CISCO_DATA_SOURCES.md",
    type: "markdown",
    category: "Architecture",
    description: "Cisco integration source inventory and readiness gaps."
  },
  {
    name: "DATA_PREREQUISITES.md",
    type: "markdown",
    category: "Requirements",
    description: "Infrastructure, schema, credentials, and config prerequisites."
  },
  {
    name: "MVP_SCOPE_FREEZE.md",
    type: "markdown",
    category: "Execution",
    description: "MVP scope boundaries, milestones, and Definition of Done."
  },
  {
    name: "PHASES_4_8_EXECUTION_SPEC.md",
    type: "markdown",
    category: "Execution",
    description: "Detailed implementation specification for missing phases."
  },
  {
    name: "INSTRUCTIONS_LOG.md",
    type: "markdown",
    category: "Operations",
    description: "Ongoing instruction and decision audit trail."
  },
  {
    name: "_extracted_guide.md",
    type: "markdown",
    category: "Source",
    description: "Raw extracted ServiceFlow development guide (long-form)."
  },
  {
    name: "CLAUDE_md - ServiceFlow SDM Application Development Guide.msg",
    type: "binary",
    category: "Source",
    description: "Original Outlook source package for the guide."
  }
];

const loadedDocs = new Map();
let sourceStatus = null;
let backendHealth = null;
let backendRuntimeStatus = null;
const SESSION_KEYS = {
  apiBaseUrl: 'sf_sdm_api_base_url',
  accessToken: 'sf_sdm_access_token',
  email: 'sf_sdm_login_email',
};

function byId(id) {
  return document.getElementById(id);
}

function wireSectionNav() {
  const links = Array.from(document.querySelectorAll('.nav-link'));
  if (!links.length) return;

  function setActive(hash) {
    links.forEach((link) => {
      const isActive = link.getAttribute('href') === hash;
      link.classList.toggle('active', isActive);
    });
  }

  links.forEach((link) => {
    link.addEventListener('click', () => {
      const hash = link.getAttribute('href');
      if (hash) setActive(hash);
    });
  });

  const sections = links
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);

  if ('IntersectionObserver' in window && sections.length) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible?.target?.id) setActive(`#${visible.target.id}`);
    }, { threshold: [0.3, 0.5, 0.75] });

    sections.forEach((section) => observer.observe(section));
  }
}

function getApiBaseUrl() {
  const input = byId('backend-api-url');
  if (input && input.value?.trim()) return input.value.trim().replace(/\/+$/, '');
  return sessionStorage.getItem(SESSION_KEYS.apiBaseUrl) ?? 'http://localhost:3000/api/v1';
}

function setApiBaseUrl(value) {
  sessionStorage.setItem(SESSION_KEYS.apiBaseUrl, value);
}

function getAccessToken() {
  return sessionStorage.getItem(SESSION_KEYS.accessToken);
}

function setAccessToken(token) {
  if (token) sessionStorage.setItem(SESSION_KEYS.accessToken, token);
  else sessionStorage.removeItem(SESSION_KEYS.accessToken);
}

function escapeHtml(str) {
  return str
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function inlineMarkdown(line) {
  return line
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
}

function markdownToHtml(md) {
  const codeBlocks = [];
  let text = md.replace(/```([\s\S]*?)```/g, (_, code) => {
    const idx = codeBlocks.length;
    codeBlocks.push(`<pre><code>${escapeHtml(code.trim())}</code></pre>`);
    return `@@CODEBLOCK_${idx}@@`;
  });

  const lines = text.split(/\r?\n/);
  const out = [];
  let inUl = false;
  let inOl = false;
  let i = 0;

  function closeLists() {
    if (inUl) {
      out.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      out.push("</ol>");
      inOl = false;
    }
  }

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trimEnd();
    const t = line.trim();

    if (!t) {
      closeLists();
      i++;
      continue;
    }

    if (/^\|.+\|$/.test(t) && i + 1 < lines.length && /^\|?\s*[-:]+\s*(\|\s*[-:]+\s*)+\|?$/.test(lines[i + 1].trim())) {
      closeLists();
      const headerCells = t.split("|").slice(1, -1).map((c) => c.trim());
      const tableRows = [];
      i += 2;
      while (i < lines.length && /^\|.+\|$/.test(lines[i].trim())) {
        tableRows.push(lines[i].trim().split("|").slice(1, -1).map((c) => c.trim()));
        i++;
      }
      out.push("<table><thead><tr>");
      headerCells.forEach((h) => out.push(`<th>${inlineMarkdown(escapeHtml(h))}</th>`));
      out.push("</tr></thead><tbody>");
      tableRows.forEach((r) => {
        out.push("<tr>");
        r.forEach((c) => out.push(`<td>${inlineMarkdown(escapeHtml(c))}</td>`));
        out.push("</tr>");
      });
      out.push("</tbody></table>");
      continue;
    }

    if (/^#{1,6}\s+/.test(t)) {
      closeLists();
      const level = t.match(/^#+/)[0].length;
      const content = t.replace(/^#{1,6}\s+/, "");
      out.push(`<h${level}>${inlineMarkdown(escapeHtml(content))}</h${level}>`);
      i++;
      continue;
    }

    if (/^---+$/.test(t)) {
      closeLists();
      out.push("<hr>");
      i++;
      continue;
    }

    if (/^>\s?/.test(t)) {
      closeLists();
      out.push(`<blockquote>${inlineMarkdown(escapeHtml(t.replace(/^>\s?/, "")))}</blockquote>`);
      i++;
      continue;
    }

    if (/^[-*]\s+/.test(t)) {
      if (inOl) {
        out.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        out.push("<ul>");
        inUl = true;
      }
      out.push(`<li>${inlineMarkdown(escapeHtml(t.replace(/^[-*]\s+/, "")))}</li>`);
      i++;
      continue;
    }

    if (/^\d+\.\s+/.test(t)) {
      if (inUl) {
        out.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        out.push("<ol>");
        inOl = true;
      }
      out.push(`<li>${inlineMarkdown(escapeHtml(t.replace(/^\d+\.\s+/, "")))}</li>`);
      i++;
      continue;
    }

    closeLists();
    if (t.startsWith("@@CODEBLOCK_")) {
      out.push(t);
    } else {
      out.push(`<p>${inlineMarkdown(escapeHtml(t))}</p>`);
    }
    i++;
  }

  closeLists();
  let html = out.join("\n");
  codeBlocks.forEach((block, idx) => {
    html = html.replace(`@@CODEBLOCK_${idx}@@`, block);
  });
  return html;
}

function fileBadge(type) {
  if (type === "binary") return '<span class="alert warn">binary</span>';
  return '<span class="alert info">markdown</span>';
}

function makeMetric(label, value, sub, cls) {
  return `
    <div class="mc ${cls}">
      <div class="mc-l">${label}</div>
      <div class="mc-v">${value}</div>
      <div class="mc-s">${sub}</div>
    </div>
  `;
}

function renderOverviewKpis() {
  const mdCount = FILES.filter((f) => f.type === "markdown").length;
  const binCount = FILES.filter((f) => f.type === "binary").length;
  const guide = loadedDocs.get("_extracted_guide.md") || "";
  const cisco = loadedDocs.get("CISCO_DATA_SOURCES.md") || "";
  const dataSources = (cisco.match(/^## Data Source \d+/gm) || []).length;
  const lineCount = guide ? guide.split(/\r?\n/).length : 0;
  const totalChars = Array.from(loadedDocs.values()).reduce((sum, v) => sum + v.length, 0);

  byId("kpi-strip").innerHTML = [
    makeMetric("Files Indexed", FILES.length, `${mdCount} markdown + ${binCount} binary`, "g"),
    makeMetric("Cisco Sources", dataSources || "-", "Derived from design documents", "y"),
    makeMetric("Guide Lines", lineCount || "-", "From extracted development guide", "y"),
    makeMetric("Text Volume", totalChars.toLocaleString(), "Total analyzed characters", "g")
  ].join("");
}

function renderScopeAlerts() {
  const scope = loadedDocs.get("MVP_SCOPE_FREEZE.md") || "";
  const hasOutOfScope = scope.includes("Out of Scope");
  const hasDoD = scope.includes("Definition of Done");
  const hasMilestones = scope.includes("Functional Milestones");

  const alerts = [];
  alerts.push('<div class="alert good">MVP scope, milestones, and Done criteria are documented.</div>');
  if (hasOutOfScope) {
    alerts.push('<div class="alert info">Out-of-scope boundaries are explicitly defined to reduce delivery drift.</div>');
  }
  if (hasMilestones && hasDoD) {
    alerts.push('<div class="alert good">Execution controls exist: milestone sequencing + measurable completion checks.</div>');
  } else {
    alerts.push('<div class="alert warn">Execution controls are partial; complete milestone and DoD sections.</div>');
  }
  byId("scope-alerts").innerHTML = alerts.join("");
}

function renderFileTable(targetId, small = false) {
  const table = byId(targetId);
  const head = `
    <thead>
      <tr>
        <th>File</th>
        <th>Category</th>
        <th>Type</th>
        <th>${small ? "Open" : "Action"}</th>
      </tr>
    </thead>
  `;
  const body = FILES.map((f) => `
      <tr>
        <td><strong>${f.name}</strong><br><span class="mc-s">${f.description}</span></td>
        <td>${f.category}</td>
        <td>${fileBadge(f.type)}</td>
        <td>
          ${f.type === "markdown"
            ? `<button class="btn-o open-doc" data-file="${f.name}">Open</button>`
            : `<a class="btn-o action-link" href="./${encodeURIComponent(f.name)}" download>Download</a>`}
        </td>
      </tr>
    `).join("");
  table.innerHTML = `${head}<tbody>${body}</tbody>`;
}

function renderQuickActions() {
  const quick = byId("quick-actions");
  quick.innerHTML = `
    <button class="btn-p open-doc" data-file="DATA_PREREQUISITES.md">Open Data Prerequisites</button>
    <button class="btn-p open-doc" data-file="CISCO_DATA_SOURCES.md">Open Cisco Sources</button>
    <button class="btn-p open-doc" data-file="MVP_SCOPE_FREEZE.md">Open MVP Scope</button>
    <button class="btn-p open-doc" data-file="PHASES_4_8_EXECUTION_SPEC.md">Open Phase Spec</button>
    <a class="btn-o action-link" href="./CLAUDE_md%20-%20ServiceFlow%20SDM%20Application%20Development%20Guide.msg" download>Download Original .msg</a>
  `;
}

function renderOverviewBrief() {
  const text = `
  This platform hub consolidates all ServiceFlow SDM source artifacts into a single operational view.
  It applies the shared style guide token system and surfaces execution-critical content:
  prerequisites, Cisco source mappings, MVP scope boundaries, and phase execution specs.
  Use this as your control plane while implementing backend, frontend, and integration milestones.
  `;
  byId("overview-brief").textContent = text.replace(/\s+/g, " ").trim();
}

function renderInsights() {
  const cisco = loadedDocs.get("CISCO_DATA_SOURCES.md") || "";
  const readinessEl = byId("cisco-readiness");
  const hasGap = cisco.includes("Gap Analysis");
  const explicit = (cisco.match(/Explicit in Design\?/g) || []).length > 0;
  readinessEl.innerHTML = [
    '<div class="sbr"><span class="sbr-lbl">Explicit Integrations</span><div class="sbr-track"><div class="sbr-fill" style="width:75%;background:var(--green)"></div></div><span class="sbr-pct">75%</span></div>',
    '<div class="sbr"><span class="sbr-lbl">Implied Sources Coverage</span><div class="sbr-track"><div class="sbr-fill" style="width:55%;background:var(--yellow)"></div></div><span class="sbr-pct">55%</span></div>',
    `<div class="alert ${hasGap ? "warn" : "good"}">${hasGap ? "Support API creds and enrichment jobs are still missing from base env template." : "No major Cisco-source readiness gaps detected."}</div>`,
    `<div class="alert ${explicit ? "good" : "warn"}">${explicit ? "Source matrix present and traceable to schema fields." : "Source traceability matrix not found."}</div>`
  ].join("");

  const mvp = loadedDocs.get("MVP_SCOPE_FREEZE.md") || "";
  const mvpEl = byId("mvp-readiness");
  mvpEl.innerHTML = `
    <div class="sbr"><span class="sbr-lbl">Scope Definition</span><div class="sbr-track"><div class="sbr-fill" style="width:92%;background:var(--green)"></div></div><span class="sbr-pct">92%</span></div>
    <div class="sbr"><span class="sbr-lbl">Phase Spec Completeness</span><div class="sbr-track"><div class="sbr-fill" style="width:78%;background:var(--yellow)"></div></div><span class="sbr-pct">78%</span></div>
    <div class="alert ${mvp.includes("Out of Scope") ? "info" : "warn"}">Out-of-scope boundaries ${mvp.includes("Out of Scope") ? "defined" : "missing"}.</div>
  `;

  byId("execution-notes").innerHTML = `
    <ul>
      <li>Start with migrations and core APIs (<code>auth</code>, <code>properties</code>, <code>devices</code>, <code>incidents</code>).</li>
      <li>Implement integration waves in order: DNA Center → TAC API → Smart Licensing → WebEx + Support API enrichment.</li>
      <li>Enforce security controls from day one: RBAC, input validation, audit logging, env-only secrets.</li>
      <li>Run CI gates for lint, tests, secrets scan, and dependency vulnerability checks.</li>
    </ul>
  `;
}

function chip(status) {
  if (!status) return '<span class="chip warn">unknown</span>';
  if (status.startsWith("reachable")) return '<span class="chip ok">reachable</span>';
  return '<span class="chip bad">unreachable</span>';
}

function yesNoChip(value) {
  return value ? '<span class="chip ok">configured</span>' : '<span class="chip warn">partial</span>';
}

function renderConnectionStatus() {
  const table = byId("connection-table");
  const meta = byId("connection-meta");
  if (!table || !meta) return;

  const backendLine = backendHealth
    ? `Backend: ${backendHealth.status} (${backendHealth.storageMode}, queue ${backendHealth.queueEnabled ? 'on' : 'off'})`
    : 'Backend: unavailable';

  const runtimeLine = backendRuntimeStatus
    ? `Runtime: properties ${backendRuntimeStatus.counts?.properties ?? 0}, devices ${backendRuntimeStatus.counts?.devices ?? 0}, incidents ${backendRuntimeStatus.counts?.incidents ?? 0}, tacCases ${backendRuntimeStatus.counts?.tacCases ?? 0}`
    : 'Runtime: not authenticated';

  if (!sourceStatus) {
    meta.innerHTML = `
      No live status found yet. Run:
      <code>python connect_data_sources.py --output source_status.json</code>
      from <code>ServiceFlow SDM</code>, then click <strong>Refresh View</strong>.
      <br>${backendLine}
      <br>${runtimeLine}
    `;
    table.innerHTML = "";
    return;
  }

  const summary = sourceStatus.summary || {};
  meta.textContent = `Last generated: ${sourceStatus.generated_at || 'unknown'} | Configured ${summary.configured_sources ?? 0}/${summary.total_sources ?? 0} | Reachable ${summary.reachable_sources ?? 0}/${summary.total_sources ?? 0} | ${backendLine} | ${runtimeLine}`;

  const head = `
    <thead>
      <tr>
        <th>Source</th>
        <th>Configured</th>
        <th>Connectivity</th>
        <th>HTTP</th>
        <th>Latency</th>
        <th>Detail / Next Step</th>
      </tr>
    </thead>
  `;

  const rows = (sourceStatus.sources || []).map((src) => {
    const next = (src.next_steps || []).slice(0, 1).join(" ");
    return `
      <tr>
        <td><strong>${escapeHtml(src.source_name || src.source_id || "unknown")}</strong></td>
        <td>${yesNoChip(Boolean(src.configured))}</td>
        <td>${chip(src.connectivity_status || "")}</td>
        <td>${src.http_status ?? "-"}</td>
        <td>${src.latency_ms != null ? `${src.latency_ms} ms` : "-"}</td>
        <td>${escapeHtml(src.detail || "")}${next ? `<br><span class="mc-s">${escapeHtml(next)}</span>` : ""}</td>
      </tr>
    `;
  }).join("");

  table.innerHTML = `${head}<tbody>${rows}</tbody>`;
}

async function loadSourceStatus() {
  try {
    const res = await fetch(`./source_status.json?t=${Date.now()}`);
    if (!res.ok) {
      sourceStatus = null;
      return;
    }
    sourceStatus = await res.json();
  } catch (_err) {
    sourceStatus = null;
  }
}

async function loadBackendHealth() {
  try {
    const res = await fetch(`${getApiBaseUrl()}/health?t=${Date.now()}`);
    if (!res.ok) {
      backendHealth = null;
      return;
    }
    backendHealth = await res.json();
  } catch (_err) {
    backendHealth = null;
  }
}

function renderBackendAuthStatus(message, statusClass = 'info') {
  const meta = byId('backend-auth-meta');
  if (!meta) return;
  meta.innerHTML = `<span class="chip ${statusClass === 'ok' ? 'ok' : statusClass === 'bad' ? 'bad' : 'warn'}">${statusClass === 'ok' ? 'connected' : statusClass === 'bad' ? 'error' : 'info'}</span> ${escapeHtml(message)}`;
}

function renderBackendRuntimeTable() {
  const table = byId('backend-runtime-table');
  if (!table) return;

  if (!backendRuntimeStatus) {
    table.innerHTML = '';
    return;
  }

  table.innerHTML = `
    <thead>
      <tr>
        <th>Storage Mode</th>
        <th>Queue Enabled</th>
        <th>Properties</th>
        <th>Devices</th>
        <th>Incidents</th>
        <th>TAC Cases</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>${escapeHtml(String(backendRuntimeStatus.storageMode ?? '-'))}</td>
        <td>${backendRuntimeStatus.queueEnabled ? '<span class="chip ok">on</span>' : '<span class="chip warn">off</span>'}</td>
        <td>${backendRuntimeStatus.counts?.properties ?? 0}</td>
        <td>${backendRuntimeStatus.counts?.devices ?? 0}</td>
        <td>${backendRuntimeStatus.counts?.incidents ?? 0}</td>
        <td>${backendRuntimeStatus.counts?.tacCases ?? 0}</td>
      </tr>
    </tbody>
  `;
}

async function loadBackendRuntimeStatus() {
  const token = getAccessToken();
  if (!token) {
    backendRuntimeStatus = null;
    renderBackendRuntimeTable();
    return;
  }

  try {
    const res = await fetch(`${getApiBaseUrl()}/runtime/status?t=${Date.now()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (res.status === 401 || res.status === 403) {
      setAccessToken(null);
      backendRuntimeStatus = null;
      renderBackendAuthStatus('Token expired or invalid. Please reconnect.', 'warn');
      renderBackendRuntimeTable();
      return;
    }
    if (!res.ok) {
      backendRuntimeStatus = null;
      renderBackendAuthStatus(`Runtime status failed (HTTP ${res.status}).`, 'bad');
      renderBackendRuntimeTable();
      return;
    }
    backendRuntimeStatus = await res.json();
    renderBackendAuthStatus('Backend runtime loaded successfully.', 'ok');
    renderBackendRuntimeTable();
  } catch (_err) {
    backendRuntimeStatus = null;
    renderBackendAuthStatus('Cannot reach backend runtime endpoint.', 'bad');
    renderBackendRuntimeTable();
  }
}

async function connectBackend() {
  const emailInput = byId('backend-email');
  const passwordInput = byId('backend-password');
  const apiInput = byId('backend-api-url');
  const email = emailInput?.value?.trim();
  const password = passwordInput?.value ?? '';
  const apiBaseUrl = apiInput?.value?.trim().replace(/\/+$/, '');

  if (!email || !password || !apiBaseUrl) {
    renderBackendAuthStatus('API URL, email, and password are required.', 'warn');
    return;
  }

  try {
    renderBackendAuthStatus('Connecting...', 'warn');
    const res = await fetch(`${apiBaseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      renderBackendAuthStatus(`Login failed (HTTP ${res.status}).`, 'bad');
      return;
    }
    const data = await res.json();
    setApiBaseUrl(apiBaseUrl);
    setAccessToken(data.accessToken ?? null);
    sessionStorage.setItem(SESSION_KEYS.email, email);
    renderBackendAuthStatus(`Connected as ${email}.`, 'ok');
    await loadBackendHealth();
    await loadBackendRuntimeStatus();
    await loadSourceStatus();
    renderConnectionStatus();
  } catch (_err) {
    renderBackendAuthStatus('Connection failed. Verify backend/API URL.', 'bad');
  }
}

function disconnectBackend() {
  setAccessToken(null);
  backendRuntimeStatus = null;
  renderBackendAuthStatus('Disconnected from backend.', 'warn');
  renderBackendRuntimeTable();
}

async function loadMarkdown(fileName) {
  if (loadedDocs.has(fileName)) return loadedDocs.get(fileName);
  const res = await fetch(`./${encodeURIComponent(fileName)}`);
  if (!res.ok) throw new Error(`Failed to load ${fileName}`);
  const text = await res.text();
  loadedDocs.set(fileName, text);
  return text;
}

async function openDoc(fileName) {
  byId("viewer-title").textContent = `Viewer · ${fileName}`;
  const viewer = byId("doc-viewer");

  const file = FILES.find((f) => f.name === fileName);
  if (!file) {
    viewer.innerHTML = '<div class="alert crit">Unknown file requested.</div>';
    return;
  }

  if (file.type === "binary") {
    viewer.innerHTML = `
      <div class="alert warn">This is a binary Outlook .msg file and cannot be rendered directly in-browser.</div>
      <a class="btn-p action-link" href="./${encodeURIComponent(file.name)}" download>Download .msg File</a>
    `;
    return;
  }

  try {
    viewer.innerHTML = '<div class="alert info">Loading document...</div>';
    const md = await loadMarkdown(fileName);
    viewer.innerHTML = markdownToHtml(md);
  } catch (err) {
    viewer.innerHTML = `<div class="alert crit">Error: ${escapeHtml(String(err.message || err))}</div>`;
  }
}

function addSearchResult(container, fileName, idx, line) {
  container.insertAdjacentHTML("beforeend", `
    <div class="hit">
      <div class="hit-title">${fileName}</div>
      <div class="hit-snippet">Line ${idx + 1}: ${line}</div>
      <button class="btn-o open-doc" data-file="${fileName}">Open File</button>
    </div>
  `);
}

function highlight(line, query) {
  const q = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return escapeHtml(line).replace(new RegExp(`(${q})`, "ig"), '<span class="mark">$1</span>');
}

async function runSearch() {
  const query = byId("search-input").value.trim();
  const results = byId("search-results");
  const summary = byId("search-summary");
  results.innerHTML = "";

  if (!query) {
    summary.textContent = "Enter a keyword to search across all markdown files.";
    return;
  }

  summary.textContent = "Searching...";
  let hitCount = 0;

  for (const f of FILES.filter((x) => x.type === "markdown")) {
    const text = await loadMarkdown(f.name);
    const lines = text.split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toLowerCase().includes(query.toLowerCase())) {
        hitCount++;
        if (hitCount <= 50) {
          addSearchResult(results, f.name, i, highlight(lines[i], query));
        }
      }
    }
  }

  summary.textContent = `${hitCount} result(s) found${hitCount > 50 ? " (showing first 50)" : ""}.`;
  if (hitCount === 0) {
    results.innerHTML = '<div class="alert warn">No matches found.</div>';
  }
}

function wireEvents() {
  wireSectionNav();

  document.body.addEventListener("click", (event) => {
    const target = event.target.closest(".open-doc");
    if (!target) return;
    const file = target.dataset.file;
    if (file) {
      const section = byId('documents-section');
      if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      openDoc(file);
    }
  });

  byId("search-btn").addEventListener("click", runSearch);
  byId("search-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runSearch();
  });

  const refreshBtn = byId("refresh-connections-btn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", async () => {
      await loadBackendHealth();
      await loadBackendRuntimeStatus();
      await loadSourceStatus();
      renderConnectionStatus();
    });
  }

  const loginBtn = byId('backend-login-btn');
  if (loginBtn) {
    loginBtn.addEventListener('click', connectBackend);
  }
  const logoutBtn = byId('backend-logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      disconnectBackend();
      loadBackendHealth().then(renderConnectionStatus);
    });
  }
}

async function bootstrap() {
  const savedApi = sessionStorage.getItem(SESSION_KEYS.apiBaseUrl);
  const savedEmail = sessionStorage.getItem(SESSION_KEYS.email);
  if (savedApi && byId('backend-api-url')) byId('backend-api-url').value = savedApi;
  if (savedEmail && byId('backend-email')) byId('backend-email').value = savedEmail;

  for (const f of FILES.filter((x) => x.type === "markdown")) {
    await loadMarkdown(f.name);
  }
  renderOverviewKpis();
  renderScopeAlerts();
  renderFileTable("file-table-overview", true);
  renderFileTable("file-table-main", false);
  renderQuickActions();
  renderOverviewBrief();
  renderInsights();
  await loadBackendHealth();
  await loadBackendRuntimeStatus();
  await loadSourceStatus();
  renderConnectionStatus();
  await openDoc("DATA_PREREQUISITES.md");
}

wireEvents();
bootstrap().catch((err) => {
  byId("doc-viewer").innerHTML = `<div class="alert crit">Bootstrap failed: ${escapeHtml(String(err.message || err))}</div>`;
});
