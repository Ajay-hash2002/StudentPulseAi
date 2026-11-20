import { api } from '../api.js';

export async function renderProfile(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Loading unified student profile evidence...</p>
    </div>
  `;

  try {
    const profile = await api.get('/students/me');
    const evidence = await api.get('/students/me/evidence');
    const projects = await api.get('/students/me/projects');
    const certs = await api.get('/students/me/certifications');
    const goals = await api.get('/career-goals');
    const catalogRoles = await api.get('/catalog/roles');
    const catalogSkills = await api.get('/catalog/skills');

    const activeGoal = goals && goals.length > 0 ? goals[0] : null;

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <div>
          <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Unified Student Profile</h2>
          <p style="color: var(--text-muted); font-size: 0.88rem;">Consolidated skills, goals, projects, and educational evidence.</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button id="btn-add-skill" class="btn btn-outline btn-sm">+ Add Skill Evidence</button>
          <button id="btn-add-project" class="btn btn-outline btn-sm">+ Add Project</button>
          <button id="btn-add-cert" class="btn btn-outline btn-sm">+ Add Certification</button>
          <button id="btn-set-goal" class="btn btn-primary btn-sm">🎯 Update Goal</button>
        </div>
      </div>

      <!-- Profile & Goal Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="grid-3">
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Student Name</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--secondary); margin-top: 4px;">
              ${escapeHtml(profile.display_name)}
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted);">${escapeHtml(profile.email)}</div>
          </div>
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Target Role Goal</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--primary); margin-top: 4px;">
              ${escapeHtml(activeGoal?.target_role || 'Not Set')}
            </div>
            <div style="font-size: 0.82rem; color: var(--text-muted);">
              Target Date: ${escapeHtml(activeGoal?.target_date || '2027')}
            </div>
          </div>
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Data Protection & Consent</div>
            <div style="display: flex; align-items: center; gap: 6px; margin-top: 6px;">
              <span class="badge badge-strong">Consent Active</span>
              <span style="font-size: 0.75rem; color: var(--text-muted);">Since ${new Date(profile.consent_at || profile.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabbed Evidence View -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Verified Evidence Records (${evidence?.length || 0})</div>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Level 1: Beginner • Level 2: Basic • Level 3: Intermediate • Level 4: Advanced</span>
        </div>

        ${evidence && evidence.length > 0 ? `
          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Skill</th>
                  <th>Observed Level</th>
                  <th>Evidence Source</th>
                  <th>Reference / Deliverable</th>
                  <th>Recorded Date</th>
                </tr>
              </thead>
              <tbody>
                ${evidence.map(ev => `
                  <tr>
                    <td><strong>${escapeHtml(ev.skill_name)}</strong></td>
                    <td>
                      <span class="badge ${getLevelBadge(ev.observed_level)}">
                        Level ${ev.observed_level} (${getLevelName(ev.observed_level)})
                      </span>
                    </td>
                    <td><span class="badge badge-low">${escapeHtml(ev.source_type)}</span></td>
                    <td style="max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                      ${escapeHtml(ev.evidence_reference)}
                    </td>
                    <td style="color: var(--text-muted); font-size: 0.8rem;">
                      ${new Date(ev.date).toLocaleDateString()}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : `
          <div class="state-box">
            <div class="state-icon">📋</div>
            <p>No verified skill evidence submitted yet.</p>
            <button class="btn btn-primary btn-sm" id="btn-empty-skill" style="margin-top: 10px;">+ Record First Skill Evidence</button>
          </div>
        `}
      </div>

      <!-- Projects & Certifications Grid -->
      <div class="grid-2">
        <!-- Projects Card -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">Project Portfolio (${projects?.length || 0})</div>
            <button id="btn-add-project-2" class="btn btn-outline btn-sm">+ Add</button>
          </div>
          ${projects && projects.length > 0 ? `
            <div style="display: flex; flex-direction: column; gap: 12px;">
              ${projects.map(p => `
                <div style="border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px;">
                  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                    <div style="font-weight: 700; color: var(--secondary);">${escapeHtml(p.title)}</div>
                    <span class="badge ${p.status === 'completed' ? 'badge-strong' : 'badge-weak'}">${escapeHtml(p.status)}</span>
                  </div>
                  <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 8px;">${escapeHtml(p.description)}</p>
                  <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                    ${(p.skills_used || []).map(s => `
                      <span class="badge badge-low" style="font-size: 0.7rem;">${escapeHtml(s)}</span>
                    `).join('')}
                  </div>
                </div>
              `).join('')}
            </div>
          ` : `
            <div style="font-size: 0.85rem; color: var(--text-muted); font-style: italic; padding: 20px 0;">
              No projects recorded yet.
            </div>
          `}
        </div>

        <!-- Certifications Card -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">Certifications & Credentials (${certs?.length || 0})</div>
            <button id="btn-add-cert-2" class="btn btn-outline btn-sm">+ Add</button>
          </div>
          ${certs && certs.length > 0 ? `
            <div style="display: flex; flex-direction: column; gap: 12px;">
              ${certs.map(c => `
                <div style="border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px;">
                  <div style="font-weight: 700; color: var(--secondary);">${escapeHtml(c.name)}</div>
                  <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 2px;">
                    Issuer: ${escapeHtml(c.issuer)} • Ref: ${escapeHtml(c.verification_reference || 'N/A')}
                  </div>
                  <div style="font-size: 0.75rem; color: var(--text-light); margin-top: 4px;">
                    Issued: ${new Date(c.issue_date).toLocaleDateString()}
                  </div>
                </div>
              `).join('')}
            </div>
          ` : `
            <div style="font-size: 0.85rem; color: var(--text-muted); font-style: italic; padding: 20px 0;">
              No certifications recorded yet.
            </div>
          `}
        </div>
      </div>

      <!-- Add Skill Modal -->
      <div id="modal-skill" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-header">
            <h3 style="font-size: 1.1rem; font-weight: 700;">Record Skill Evidence</h3>
            <button class="btn-close modal-close-btn">&times;</button>
          </div>
          <form id="form-add-skill">
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label" for="select-skill">Skill Name</label>
                <input list="skills-list" id="input-skill-name" class="form-control" required placeholder="e.g. Python, SQL, React" />
                <datalist id="skills-list">
                  ${(catalogSkills || []).map(s => `<option value="${escapeHtml(s.skill_name)}"></option>`).join('')}
                </datalist>
              </div>
              <div class="form-group">
                <label class="form-label" for="select-source">Evidence Source Type</label>
                <select id="select-source" class="form-control" required>
                  <option value="project">Project Deliverable</option>
                  <option value="assessment">Assessment Result</option>
                  <option value="certification">Certification Credential</option>
                  <option value="interview">Mock Interview / Presentation</option>
                  <option value="self_reported">Coursework / Self-Study</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="input-level">Observed Proficiency Level</label>
                <select id="input-level" class="form-control" required>
                  <option value="1">Level 1 - Beginner (Concepts understood)</option>
                  <option value="2">Level 2 - Basic (Can write simple programs)</option>
                  <option value="3" selected>Level 3 - Intermediate (Can build features independently)</option>
                  <option value="4">Level 4 - Advanced (Architectural depth & optimization)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="input-ref">Evidence Reference / Notes</label>
                <input type="text" id="input-ref" class="form-control" required placeholder="e.g. GitHub repo link, course quiz score, project module" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline modal-close-btn">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Evidence</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Project Modal -->
      <div id="modal-project" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-header">
            <h3 style="font-size: 1.1rem; font-weight: 700;">Add Project Deliverable</h3>
            <button class="btn-close modal-close-btn">&times;</button>
          </div>
          <form id="form-add-project">
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">Project Title</label>
                <input type="text" id="proj-title" class="form-control" required placeholder="e.g. Hospital Management System" />
              </div>
              <div class="form-group">
                <label class="form-label">Description</label>
                <textarea id="proj-desc" class="form-control" required placeholder="Summary of architecture, features, and tools used..."></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Skills Used (comma-separated)</label>
                <input type="text" id="proj-skills" class="form-control" required placeholder="Python, FastAPI, SQL, Docker" />
              </div>
              <div class="form-group">
                <label class="form-label">Status</label>
                <select id="proj-status" class="form-control" required>
                  <option value="completed">Completed</option>
                  <option value="in_progress">In Progress</option>
                  <option value="planned">Planned</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline modal-close-btn">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Project</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Certification Modal -->
      <div id="modal-cert" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-header">
            <h3 style="font-size: 1.1rem; font-weight: 700;">Add Certification</h3>
            <button class="btn-close modal-close-btn">&times;</button>
          </div>
          <form id="form-add-cert">
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">Certification Name</label>
                <input type="text" id="cert-name" class="form-control" required placeholder="e.g. Meta Database Engineer Specialization" />
              </div>
              <div class="form-group">
                <label class="form-label">Issuing Organization</label>
                <input type="text" id="cert-issuer" class="form-control" required placeholder="e.g. Coursera, AWS, Google Cloud" />
              </div>
              <div class="form-group">
                <label class="form-label">Verification Reference / Credential ID</label>
                <input type="text" id="cert-ref" class="form-control" placeholder="e.g. CERT-DB-4091" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline modal-close-btn">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Certification</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Update Goal Modal -->
      <div id="modal-goal" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-header">
            <h3 style="font-size: 1.1rem; font-weight: 700;">Set Target Career Role</h3>
            <button class="btn-close modal-close-btn">&times;</button>
          </div>
          <form id="form-set-goal">
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">Select Target Role</label>
                <select id="goal-role" class="form-control" required>
                  ${(catalogRoles || []).map(r => `
                    <option value="${escapeHtml(r.title)}" ${r.title === activeGoal?.target_role ? 'selected' : ''}>
                      ${escapeHtml(r.title)}
                    </option>
                  `).join('')}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Target Completion Date</label>
                <input type="date" id="goal-date" class="form-control" value="${activeGoal?.target_date || '2027-06-30'}" />
              </div>
              <div class="form-group">
                <label class="form-label">Aspirations & Notes</label>
                <textarea id="goal-notes" class="form-control" placeholder="Specific interests or target companies...">${escapeHtml(activeGoal?.notes || '')}</textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline modal-close-btn">Cancel</button>
              <button type="submit" class="btn btn-primary">Update Goal</button>
            </div>
          </form>
        </div>
      </div>
    `;

    // Hook modal controls
    setupModals(container);

  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load profile: ${escapeHtml(error.message)}</div>`;
  }
}

function setupModals(container) {
  const modalSkill = container.querySelector('#modal-skill');
  const modalProject = container.querySelector('#modal-project');
  const modalCert = container.querySelector('#modal-cert');
  const modalGoal = container.querySelector('#modal-goal');

  const openModal = (m) => m.classList.add('active');
  const closeModal = (m) => m.classList.remove('active');

  container.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      container.querySelectorAll('.modal-overlay').forEach(closeModal);
    });
  });

  const btnSkill = container.querySelector('#btn-add-skill');
  if (btnSkill) btnSkill.addEventListener('click', () => openModal(modalSkill));

  const btnEmptySkill = container.querySelector('#btn-empty-skill');
  if (btnEmptySkill) btnEmptySkill.addEventListener('click', () => openModal(modalSkill));

  const btnProj = container.querySelector('#btn-add-project');
  if (btnProj) btnProj.addEventListener('click', () => openModal(modalProject));

  const btnProj2 = container.querySelector('#btn-add-project-2');
  if (btnProj2) btnProj2.addEventListener('click', () => openModal(modalProject));

  const btnCert = container.querySelector('#btn-add-cert');
  if (btnCert) btnCert.addEventListener('click', () => openModal(modalCert));

  const btnCert2 = container.querySelector('#btn-add-cert-2');
  if (btnCert2) btnCert2.addEventListener('click', () => openModal(modalCert));

  const btnGoal = container.querySelector('#btn-set-goal');
  if (btnGoal) btnGoal.addEventListener('click', () => openModal(modalGoal));

  // Form Submissions
  container.querySelector('#form-add-skill').addEventListener('submit', async (e) => {
    e.preventDefault();
    const skillName = container.querySelector('#input-skill-name').value;
    const sourceType = container.querySelector('#select-source').value;
    const observedLevel = parseInt(container.querySelector('#input-level').value, 10);
    const ref = container.querySelector('#input-ref').value;
    await api.post('/students/me/skills', {
      skill_name: skillName,
      source_type: sourceType,
      observed_level: observedLevel,
      evidence_reference: ref
    });
    closeModal(modalSkill);
    renderProfile(container);
  });

  container.querySelector('#form-add-project').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = container.querySelector('#proj-title').value;
    const desc = container.querySelector('#proj-desc').value;
    const skills = container.querySelector('#proj-skills').value.split(',').map(s => s.trim()).filter(Boolean);
    const status = container.querySelector('#proj-status').value;
    await api.post('/students/me/projects', {
      title,
      description: desc,
      skills_used: skills,
      status
    });
    closeModal(modalProject);
    renderProfile(container);
  });

  container.querySelector('#form-add-cert').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = container.querySelector('#cert-name').value;
    const issuer = container.querySelector('#cert-issuer').value;
    const ref = container.querySelector('#cert-ref').value;
    await api.post('/students/me/certifications', {
      name,
      issuer,
      verification_reference: ref || null
    });
    closeModal(modalCert);
    renderProfile(container);
  });

  container.querySelector('#form-set-goal').addEventListener('submit', async (e) => {
    e.preventDefault();
    const targetRole = container.querySelector('#goal-role').value;
    const targetDate = container.querySelector('#goal-date').value;
    const notes = container.querySelector('#goal-notes').value;
    await api.post('/career-goals', {
      target_role: targetRole,
      target_date: targetDate,
      notes
    });
    closeModal(modalGoal);
    renderProfile(container);
  });
}

function getLevelBadge(lvl) {
  if (lvl >= 3) return 'badge-strong';
  if (lvl === 2) return 'badge-low';
  return 'badge-weak';
}

function getLevelName(lvl) {
  const map = { 1: 'Beginner', 2: 'Basic', 3: 'Intermediate', 4: 'Advanced' };
  return map[lvl] || 'Unknown';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
