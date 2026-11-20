import { auth } from '../auth.js';

export function renderLoginPage(container) {
  container.innerHTML = `
    <div style="max-width: 480px; margin: 40px auto;">
      <div class="card" style="padding: 32px;">
        <div style="text-align: center; margin-bottom: 24px;">
          <div class="brand-logo" style="width: 48px; height: 48px; margin: 0 auto 12px; font-size: 1.4rem;">SP</div>
          <h2 style="font-size: 1.5rem; font-weight: 800; color: var(--secondary);">Student Pulse AI</h2>
          <p style="color: var(--text-muted); font-size: 0.88rem; margin-top: 4px;">Evidence → Insight → Action</p>
          <div style="margin-top: 10px;">
            <span class="badge badge-low" style="font-size: 0.72rem;">MSE-2 Prototype Baseline</span>
          </div>
        </div>

        <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 20px;">
          <div style="font-size: 0.78rem; font-weight: 700; color: var(--secondary); margin-bottom: 6px;">
            🚀 Fast Demo Account Access (1-Click)
          </div>
          <div class="demo-pills" style="margin: 0;">
            <button class="demo-pill" id="btn-quick-demo1" title="Aarav Sharma - Rich backend evidence & high assessments">
              Demo 1 (Rich Profile)
            </button>
            <button class="demo-pill" id="btn-quick-demo2" title="Priya Patel - Sparse frontend evidence">
              Demo 2 (Sparse Profile)
            </button>
            <button class="demo-pill" id="btn-quick-demo3" title="Rohan Verma - Fresh profile without evidence">
              Demo 3 (Fresh/Empty)
            </button>
          </div>
        </div>

        <div style="display: flex; border-bottom: 1px solid var(--border-color); margin-bottom: 20px;">
          <button id="tab-login" style="flex: 1; padding: 10px; background: none; border: none; font-weight: 700; border-bottom: 2px solid var(--primary); color: var(--primary); cursor: pointer;">
            Sign In
          </button>
          <button id="tab-register" style="flex: 1; padding: 10px; background: none; border: none; font-weight: 600; color: var(--text-muted); cursor: pointer;">
            Register Account
          </button>
        </div>

        <div id="auth-alert" style="display: none;" class="alert-box alert-warning"></div>

        <!-- Login Form -->
        <form id="form-login">
          <div class="form-group">
            <label class="form-label" for="login-email">Email Address</label>
            <input type="email" id="login-email" class="form-control" required placeholder="demo1@example.com" value="demo1@example.com" />
          </div>
          <div class="form-group">
            <label class="form-label" for="login-password">Password</label>
            <input type="password" id="login-password" class="form-control" required placeholder="••••••••" value="Demo@12345" />
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 8px;">
            Sign In to Dashboard
          </button>
        </form>

        <!-- Register Form -->
        <form id="form-register" style="display: none;">
          <div class="form-group">
            <label class="form-label" for="reg-name">Full Display Name</label>
            <input type="text" id="reg-name" class="form-control" required placeholder="Student Name" />
          </div>
          <div class="form-group">
            <label class="form-label" for="reg-email">College / Personal Email</label>
            <input type="email" id="reg-email" class="form-control" required placeholder="student@kiet.edu" />
          </div>
          <div class="form-group">
            <label class="form-label" for="reg-password">Password (min 6 characters)</label>
            <input type="password" id="reg-password" class="form-control" minlength="6" required placeholder="••••••••" />
          </div>
          <div class="form-group">
            <label class="form-check">
              <input type="checkbox" id="reg-consent" required />
              <span>I consent to storing my educational evidence, assessments, and projects for personalized career readiness guidance.</span>
            </label>
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 8px;">
            Create Student Account
          </button>
        </form>

        <div style="margin-top: 24px; text-align: center; font-size: 0.75rem; color: var(--text-muted);">
          Team Byte Force • KIET AI Fundamentals & Python Programming (MSE-2)
        </div>
      </div>
    </div>
  `;

  const alertBox = container.querySelector('#auth-alert');
  const tabLogin = container.querySelector('#tab-login');
  const tabRegister = container.querySelector('#tab-register');
  const formLogin = container.querySelector('#form-login');
  const formRegister = container.querySelector('#form-register');

  const showAlert = (msg, isError = true) => {
    alertBox.style.display = 'flex';
    alertBox.className = `alert-box ${isError ? 'alert-warning' : 'alert-info'}`;
    alertBox.textContent = msg;
  };

  // Tab switching
  tabLogin.addEventListener('click', () => {
    tabLogin.style.borderBottom = '2px solid var(--primary)';
    tabLogin.style.color = 'var(--primary)';
    tabRegister.style.borderBottom = 'none';
    tabRegister.style.color = 'var(--text-muted)';
    formLogin.style.display = 'block';
    formRegister.style.display = 'none';
    alertBox.style.display = 'none';
  });

  tabRegister.addEventListener('click', () => {
    tabRegister.style.borderBottom = '2px solid var(--primary)';
    tabRegister.style.color = 'var(--primary)';
    tabLogin.style.borderBottom = 'none';
    tabLogin.style.color = 'var(--text-muted)';
    formLogin.style.display = 'none';
    formRegister.style.display = 'block';
    alertBox.style.display = 'none';
  });

  // Quick Demo Buttons
  const fillAndSubmit = (email, pass) => {
    container.querySelector('#login-email').value = email;
    container.querySelector('#login-password').value = pass;
    formLogin.dispatchEvent(new Event('submit'));
  };

  container.querySelector('#btn-quick-demo1').addEventListener('click', () => fillAndSubmit('demo1@example.com', 'Demo@12345'));
  container.querySelector('#btn-quick-demo2').addEventListener('click', () => fillAndSubmit('demo2@example.com', 'Demo@12345'));
  container.querySelector('#btn-quick-demo3').addEventListener('click', () => fillAndSubmit('demo3@example.com', 'Demo@12345'));

  // Submit Login
  formLogin.addEventListener('submit', async (e) => {
    e.preventDefault();
    alertBox.style.display = 'none';
    const email = container.querySelector('#login-email').value;
    const pass = container.querySelector('#login-password').value;
    try {
      await auth.login(email, pass);
      window.location.hash = '#dashboard';
    } catch (err) {
      showAlert(err.message || 'Login failed. Please check credentials.');
    }
  });

  // Submit Register
  formRegister.addEventListener('submit', async (e) => {
    e.preventDefault();
    alertBox.style.display = 'none';
    const name = container.querySelector('#reg-name').value;
    const email = container.querySelector('#reg-email').value;
    const pass = container.querySelector('#reg-password').value;
    const consent = container.querySelector('#reg-consent').checked;

    try {
      await auth.register(name, email, pass, consent);
      window.location.hash = '#dashboard';
    } catch (err) {
      showAlert(err.message || 'Registration failed.');
    }
  });
}
