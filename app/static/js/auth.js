import { api } from './api.js';

export const auth = {
  getStudent() {
    try {
      const raw = localStorage.getItem('spa_student');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setSession(data) {
    if (data && data.access_token) {
      api.setToken(data.access_token);
      localStorage.setItem('spa_student', JSON.stringify({
        student_id: data.student_id,
        display_name: data.display_name,
        email: data.email
      }));
    }
  },

  clearSession() {
    api.setToken(null);
    localStorage.removeItem('spa_student');
  },

  isAuthenticated() {
    return !!api.getToken();
  },

  async login(email, password) {
    const data = await api.post('/auth/login', { email, password });
    this.setSession(data);
    return data;
  },

  async register(displayName, email, password, consentGiven) {
    const data = await api.post('/auth/register', {
      display_name: displayName,
      email,
      password,
      consent_given: consentGiven
    });
    this.setSession(data);
    return data;
  },

  logout() {
    this.clearSession();
    window.location.hash = '#login';
  }
};
