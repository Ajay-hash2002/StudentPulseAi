import { api } from '../api.js';

export async function renderProjectReadiness(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Analyzing project portfolio and capability coverage...</p>
    </div>
  `;

  try {
    const goals = await api.get('/career-goals');
    const targetRole = goals && goals.length > 0 ? goals[0].target_role : "Backend Developer";

    const projReadiness = await api.post('/analysis/project-readiness', { target_role: targetRole });
    const projects = await api.get('/students/me/projects');

    const coverage = projReadiness.project_coverage_pct || 0;

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <div>
          <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Project Readiness</h2>
          <p style="color: var(--text-muted); font-size: 0.88rem;">Evaluating practical application of role skills in software deliverables.</p>
        </div>
        <a href="#profile" class="btn btn-outline btn-sm">+ Add New Project</a>
      </div>

      <!-- Overview Cards -->
      <div class="grid-3" style="margin-bottom: 24px;">
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">💼</div>
          <div>
            <div class="stat-val">${coverage}%</div>
            <div class="stat-label">Role Skills Coverage</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--success-bg); color: #059669;">📦</div>
          <div>
            <div class="stat-val">${projReadiness.completed_projects_count}</div>
            <div class="stat-label">Completed Deliverables</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: #fdf2f8; color: #db2777;">🎯</div>
          <div>
            <div class="stat-val" style="font-size: 1.2rem; margin-top: 4px;">${escapeHtml(targetRole)}</div>
            <div class="stat-label">Target Role Standard</div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div>
            <div class="card-title">Portfolio Readiness Assessment</div>
            <div class="card-subtitle">${escapeHtml(projReadiness.readiness_summary)}</div>
          </div>
          <span class="badge ${coverage >= 60 ? 'badge-strong' : 'badge-weak'}">
            ${coverage >= 60 ? 'Portfolio Ready' : 'Development Required'}
          </span>
        </div>

        <div class="grid-2" style="margin-top: 16px;">
          <!-- Demonstrated -->
          <div style="background: var(--success-bg); border: 1px solid var(--success-border); border-radius: var(--radius-sm); padding: 18px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #065f46; text-transform: uppercase; margin-bottom: 8px;">
              ✅ Demonstrated in Code (${projReadiness.demonstrated_skills?.length || 0})
            </div>
            ${projReadiness.demonstrated_skills && projReadiness.demonstrated_skills.length > 0 ? `
              <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${projReadiness.demonstrated_skills.map(s => `
                  <span class="badge badge-strong">${escapeHtml(s)}</span>
                `).join('')}
              </div>
            ` : `
              <div style="font-size: 0.82rem; color: #065f46; font-style: italic;">
                No skills proven in project deliverables yet.
              </div>
            `}
          </div>

          <!-- Missing -->
          <div style="background: #fffbeb; border: 1px solid var(--warning-border); border-radius: var(--radius-sm); padding: 18px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #92400e; text-transform: uppercase; margin-bottom: 8px;">
              ⚠️ Missing Project Capabilities (${projReadiness.missing_role_capabilities?.length || 0})
            </div>
            ${projReadiness.missing_role_capabilities && projReadiness.missing_role_capabilities.length > 0 ? `
              <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                ${projReadiness.missing_role_capabilities.map(s => `
                  <span class="badge badge-missing">${escapeHtml(s)}</span>
                `).join('')}
              </div>
            ` : `
              <div style="font-size: 0.82rem; color: #92400e;">
                All required role competencies are covered in your project portfolio!
              </div>
            `}
          </div>
        </div>
      </div>

      <!-- Project List -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Recorded Student Projects (${projects?.length || 0})</div>
        </div>

        ${projects && projects.length > 0 ? `
          <div style="display: flex; flex-direction: column; gap: 16px;">
            ${projects.map(p => `
              <div style="border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 18px; background: #fafbfc;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                  <h4 style="font-size: 1.05rem; font-weight: 700; color: var(--secondary);">${escapeHtml(p.title)}</h4>
                  <span class="badge ${p.status === 'completed' ? 'badge-strong' : 'badge-weak'}">${escapeHtml(p.status)}</span>
                </div>
                <p style="font-size: 0.88rem; color: var(--text-main); margin: 8px 0 12px;">${escapeHtml(p.description)}</p>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted);">Skills Demonstrated:</span>
                  ${(p.skills_used || []).map(s => `
                    <span class="badge badge-low" style="font-size: 0.72rem;">${escapeHtml(s)}</span>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        ` : `
          <div class="state-box">
            <div class="state-icon">💼</div>
            <p>No projects submitted yet. Build practical projects to verify hands-on capability.</p>
          </div>
        `}
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load project readiness: ${escapeHtml(error.message)}</div>`;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
