import { api } from '../api.js';

export async function renderInterviewReadiness(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Analyzing interview indicators and soft-skills evidence...</p>
    </div>
  `;

  try {
    const interviewData = await api.post('/analysis/interview-readiness', {});
    const level = interviewData.interview_readiness_level || "Practice Required";
    const commScore = interviewData.communication_score !== null ? `${interviewData.communication_score}%` : 'No score recorded';

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <div>
          <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Interview Readiness</h2>
          <p style="color: var(--text-muted); font-size: 0.88rem;">Behavioral, verbal communication, and technical interview preparation indicators.</p>
        </div>
        <a href="#action-plan" class="btn btn-primary btn-sm">⚡ Practice Interview Topics</a>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="grid-3" style="margin-bottom: 24px;">
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">🗣️</div>
          <div>
            <div class="stat-val" style="font-size: 1.3rem;">${commScore}</div>
            <div class="stat-label">Communication Benchmark</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--info-bg); color: #0891b2;">🎯</div>
          <div>
            <div class="stat-val">${interviewData.mock_practices_count}</div>
            <div class="stat-label">Mock Interviews Recorded</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--success-bg); color: #059669;">👥</div>
          <div>
            <div class="stat-val">${interviewData.presentation_evidence_count}</div>
            <div class="stat-label">Presentation Deliverables</div>
          </div>
        </div>
      </div>

      <!-- Interview Preparation Card -->
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div>
            <div class="card-title">Placement & Interview Preparedness</div>
            <div class="card-subtitle">Transparent indicators based on verified soft-skills and assessment data</div>
          </div>
          <span class="badge ${level === 'Interview Ready' ? 'badge-strong' : (level === 'Practice Required' ? 'badge-weak' : 'badge-low')}">
            ${escapeHtml(level)}
          </span>
        </div>

        <div style="margin: 16px 0 24px;">
          <p style="font-size: 0.9rem; color: var(--text-main); line-height: 1.6;">
            ${level === 'Interview Ready' 
              ? 'Excellent progress! Your profile records high communication benchmarks and verified mock interview practice sessions. Continue refining STAR behavioral responses and architecture tradeoff explanations.'
              : 'Technical skill is only half the interview. Placement panels look for clear verbal articulation, structured problem breakdown, and collaborative teamwork.'
            }
          </p>
        </div>

        <div style="border-top: 1px solid var(--border-color); padding-top: 20px;">
          <div style="font-size: 0.82rem; font-weight: 700; color: var(--secondary); text-transform: uppercase; margin-bottom: 12px;">
            Recommended Interview Practice Topics:
          </div>
          <div style="display: flex; flex-direction: column; gap: 10px;">
            ${(interviewData.recommended_practice_topics || []).map(topic => `
              <div style="padding: 14px; background: #fafbfc; border: 1px solid var(--border-color); border-radius: var(--radius-sm); display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="font-size: 1.1rem;">💡</span>
                  <span style="font-weight: 600; font-size: 0.88rem; color: var(--secondary);">${escapeHtml(topic)}</span>
                </div>
                <a href="#action-plan" class="btn btn-outline btn-sm">Add to Plan</a>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- STAR Method Card -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Framework: The STAR Technique for Behavioral Rounds</div>
        </div>
        <div class="grid-4" style="margin-top: 12px;">
          <div style="padding: 14px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <div style="font-weight: 800; color: var(--primary); font-size: 1.1rem; margin-bottom: 4px;">S - Situation</div>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Set the scene and context of the engineering challenge or college project.</p>
          </div>
          <div style="padding: 14px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <div style="font-weight: 800; color: var(--primary); font-size: 1.1rem; margin-bottom: 4px;">T - Task</div>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Describe your exact individual responsibility in resolving the problem.</p>
          </div>
          <div style="padding: 14px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <div style="font-weight: 800; color: var(--primary); font-size: 1.1rem; margin-bottom: 4px;">A - Action</div>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Explain the technical decisions, code modules, and algorithms you applied.</p>
          </div>
          <div style="padding: 14px; background: #f8fafc; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
            <div style="font-weight: 800; color: var(--primary); font-size: 1.1rem; margin-bottom: 4px;">R - Result</div>
            <p style="font-size: 0.8rem; color: var(--text-muted);">Share the measurable outcome (e.g. latency reduced by 40%, project completed on time).</p>
          </div>
        </div>
      </div>
    `;
  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load interview readiness: ${escapeHtml(error.message)}</div>`;
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
