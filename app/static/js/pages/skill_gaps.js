import { api } from '../api.js';

export async function renderSkillGaps(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Comparing demonstrated evidence against role benchmarks...</p>
    </div>
  `;

  try {
    const catalogRoles = await api.get('/catalog/roles');
    const goals = await api.get('/career-goals');
    const defaultRole = goals && goals.length > 0 ? goals[0].target_role : "Backend Developer";

    await renderSkillGapsForRole(container, defaultRole, catalogRoles);
  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load skill gaps: ${escapeHtml(error.message)}</div>`;
  }
}

async function renderSkillGapsForRole(container, targetRole, catalogRoles) {
  const gapsData = await api.post('/analysis/skill-gaps', { target_role: targetRole });

  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
      <div>
        <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Skill-Gap Analysis</h2>
        <p style="color: var(--text-muted); font-size: 0.88rem;">Grounded comparison between demonstrated profile evidence and target industry roles.</p>
      </div>

      <!-- Role Selector -->
      <div style="display: flex; align-items: center; gap: 10px;">
        <label for="select-role" style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted);">Target Role:</label>
        <select id="select-role" class="form-control" style="width: auto; font-weight: 600; color: var(--primary);">
          ${(catalogRoles || []).map(r => `
            <option value="${escapeHtml(r.title)}" ${r.title.toLowerCase() === targetRole.toLowerCase() ? 'selected' : ''}>
              ${escapeHtml(r.title)}
            </option>
          `).join('')}
        </select>
      </div>
    </div>

    <!-- Summary Metrics Grid -->
    <div class="grid-4" style="margin-bottom: 24px;">
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">🎯</div>
        <div>
          <div class="stat-val">${gapsData.total_required_skills}</div>
          <div class="stat-label">Required Competencies</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--success-bg); color: #059669;">✅</div>
        <div>
          <div class="stat-val" style="color: #059669;">${gapsData.strong_count}</div>
          <div class="stat-label">Strong (Meets Goal)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fff7ed; color: #ea580c;">📈</div>
        <div>
          <div class="stat-val" style="color: #ea580c;">${gapsData.weak_count}</div>
          <div class="stat-label">Developing / Below Level</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: var(--warning-bg); color: #d97706;">❓</div>
        <div>
          <div class="stat-val" style="color: #d97706;">${gapsData.missing_count}</div>
          <div class="stat-label">Needs Evidence / Unknown</div>
        </div>
      </div>
    </div>

    <!-- Visual Chart & Matrix Grid -->
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <div>
          <div class="card-title">Competency Comparison Chart</div>
          <div class="card-subtitle">Required level (1-4) vs your demonstrated level</div>
        </div>
        <span class="badge badge-low">Rule-based Matrix</span>
      </div>
      <div style="height: 280px; position: relative;">
        <canvas id="gap-radar-chart"></canvas>
      </div>
    </div>

    <!-- Detailed Gap Breakdown Table -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Detailed Evidence & Gap Register</div>
          <div class="card-subtitle">Every gap is linked to a reason and supporting or missing evidence</div>
        </div>
        <a href="#action-plan" class="btn btn-primary btn-sm">Generate Action Plan →</a>
      </div>

      <div class="table-responsive">
        <table class="custom-table">
          <thead>
            <tr>
              <th>Skill</th>
              <th>Required Level</th>
              <th>Demonstrated Level</th>
              <th>Gap Status</th>
              <th>Analytical Reason</th>
              <th>Supporting Evidence Reference</th>
            </tr>
          </thead>
          <tbody>
            ${gapsData.gaps.map(g => {
              const statusBadgeClass = g.status === 'strong'
                ? 'badge-strong'
                : (g.status === 'weak' ? 'badge-weak' : 'badge-missing');
              
              const statusText = g.status === 'strong'
                ? 'Strong'
                : (g.status === 'weak' ? 'Developing' : 'Needs Evidence');

              return `
                <tr>
                  <td><strong>${escapeHtml(g.skill)}</strong></td>
                  <td><span class="badge badge-low">Level ${g.required_level}</span></td>
                  <td>
                    <span class="badge ${g.observed_level ? getObservedBadge(g.observed_level) : 'badge-missing'}">
                      ${escapeHtml(g.level_label)}
                    </span>
                  </td>
                  <td><span class="badge ${statusBadgeClass}">${statusText}</span></td>
                  <td style="font-size: 0.82rem; color: var(--text-main);">${escapeHtml(g.reason)}</td>
                  <td style="font-size: 0.78rem; color: var(--text-muted); max-width: 260px;">
                    ${(g.evidence_refs || []).map(ref => `<div>• ${escapeHtml(ref)}</div>`).join('')}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>

      <div class="alert-box alert-info" style="margin-top: 20px; font-size: 0.8rem;">
        💡 <strong>Transparency Note:</strong> Skills flagged with <em>"Needs Evidence / Unknown"</em> mean no assessment or project deliverable has been recorded yet. You can bridge this by submitting a quiz or adding a project on your Profile.
      </div>
    </div>
  `;

  // Selector listener
  const roleSelect = container.querySelector('#select-role');
  roleSelect.addEventListener('change', () => {
    renderSkillGapsForRole(container, roleSelect.value, catalogRoles);
  });

  // Render chart
  renderComparisonChart(container, gapsData.gaps);
}

function renderComparisonChart(container, gaps) {
  const canvas = container.querySelector('#gap-radar-chart');
  if (!canvas || !window.Chart || !gaps || gaps.length === 0) return;

  const labels = gaps.map(g => g.skill);
  const requiredLevels = gaps.map(g => g.required_level);
  const observedLevels = gaps.map(g => g.observed_level || 0);

  new window.Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Role Requirement Level (Target)',
          data: requiredLevels,
          backgroundColor: 'rgba(148, 163, 184, 0.4)',
          borderColor: '#94a3b8',
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: 'Demonstrated Level (Current)',
          data: observedLevels,
          backgroundColor: observedLevels.map((val, idx) => {
            if (val >= requiredLevels[idx]) return 'rgba(16, 185, 129, 0.7)';
            if (val > 0) return 'rgba(245, 158, 11, 0.7)';
            return 'rgba(239, 68, 68, 0.2)';
          }),
          borderColor: observedLevels.map((val, idx) => {
            if (val >= requiredLevels[idx]) return '#10b981';
            if (val > 0) return '#f59e0b';
            return '#ef4444';
          }),
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 4,
          ticks: {
            stepSize: 1,
            callback: (v) => {
              const m = { 0: 'None', 1: 'Beginner', 2: 'Basic', 3: 'Interm.', 4: 'Adv.' };
              return m[v] || v;
            }
          },
          title: { display: true, text: 'Proficiency Level (0-4)' }
        }
      },
      plugins: {
        legend: { position: 'top' }
      }
    }
  });
}

function getObservedBadge(lvl) {
  if (lvl >= 3) return 'badge-strong';
  if (lvl === 2) return 'badge-low';
  return 'badge-weak';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
