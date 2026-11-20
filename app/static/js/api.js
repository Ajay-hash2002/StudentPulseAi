// Central API Client for Student Pulse AI

class ApiClient {
  constructor() {
    this.baseUrl = '/api/v1';
  }

  getToken() {
    return localStorage.getItem('spa_token');
  }

  setToken(token) {
    if (token) {
      localStorage.setItem('spa_token', token);
    } else {
      localStorage.removeItem('spa_token');
    }
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401 && !endpoint.startsWith('/auth/')) {
        this.setToken(null);
        window.location.hash = '#login';
        throw new Error('Session expired. Please log in again.');
      }

      const resJson = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = resJson?.error?.message || `Request failed with status ${response.status}`;
        const err = new Error(errorMsg);
        err.status = response.status;
        err.code = resJson?.error?.code || 'UNKNOWN_ERROR';
        throw err;
      }

      if (resJson && resJson.success === false) {
        const err = new Error(resJson.error?.message || 'Operation failed');
        err.code = resJson.error?.code || 'OPERATION_FAILED';
        throw err;
      }

      return resJson?.data;
    } catch (error) {
      console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, error);
      throw error;
    }
  }

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  patch(endpoint, body) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body)
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

export const api = new ApiClient();
