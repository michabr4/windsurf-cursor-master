/* AI Factory Framework — Application Logic */

function aiFactory() {
  return {
    /* Data sources */
    framework: FRAMEWORK,
    roles: CX_ROLES,
    assessmentQuestions: ASSESSMENT_QUESTIONS,

    /* UI state */
    mobileNav: false,
    selectedRole: null,
    expandedRole: null,
    activeLifecycleStage: 0,
    activeMaturityLevel: 1,

    /* Assessment state */
    assessmentAnswers: {},
    assessmentComplete: false,
    assessmentResult: { level: 1, name: '', description: '', score: 0 },

    init() {
      this.$nextTick(() => {
        if (typeof lucide !== 'undefined') {
          lucide.createIcons();
        }
      });

      /* Re-render icons when Alpine updates the DOM */
      this.$watch('expandedRole', () => {
        this.$nextTick(() => { if (typeof lucide !== 'undefined') lucide.createIcons(); });
      });
      this.$watch('selectedRole', () => {
        this.$nextTick(() => { if (typeof lucide !== 'undefined') lucide.createIcons(); });
      });
      this.$watch('activeLifecycleStage', () => {
        this.$nextTick(() => { if (typeof lucide !== 'undefined') lucide.createIcons(); });
      });
      this.$watch('activeMaturityLevel', () => {
        this.$nextTick(() => { if (typeof lucide !== 'undefined') lucide.createIcons(); });
      });
      this.$watch('assessmentComplete', () => {
        this.$nextTick(() => { if (typeof lucide !== 'undefined') lucide.createIcons(); });
      });

      /* Section reveal on scroll */
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      }, { threshold: 0.1 });

      document.querySelectorAll('.section-reveal').forEach(el => {
        observer.observe(el);
      });
    },

    /* Computed: filter roles based on selection */
    get filteredRoles() {
      if (this.selectedRole === null) return this.roles;
      return this.roles.filter(r => r.id === this.selectedRole);
    },

    /* Toggle role card expansion */
    toggleRole(roleId) {
      this.expandedRole = this.expandedRole === roleId ? null : roleId;
    },

    /* Role color utility */
    getRoleColorClasses(color) {
      const map = {
        blue: 'bg-blue-100 text-blue-600',
        indigo: 'bg-indigo-100 text-indigo-600',
        violet: 'bg-violet-100 text-violet-600',
        sky: 'bg-sky-100 text-sky-600',
        emerald: 'bg-emerald-100 text-emerald-600',
        amber: 'bg-amber-100 text-amber-600',
        teal: 'bg-teal-100 text-teal-600',
        red: 'bg-red-100 text-red-600',
        orange: 'bg-orange-100 text-orange-600',
        yellow: 'bg-yellow-100 text-yellow-600',
      };
      return map[color] || 'bg-slate-100 text-slate-600';
    },

    /* Assessment calculation */
    calculateAssessment() {
      const values = Object.values(this.assessmentAnswers);
      const avg = values.reduce((sum, v) => sum + v, 0) / values.length;
      
      let level, name, description;
      if (avg <= 1.5) {
        level = 1;
        name = 'Manual';
        description = 'Your team operates primarily through manual processes. This is a great starting point — the biggest gains are ahead of you.';
      } else if (avg <= 2.5) {
        level = 2;
        name = 'Assisted';
        description = 'Your team is experimenting with AI tools. Now it\'s time to move from ad-hoc usage to structured agent design.';
      } else if (avg <= 3.5) {
        level = 3;
        name = 'Augmented';
        description = 'Your team has active agent workflows with human oversight. Focus on expanding coverage and measuring impact.';
      } else {
        level = 4;
        name = 'Autonomous';
        description = 'Your team is operating as a mature AI Factory. Focus on governance, scaling, and continuous optimization.';
      }

      this.assessmentResult = { level, name, description, score: avg };
      this.assessmentComplete = true;
    },

    /* Recommendations based on maturity level */
    getRecommendations() {
      const recs = {
        1: [
          { title: 'Start with Observation', desc: 'Document your top 5 most repetitive, time-consuming tasks this week. These are your first agent candidates.' },
          { title: 'Pick One Process', desc: 'Choose the simplest, lowest-risk task and explore how an AI tool (ChatGPT, Copilot) could assist. Don\'t automate — just assist.' },
          { title: 'Measure Your Baseline', desc: 'Start tracking cycle time on 2-3 key workflows. You need a "before" to prove the "after".' },
          { title: 'Build Awareness', desc: 'Share the AI Factory Framework with your team. Start the conversation about what\'s possible.' }
        ],
        2: [
          { title: 'Formalize Your Experiments', desc: 'Move from ad-hoc AI tool usage to structured pilots. Define what the agent does, what humans review, and what success looks like.' },
          { title: 'Design Your First Agent', desc: 'Pick one pain point from the Role Explorer and design a purpose-built agent with clear inputs, logic, and outputs.' },
          { title: 'Establish HITL Patterns', desc: 'Create human-in-the-loop approval workflows — draft-first, human-approved outputs before any customer-facing action.' },
          { title: 'Track and Share Results', desc: 'Measure cycle-time improvements and share wins with leadership. Evidence drives investment.' }
        ],
        3: [
          { title: 'Chain Your Agents', desc: 'Connect individual agents into multi-step workflows. Your Case Lifecycle Chain is a great model.' },
          { title: 'Build Governance', desc: 'Formalize approval gates, audit trails, and escalation paths. Governance enables trust, which enables scale.' },
          { title: 'Expand Coverage', desc: 'Apply proven agent patterns to adjacent roles and workflows. What works for one team can work for many.' },
          { title: 'Invest in Dashboards', desc: 'Build real-time performance dashboards that track agent impact. Make the ROI visible to everyone.' }
        ],
        4: [
          { title: 'Optimize the Portfolio', desc: 'Use agent performance data to prioritize investments. Double down on what works, sunset what doesn\'t.' },
          { title: 'Scale Across the Org', desc: 'Package your best agents as templates and deploy across geographies and business units.' },
          { title: 'Pioneer New Patterns', desc: 'Explore agent-of-agents orchestration. Your team is ready to design systems, not just individual agents.' },
          { title: 'Share the Playbook', desc: 'Your AI Factory is a model for others. Document and share your journey to drive organizational transformation.' }
        ]
      };

      const items = recs[this.assessmentResult.level] || recs[1];
      return items.map((r, i) => 
        `<div class="flex items-start gap-3 p-3 bg-white rounded-xl border border-slate-200">
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold flex-shrink-0">${i + 1}</div>
          <div>
            <div class="font-semibold text-slate-800">${r.title}</div>
            <div class="text-sm text-slate-500 mt-1">${r.desc}</div>
          </div>
        </div>`
      ).join('');
    },

    /* Reset assessment */
    resetAssessment() {
      this.assessmentAnswers = {};
      this.assessmentComplete = false;
      this.assessmentResult = { level: 1, name: '', description: '', score: 0 };
    }
  };
}
