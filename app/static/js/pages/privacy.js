import { api } from '../api.js';
import { auth } from '../auth.js';

export async function renderPrivacy(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Loading privacy settings and consent controls...</p>
    </div>
  `;

  try {
    const profile = await api.get('/students/me');
    const evidence = await api.get('/students/me/evidence');
    const assessments = await api.get('/assessments');
    const projects = await api.get('/students/me/projects');
    const goals = await api.get('/career-goals');

    container.innerHTML = `
      <div style="margin-bottom: 24px;">
        <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Profile & Privacy Settings</h2>
        <p style="color: var(--text-muted); font-size: 0.88rem;">Manage your profile attributes, download your evidence data, and review consent safeguards.</p>
      </div>

      <!-- Profile Edit Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div class="card-title">Profile Information</div>
        </div>
        <form id="form-update-profile" style="max-width: 480px;">
          <div class="form-group">
            <label class="form-label" for="edit-name">Display Name</label>
            <input type="text" id="edit-name" class="form-control" value="${escapeHtml(profile.display_name)}" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email Address (Read-only)</label>
            <input type="email" class="form-control" value="${escapeHtml(profile.email)}" disabled style="background: #f1f5f9;" />
          </div>
          <div class="form-group">
            <label class="form-label">Account Created</label>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
              ${new Date(profile.created_at).toLocaleString()}
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-sm">Update Profile Name</button>
        </form>
      </div>

      <!-- Data Rights & Export Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div class="card-title">Data Portability & Export (Right of Access)</div>
        </div>
        <p style="font-size: 0.88rem; color: var(--text-main); margin-bottom: 16px;">
          You can download a complete, machine-readable JSON copy of your student profile, verified skill evidence, assessments, and projects at any time.
        </p>
        <button id="btn-export-data" class="btn btn-outline">
          📥 Export Complete Student Data (JSON)
        </button>
      </div>

      <!-- Reporting / Feedback Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div class="card-title">Report Inaccurate Recommendation</div>
          <div class="card-subtitle">Contest an ungrounded or biased action item</div>
        </div>
        <form id="form-report" style="max-width: 600px;">
          <div class="form-group">
            <label class="form-label">Recommendation or Skill Area</label>
            <input type="text" id="report-topic" class="form-control" required placeholder="e.g. Action item regarding Docker was irrelevant" />
          </div>
          <div class="form-group">
            <label class="form-label">Reason / Discrepancy Description</label>
            <textarea id="report-desc" class="form-control" required placeholder="Explain why the recommendation was inaccurate or why the observed level was wrong..."></textarea>
          </div>
          <button type="submit" class="btn btn-outline btn-sm">Submit Report for Faculty Review</button>
        </form>
      </div>

      <!-- Consent & Privacy Policy Card -->
      <div class="card" style="margin-bottom: 24px; border-left: 4px solid var(--info);">
        <div class="card-header">
          <div class="card-title">Educational Privacy & AI Safety Safeguards</div>
        </div>
        <ul style="padding-left: 20px; font-size: 0.85rem; line-height: 1.8; color: var(--text-main);">
          <li><strong>Purpose Limitation:</strong> Evidence is collected strictly for academic guidance and placement preparedness.</li>
          <li><strong>No Automated High-Impact Decisions:</strong> Student Pulse AI never makes admission, graduation, grading, or employment decisions automatically.</li>
          <li><strong>Zero Secret Exposure:</strong> No API keys or credentials are stored in frontend client code.</li>
          <li><strong>Missing Evidence Standard:</strong> Missing evidence is designated as <em>"Needs Evidence / Unknown"</em> and never treated as student failure.</li>
          <li><strong>Audit Trail:</strong> System events are logged without storing passwords or private student prompts.</li>
        </ul>
      </div>

      <!-- Danger Zone: Account Deletion -->
      <div class="card" style="border: 1px solid var(--danger-border); background: #fffcfc;">
        <div class="card-header">
          <div class="card-title" style="color: var(--danger);">Danger Zone: Permanent Account Deletion</div>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">
          Once deleted, your account, assessments, project evidence, and recommendations will be permanently purged from the database. This action cannot be reversed.
        </p>
        <button id="btn-delete-account" class="btn btn-danger btn-sm">
          ⚠️ Delete My Account & All Evidence
        </button>
      </div>
    `;

    // Update Name Listener
    container.querySelector('#form-update-profile').addEventListener('submit', async (e) => {
      e.preventDefault();
      const newName = container.querySelector('#edit-name').value;
      try {
        const updated = await api.patch('/students/me', { display_name: newName });
        auth.setSession({ ...auth.getStudent(), display_name: updated.display_name });
        alert('Profile display name updated successfully!');
      } catch (err) {
        alert('Failed to update profile: ' + err.message);
      }
    });

    // Export Data Listener
    container.querySelector('#btn-export-data').addEventListener('click', () => {
      const exportObject = {
        exported_at: new Date().toISOString(),
        profile,
        evidence,
        assessments,
        projects,
        goals
      };
      const blob = new Blob([JSON.stringify(exportObject, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `student_pulse_export_${profile.student_id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });

    // Report listener
    container.querySelector('#form-report').addEventListener('submit', (e) => {
      e.preventDefault();
      alert('Thank you for your report. The system intelligence audit team has received your feedback.');
      container.querySelector('#form-report').reset();
    });

    // Delete Account Listener
    container.querySelector('#btn-delete-account').addEventListener('click', async () => {
      const confirmFirst = confirm('Are you sure you want to permanently delete your account and all evidence?');
      if (!confirmFirst) return;

      const confirmSecond = confirm('This cannot be undone. All your project records and assessments will be erased immediately. Proceed?');
      if (!confirmSecond) return;

      try {
        await api.delete('/students/me');
        alert('Your account has been deleted.');
        auth.logout();
      } catch (err) {
        alert('Deletion failed: ' + err.message);
      }
    });

  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load privacy settings: ${escapeHtml(error.message)}</div>`;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
