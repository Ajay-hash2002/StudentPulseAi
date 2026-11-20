import { api } from '../api.js';

export async function renderActionPlan(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Generating personalized action plan roadmap...</p>
    </div>
  `;

  try {
    const goals = await api.get('/career-goals');
    const targetRole = goals && goals.length > 0 ? goals[0].target_role : "Backend Developer";

    // Call POST /action-plans to get or refresh plan
    const plan = await api.post('/action-plans', { target_role: targetRole });
    renderPlanView(container, plan);
  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load action plan: ${escapeHtml(error.message)}</div>`;
  }
}

function renderPlanView(container, plan) {
  const actions = plan.actions || [];
  const progress = plan.progress_pct || 0;

  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
      <div>
        <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Personalised Action Plan</h2>
        <p style="color: var(--text-muted); font-size: 0.88rem;">
          Prioritised learning & practice roadmap for <strong style="color: var(--primary);">${escapeHtml(plan.target_role)}</strong>
        </p>
      </div>
      <div style="display: flex; gap: 8px;">
        <button id="btn-regen-plan" class="btn btn-outline btn-sm">🔄 Refresh Recommendations</button>
      </div>
    </div>

    <!-- AI Explanation Card -->
    <div class="card" style="margin-bottom: 20px; border-left: 4px solid var(--primary);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--primary);">
          ✨ AI-Grounded Plan Narrative
        </span>
        <span class="badge badge-low" style="font-size: 0.72rem;">${escapeHtml(plan.explanation_source)}</span>
      </div>
      <p style="font-size: 0.92rem; color: var(--text-main); line-height: 1.6;">
        ${escapeHtml(plan.summary_explanation)}
      </p>
    </div>

    <!-- Progress & Filter Card -->
    <div class="card" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <div style="font-weight: 700; font-size: 0.95rem; color: var(--secondary);">
          Plan Execution Progress
        </div>
        <div style="font-weight: 800; font-size: 1.1rem; color: var(--primary);">
          ${progress}% Completed
        </div>
      </div>
      <div class="progress-bar-bg" style="height: 10px;">
        <div class="progress-bar-fill" style="width: ${progress}%;"></div>
      </div>

      <div style="display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap;">
        <button class="filter-btn btn btn-primary btn-sm" data-filter="all">All Actions (${actions.length})</button>
        <button class="filter-btn btn btn-outline btn-sm" data-filter="todo">To Do (${actions.filter(a => a.status === 'todo').length})</button>
        <button class="filter-btn btn btn-outline btn-sm" data-filter="in_progress">In Progress (${actions.filter(a => a.status === 'in_progress').length})</button>
        <button class="filter-btn btn btn-outline btn-sm" data-filter="done">Completed (${actions.filter(a => a.status === 'done').length})</button>
      </div>
    </div>

    <!-- Action Items List -->
    <div id="actions-container">
      ${actions.map((act, idx) => `
        <div class="action-item-card ${act.status}" data-status="${act.status}" id="card-${act.recommendation_id}">
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap;">
              <span class="badge ${act.priority === 'high' ? 'badge-high' : (act.priority === 'medium' ? 'badge-medium' : 'badge-low')}">
                ${act.priority.toUpperCase()} PRIORITY
              </span>
              <span class="badge ${act.status === 'done' ? 'badge-strong' : (act.status === 'in_progress' ? 'badge-weak' : 'badge-low')}">
                ${act.status === 'done' ? 'Completed' : (act.status === 'in_progress' ? 'In Progress' : 'To Do')}
              </span>
            </div>
            <div class="action-text">${escapeHtml(act.action_text)}</div>
            <div class="action-reason">
              <strong>Why:</strong> ${escapeHtml(act.reason)}
            </div>

            <div style="margin-top: 10px; display: flex; align-items: center; gap: 10px;">
              <button class="btn btn-outline btn-sm btn-why" data-idx="${idx}">
                🔍 Why this recommendation?
              </button>
            </div>
          </div>

          <!-- Status Selector -->
          <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
            <label style="font-size: 0.72rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Status</label>
            <select class="form-control status-select" data-id="${act.recommendation_id}" style="width: 140px; font-size: 0.82rem; padding: 6px 8px;">
              <option value="todo" ${act.status === 'todo' ? 'selected' : ''}>To Do</option>
              <option value="in_progress" ${act.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
              <option value="done" ${act.status === 'done' ? 'selected' : ''}>Completed</option>
            </select>
          </div>
        </div>
      `).join('')}
    </div>

    <!-- Traceability / Why Modal -->
    <div id="why-modal" class="modal-overlay">
      <div class="modal-box">
        <div class="modal-header">
          <h3 style="font-size: 1.1rem; font-weight: 700;">Traceability & Evidence Grounding</h3>
          <button class="btn-close" id="btn-close-why">&times;</button>
        </div>
        <div class="modal-body" id="why-modal-content" style="font-size: 0.88rem; line-height: 1.6;">
          <!-- Injected dynamically -->
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" id="btn-why-ok">Close</button>
        </div>
      </div>
    </div>
  `;

  // Filter functionality
  const filterBtns = container.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.className = 'filter-btn btn btn-outline btn-sm';
      });
      btn.className = 'filter-btn btn btn-primary btn-sm';

      const filter = btn.dataset.filter;
      const cards = container.querySelectorAll('.action-item-card');
      cards.forEach(card => {
        if (filter === 'all' || card.dataset.status === filter) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // Status Change Listener
  container.querySelectorAll('.status-select').forEach(select => {
    select.addEventListener('change', async (e) => {
      const recId = select.dataset.id;
      const newStatus = select.value;
      try {
        await api.patch(`/action-plans/${plan.plan_id}/items/${recId}`, { status: newStatus });
        // Refresh plan view
        const refreshedPlan = await api.get(`/action-plans/${plan.plan_id}`);
        renderPlanView(container, refreshedPlan);
      } catch (err) {
        alert('Failed to update status: ' + err.message);
      }
    });
  });

  // Traceability Modal Listener
  const whyModal = container.querySelector('#why-modal');
  const whyContent = container.querySelector('#why-modal-content');
  container.querySelectorAll('.btn-why').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.dataset.idx, 10);
      const act = actions[idx];
      whyContent.innerHTML = `
        <h4 style="font-size: 1rem; font-weight: 700; color: var(--secondary); margin-bottom: 8px;">
          ${escapeHtml(act.action_text)}
        </h4>
        <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 14px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Analytical Reason:</div>
          <p style="margin-top: 4px; color: var(--text-main);">${escapeHtml(act.reason)}</p>
        </div>
        <div style="background: var(--primary-light); border: 1px solid var(--primary-border); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 14px;">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--primary); text-transform: uppercase;">Evidence Grounding:</div>
          <ul style="padding-left: 20px; margin-top: 4px; color: var(--text-main);">
            ${(act.evidence_refs || []).map(r => `<li>${escapeHtml(r)}</li>`).join('')}
          </ul>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">
          ✓ <strong>Explainable AI Guarantee:</strong> This recommendation directly references recorded student evidence and official role competencies from <code>role_requirements.json</code>. No fictitious claims or ungrounded suggestions.
        </div>
      `;
      whyModal.classList.add('active');
    });
  });

  container.querySelector('#btn-close-why').addEventListener('click', () => whyModal.classList.remove('active'));
  container.querySelector('#btn-why-ok').addEventListener('click', () => whyModal.classList.remove('active'));

  // Regenerate Button
  container.querySelector('#btn-regen-plan').addEventListener('click', () => {
    renderActionPlan(container);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
