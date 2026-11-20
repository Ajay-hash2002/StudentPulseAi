import { auth } from './auth.js';
import { renderLoginPage } from './pages/login.js';
import { renderDashboard } from './pages/dashboard.js';
import { renderProfile } from './pages/profile.js';
import { renderAssessments } from './pages/assessments.js';
import { renderSkillGaps } from './pages/skill_gaps.js';
import { renderProjectReadiness } from './pages/project_readiness.js';
import { renderInterviewReadiness } from './pages/interview_readiness.js';
import { renderActionPlan } from './pages/action_plan.js';
import { renderPrivacy } from './pages/privacy.js';

const routes = {
  '#login': { title: 'Sign In', render: renderLoginPage, isPublic: true },
  '#dashboard': { title: 'Student Dashboard', render: renderDashboard },
  '#profile': { title: 'Unified Student Profile', render: renderProfile },
  '#assessments': { title: 'Assessment Analysis', render: renderAssessments },
  '#skill-gaps': { title: 'Skill-Gap Matrix', render: renderSkillGaps },
  '#project-readiness': { title: 'Project Readiness', render: renderProjectReadiness },
  '#interview-readiness': { title: 'Interview Readiness', render: renderInterviewReadiness },
  '#action-plan': { title: 'Personalised Action Plan', render: renderActionPlan },
  '#privacy': { title: 'Profile & Privacy Settings', render: renderPrivacy }
};

export class Router {
  constructor() {
    this.container = document.getElementById('content-area');
    this.pageTitle = document.getElementById('page-title');
    this.sidebar = document.getElementById('sidebar');
    this.topNavbar = document.getElementById('top-navbar');
    this.demoBanner = document.getElementById('demo-banner');

    window.addEventListener('hashchange', () => this.handleRoute());
  }

  init() {
    if (!window.location.hash) {
      window.location.hash = auth.isAuthenticated() ? '#dashboard' : '#login';
    } else {
      this.handleRoute();
    }
  }

  handleRoute() {
    let hash = window.location.hash || '#login';
    const isAuth = auth.isAuthenticated();

    if (!isAuth && hash !== '#login') {
      window.location.hash = '#login';
      return;
    }

    if (isAuth && hash === '#login') {
      window.location.hash = '#dashboard';
      return;
    }

    const route = routes[hash] || routes['#dashboard'];

    // Toggle navigation UI visibility based on auth
    if (hash === '#login') {
      this.sidebar.style.display = 'none';
      this.topNavbar.style.display = 'none';
    } else {
      this.sidebar.style.display = 'flex';
      this.topNavbar.style.display = 'flex';
      this.updateSidebarUser();
      this.highlightNav(hash);
    }

    if (this.pageTitle) {
      this.pageTitle.textContent = route.title;
    }

    // Scroll top
    window.scrollTo(0, 0);

    // Render page
    route.render(this.container);
  }

  highlightNav(hash) {
    document.querySelectorAll('.nav-item').forEach(el => {
      if (el.getAttribute('href') === hash) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });
  }

  updateSidebarUser() {
    const student = auth.getStudent();
    if (!student) return;

    const nameEl = document.getElementById('sidebar-user-name');
    const avatarEl = document.getElementById('sidebar-user-avatar');

    if (nameEl) nameEl.textContent = student.display_name || 'Student';
    if (avatarEl) {
      const initials = (student.display_name || 'SP')
        .split(' ')
        .map(n => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase();
      avatarEl.textContent = initials;
    }
  }
}
