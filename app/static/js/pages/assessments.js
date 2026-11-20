import { api } from '../api.js';

export async function renderAssessments(container) {
  container.innerHTML = `
    <div class="state-box">
      <div class="spinner"></div>
      <p>Loading assessment history and analyzing benchmarks...</p>
    </div>
  `;

  try {
    const assessments = await api.get('/assessments');
    const scores = (assessments || []).map(a => a.score_or_result);
    const avgScore = scores.length > 0 ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : 0;
    const highestScore = scores.length > 0 ? Math.max(...scores).toFixed(1) : 0;

    // Identify weak areas (< 75%)
    const improvementAreas = (assessments || []).filter(a => (a.score_or_result / a.max_score) * 100 < 75);

    container.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <div>
          <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Assessment Analysis</h2>
          <p style="color: var(--text-muted); font-size: 0.88rem;">Academic, technical quiz, and aptitude test benchmarks.</p>
        </div>
        <button id="btn-submit-assessment" class="btn btn-primary">+ Submit Assessment Score</button>
      </div>

      <!-- Quick Metrics -->
      <div class="grid-3" style="margin-bottom: 24px;">
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">📝</div>
          <div>
            <div class="stat-val">${assessments?.length || 0}</div>
            <div class="stat-label">Total Tests Taken</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--info-bg); color: #0891b2;">🎯</div>
          <div>
            <div class="stat-val">${avgScore}%</div>
            <div class="stat-label">Average Performance</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: var(--success-bg); color: #059669;">🏆</div>
          <div>
            <div class="stat-val">${highestScore}%</div>
            <div class="stat-label">Highest Score Achieved</div>
          </div>
        </div>
      </div>

      <!-- Assessment Breakdown & Chart Grid -->
      <div class="grid-2">
        <!-- History Table -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">Completed Assessments</div>
            <span class="badge badge-low">Verified Scores</span>
          </div>

          ${assessments && assessments.length > 0 ? `
            <div class="table-responsive">
              <table class="custom-table">
                <thead>
                  <tr>
                    <th>Assessment Topic</th>
                    <th>Score</th>
                    <th>Benchmark Status</th>
                    <th>Date Taken</th>
                  </tr>
                </thead>
                <tbody>
                  ${assessments.map(a => {
                    const pct = (a.score_or_result / a.max_score) * 100;
                    return `
                      <tr>
                        <td><strong>${escapeHtml(a.assessment_type)}</strong></td>
                        <td>
                          <span style="font-weight: 700;">${a.score_or_result}</span> / ${a.max_score} (${pct.toFixed(0)}%)
                        </td>
                        <td>
                          <span class="badge ${pct >= 80 ? 'badge-strong' : (pct >= 65 ? 'badge-low' : 'badge-weak')}">
                            ${pct >= 80 ? 'Above Benchmark' : (pct >= 65 ? 'Satisfactory' : 'Needs Review')}
                          </span>
                        </td>
                        <td style="color: var(--text-muted); font-size: 0.8rem;">
                          ${new Date(a.completed_at).toLocaleDateString()}
                        </td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          ` : `
            <div class="state-box">
              <div class="state-icon">📝</div>
              <p>No assessment records submitted yet.</p>
            </div>
          `}
        </div>

        <!-- Analytical Insights & Improvement Areas -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">Performance Insights & Improvement Areas</div>
          </div>

          <div style="margin-bottom: 20px;">
            <div style="font-size: 0.85rem; line-height: 1.5; color: var(--text-main); margin-bottom: 16px;">
              ${assessments && assessments.length > 0
                ? `You have completed <strong>${assessments.length} assessment(s)</strong> with an overall benchmark average of <strong>${avgScore}%</strong>. Assessment scores are directly mapped to corresponding technical competencies (e.g. Python Quiz establishes Python skill evidence).`
                : 'No assessments have been recorded for your profile. Academic and technical evaluations provide reliable grounding for career readiness scores.'
              }
            </div>

            <div style="font-size: 0.82rem; font-weight: 700; color: #b45309; text-transform: uppercase; margin-bottom: 8px;">
              Target Improvement Recommendations (${improvementAreas.length})
            </div>
            ${improvementAreas.length > 0 ? `
              <div style="display: flex; flex-direction: column; gap: 8px;">
                ${improvementAreas.map(a => `
                  <div style="padding: 12px; background: #fffbeb; border: 1px solid var(--warning-border); border-radius: var(--radius-sm); font-size: 0.84rem;">
                    <div style="font-weight: 700; color: #78350f;">${escapeHtml(a.assessment_type)} (${a.score_or_result}/${a.max_score})</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                      Score is below the 75% benchmark. Target targeted practice problems in this subject before placement interviews.
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div style="font-size: 0.84rem; color: #059669; background: var(--success-bg); border: 1px solid var(--success-border); padding: 12px; border-radius: var(--radius-sm);">
                🎉 All completed assessments meet or exceed the 75% placement readiness benchmark!
              </div>
            `}
          </div>

          <!-- Assessment Canvas Chart -->
          <div style="margin-top: 20px;">
            <canvas id="assessment-chart" style="max-height: 220px;"></canvas>
          </div>
        </div>
      </div>

      <!-- Submit Assessment Modal -->
      <div id="modal-assessment" class="modal-overlay">
        <div class="modal-box">
          <div class="modal-header">
            <h3 style="font-size: 1.1rem; font-weight: 700;">Submit Assessment Result</h3>
            <button class="btn-close modal-close-btn">&times;</button>
          </div>
          <form id="form-assessment">
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">Assessment Subject / Title</label>
                <input type="text" id="ass-type" class="form-control" required placeholder="e.g. Python Quiz, DSA Test, Communication Benchmark" />
              </div>
              <div class="form-group">
                <label class="form-label">Score Achieved (0 - 100)</label>
                <input type="number" id="ass-score" class="form-control" step="0.5" min="0" max="100" required placeholder="85.0" />
              </div>
              <div class="form-group">
                <label class="form-label">Maximum Score</label>
                <input type="number" id="ass-max" class="form-control" step="1" min="1" value="100" required />
              </div>
              <div class="alert-box alert-info" style="font-size: 0.78rem;">
                Note: Submitting this score automatically correlates and logs skill evidence on your profile.
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-outline modal-close-btn">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Assessment</button>
            </div>
          </form>
        </div>
      </div>
    `;

    // Modal controls
    const modal = container.querySelector('#modal-assessment');
    container.querySelector('#btn-submit-assessment').addEventListener('click', () => modal.classList.add('active'));
    container.querySelectorAll('.modal-close-btn').forEach(b => b.addEventListener('click', () => modal.classList.remove('active')));

    container.querySelector('#form-assessment').addEventListener('submit', async (e) => {
      e.preventDefault();
      const type = container.querySelector('#ass-type').value;
      const score = parseFloat(container.querySelector('#ass-score').value);
      const maxScore = parseFloat(container.querySelector('#ass-max').value);
      await api.post('/assessments', {
        assessment_type: type,
        score_or_result: score,
        max_score: maxScore
      });
      modal.classList.remove('active');
      renderAssessments(container);
    });

    // Render Chart if Chart.js is present
    renderAssessmentChart(container, assessments);

  } catch (error) {
    container.innerHTML = `<div class="alert-box alert-warning">Failed to load assessments: ${escapeHtml(error.message)}</div>`;
  }
}

function renderAssessmentChart(container, assessments) {
  const canvas = container.querySelector('#assessment-chart');
  if (!canvas || !window.Chart || !assessments || assessments.length === 0) return;

  const labels = assessments.map(a => a.assessment_type);
  const data = assessments.map(a => (a.score_or_result / a.max_score) * 100);

  new window.Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Score (%)',
        data: data,
        backgroundColor: data.map(v => v >= 80 ? 'rgba(16, 185, 129, 0.7)' : (v >= 65 ? 'rgba(59, 130, 246, 0.7)' : 'rgba(245, 158, 11, 0.7)')),
        borderColor: data.map(v => v >= 80 ? '#10b981' : (v >= 65 ? '#2563eb' : '#f59e0b')),
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: { display: true, text: 'Score (%)' }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
