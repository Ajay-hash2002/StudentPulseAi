import { api } from '../api.js';
import { auth } from '../auth.js';

export async function renderDashboard(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Analyzing profile evidence and calculating readiness...</p>
    </div>
  `;

  try {
    const student = auth.getStudent();
    const goals = await api.get('/career-goals');
    const activeGoal = goals && goals.length > 0 ? goals[0] : null;
    const targetRole = activeGoal?.target_role || "Backend Developer";

    // Fetch readiness and skill gaps
    const readiness = await api.post('/analysis/readiness', { target_role: targetRole });
    const gapsData = await api.post('/analysis/skill-gaps', { target_role: targetRole });
    const evidenceList = await api.get('/students/me/evidence');
    const assessments = await api.get('/assessments');

    const score = readiness.readiness_score || 0;
    const coverage = readiness.evidence_coverage_pct || 0;
    const level = readiness.readiness_level || "Foundation";

    // Determine gauge color
    let scoreColor = '#2563eb';
    if (score >= 75) scoreColor = '#10b981';
    else if (score >= 50) scoreColor = '#f59e0b';
    else if (score > 0) scoreColor = '#3b82f6';
    else scoreColor = '#94a3b8';

    container.innerHTML = `
      <!-- Welcome Header -->
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; flex-wrap: wrap; gap: 16px;">
        <div>
          <h2 style="font-size: 1.6rem; font-weight: 800; color: var(--secondary);">
            Welcome back, ${escapeHtml(student?.display_name || 'Student')}! 👋
          </h2>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 4px;">
            Target Career Goal: <strong style="color: var(--primary);">${escapeHtml(targetRole)}</strong> • 
            Status: <span class="badge ${score >= 60 ? 'badge-strong' : 'badge-weak'}">${escapeHtml(level)}</span>
          </p>
        </div>
        <div style="display: flex; gap: 10px;">
          <a href="#action-plan" class="btn btn-primary">
            ⚡ View Action Plan
          </a>
          <button id="btn-calc-modal" class="btn btn-outline">
            ℹ️ How is this calculated?
          </button>
        </div>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="grid-4" style="margin-bottom: 24px;">
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">🎯</div>
          <div>
            <div class="stat-val">${score}%</div>
            <div class="stat-label">Readiness Score</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--info-bg); color: #0891b2;">📊</div>
          <div>
            <div class="stat-val">${coverage}%</div>
            <div class="stat-label">Evidence Coverage</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--success-bg); color: #059669;">💡</div>
          <div>
            <div class="stat-val">${evidenceList?.length || 0}</div>
            <div class="stat-label">Skills Verified</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: #fdf2f8; color: #db2777;">📝</div>
          <div>
            <div class="stat-val">${assessments?.length || 0}</div>
            <div class="stat-label">Assessments Taken</div>
          </div>
        </div>
      </div>

      <!-- Main Readiness & Breakdown Row -->
      <div class="grid-2">
        <!-- Readiness Gauge Card -->
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Career Readiness Benchmark</div>
              <div class="card-subtitle">Evidence-backed calculation for ${escapeHtml(targetRole)}</div>
            </div>
            <span class="badge badge-low">Deterministic Rule Engine</span>
          </div>

          <div class="readiness-gauge-box" style="margin: 20px 0;">
            <div class="gauge-circle" style="border-color: ${scoreColor};">
              <div class="gauge-score" style="color: ${scoreColor};">${score}%</div>
              <div class="gauge-label">${escapeHtml(level)}</div>
            </div>
            <div style="flex: 1;">
              <p style="font-size: 0.88rem; color: var(--text-main); margin-bottom: 12px; line-height: 1.4;">
                ${score === 0 
                  ? 'Your profile is currently in the <strong>baseline stage</strong>. Submit your assessments or projects to activate your evidence-backed readiness calculations.'
                  : `Your evidence indicates <strong>${escapeHtml(level)}</strong> towards standard industry requirements for ${escapeHtml(targetRole)}.`
                }
              </p>
              <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; align-items: center; gap: 8px;">
                <span>Verified Evidence: ${gapsData.strong_count} strong • ${gapsData.weak_count} developing • ${gapsData.missing_count} missing</span>
              </div>
            </div>
          </div>

          <!-- Criteria Progress Bars -->
          <div style="margin-top: 18px; border-top: 1px solid var(--border-color); padding-top: 16px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-muted); margin-bottom: 10px; text-transform: uppercase;">
              Readiness Criteria Breakdown
            </div>
            ${readiness.criteria_breakdown.map(crit => `
              <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600;">
                  <span>${escapeHtml(crit.criterion)}</span>
                  <span>${crit.achieved_score} / ${crit.max_possible} pts</span>
                </div>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill" style="width: ${(crit.achieved_score / crit.max_possible) * 100}%;"></div>
                </div>
                <div style="font-size: 0.74rem; color: var(--text-muted);">${escapeHtml(crit.description)}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Strengths & Priority Gaps Card -->
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Key Strengths & Critical Gaps</div>
              <div class="card-subtitle">Transparent comparison against ${escapeHtml(targetRole)} requirements</div>
            </div>
            <a href="#skill-gaps" class="btn btn-outline btn-sm">Full Gap Matrix →</a>
          </div>

          <!-- Strengths -->
          <div style="margin-bottom: 20px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #059669; text-transform: uppercase; margin-bottom: 8px;">
              ✅ Demonstrated Strengths (${readiness.strengths?.length || 0})
            </div>
            ${readiness.strengths && readiness.strengths.length > 0 ? `
              <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${readiness.strengths.map(s => `
                  <span class="badge badge-strong" style="padding: 6px 12px; font-size: 0.82rem;">${escapeHtml(s)}</span>
                `).join('')}
              </div>
            ` : `
              <div style="font-size: 0.84rem; color: var(--text-muted); font-style: italic;">
                No strong role proficiencies recorded yet. Complete assessments or add projects to demonstrate capability.
              </div>
            `}
          </div>

          <!-- Critical Gaps -->
          <div>
            <div style="font-size: 0.82rem; font-weight: 700; color: #b45309; text-transform: uppercase; margin-bottom: 8px;">
              ⚠️ Priority Development Gaps (${readiness.critical_gaps?.length || 0})
            </div>
            ${readiness.critical_gaps && readiness.critical_gaps.length > 0 ? `
              <div style="display: flex; flex-direction: column; gap: 8px;">
                ${readiness.critical_gaps.map(g => `
                  <div style="padding: 10px 14px; background: #fffbeb; border: 1px solid var(--warning-border); border-radius: var(--radius-sm); font-size: 0.84rem; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; color: #78350f;">${escapeHtml(g)}</span>
                    <a href="#action-plan" class="btn btn-outline btn-sm" style="padding: 3px 8px; font-size: 0.72rem;">Target Practice</a>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div style="font-size: 0.84rem; color: var(--text-muted); font-style: italic;">
                No critical gaps detected!
              </div>
            `}
          </div>

          <!-- Guidance Disclaimer Banner -->
          <div class="alert-box alert-info" style="margin-top: 24px; font-size: 0.78rem;">
            <span>ℹ️ <strong>Guidance Only:</strong> ${escapeHtml(readiness.limitations)}</span>
          </div>
        </div>
      </div>

      <!-- Calculation Modal -->
      <div id="calc-modal" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-header">
            <h3 style="font-size: 1.1rem; font-weight: 700;">How Career Readiness is Calculated</h3>
            <button class="btn-close" id="btn-close-modal">&times;</button>
          </div>
          <div class="modal-body" style="font-size: 0.88rem; line-height: 1.6;">
            <p style="margin-bottom: 12px;">
              Student Pulse AI uses a <strong>deterministic, evidence-grounded scoring engine</strong>.
              We never guess student abilities or use opaque black-box scoring.
            </p>
            <div style="background: #f1f5f9; padding: 12px; border-radius: var(--radius-sm); font-family: monospace; font-size: 0.82rem; margin-bottom: 16px;">
              Readiness Score = [ Σ(Achieved Weighted Criteria) ÷ Σ(Applicable Weights) ] × 100
            </div>
            <h4 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 6px;">Evaluation Pillars:</h4>
            <ul style="padding-left: 20px; margin-bottom: 16px;">
              <li><strong>Core Role Skills Match (40%):</strong> Compares demonstrated proficiency (1-4) with role benchmark.</li>
              <li><strong>Assessment Benchmark (25%):</strong> Evaluates verified technical quiz and aptitude test performance.</li>
              <li><strong>Project Portfolio Coverage (20%):</strong> Rewards skills proven in practical code repositories and deliverables.</li>
              <li><strong>Interview & Soft-Skills Readiness (15%):</strong> Incorporates communication assessments and mock practice evidence.</li>
            </ul>
            <div class="alert-box alert-warning" style="font-size: 0.8rem; margin: 0;">
              <strong>Missing Evidence Principle:</strong> Missing evidence is flagged as <em>"Needs Evidence / Unknown"</em>. It is never treated as a negative failure, but as a roadmap suggestion.
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" id="btn-modal-gotit">Understood</button>
          </div>
        </div>
      </div>
    `;

    // Modal listeners
    const modal = container.querySelector('#calc-modal');
    container.querySelector('#btn-calc-modal').addEventListener('click', () => modal.classList.add('active'));
    container.querySelector('#btn-close-modal').addEventListener('click', () => modal.classList.remove('active'));
    container.querySelector('#btn-modal-gotit').addEventListener('click', () => modal.classList.remove('active'));
  } catch (error) {
    container.innerHTML = `
      <div class="alert-box alert-warning">
        Failed to load dashboard data: ${escapeHtml(error.message || 'Unknown error')}
      </div>
    `;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
