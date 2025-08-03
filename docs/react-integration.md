# React Frontend Integration Guide

This document provides examples and configuration for integrating the Interview Scheduling API with a React frontend.

## API Endpoints Overview

### Base URL: `http://localhost:8000`

### Authentication & CORS
- CORS is configured for `localhost:3000` (React dev server)
- All endpoints use JSON for request/response
- Standard HTTP status codes for error handling

## React API Client Configuration

### 1. Install Dependencies
```bash
npm install axios
# or
npm install fetch
```

### 2. API Client Setup (`src/api/client.js`)
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', error.response?.data || error.message);
    
    // Handle common error scenarios
    if (error.response?.status === 401) {
      // Handle authentication errors
      console.log('Unauthorized access');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.log('Server error occurred');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 3. API Service Functions (`src/api/services.js`)
```javascript
import apiClient from './client';

// Users API
export const usersAPI = {
  getAll: (params = {}) => apiClient.get('/api/users/', { params }),
  getById: (id) => apiClient.get(`/api/users/${id}`),
  create: (userData) => apiClient.post('/api/users/', userData),
  update: (id, userData) => apiClient.put(`/api/users/${id}`, userData),
  delete: (id) => apiClient.delete(`/api/users/${id}`),
};

// Candidates API
export const candidatesAPI = {
  getAll: (params = {}) => apiClient.get('/api/candidates/', { params }),
  getById: (id) => apiClient.get(`/api/candidates/${id}`),
  create: (candidateData) => apiClient.post('/api/candidates/', candidateData),
  update: (id, candidateData) => apiClient.put(`/api/candidates/${id}`, candidateData),
  delete: (id) => apiClient.delete(`/api/candidates/${id}`),
};

// Interviews API
export const interviewsAPI = {
  getAll: (params = {}) => apiClient.get('/api/interviews/', { params }),
  getById: (id) => apiClient.get(`/api/interviews/${id}`),
  create: (interviewData) => apiClient.post('/api/interviews/', interviewData),
  update: (id, interviewData) => apiClient.put(`/api/interviews/${id}`, interviewData),
  updateStatus: (id, status, feedback, score) => 
    apiClient.patch(`/api/interviews/${id}/status`, null, {
      params: { new_status: status, feedback, score }
    }),
};

// Dashboard & Analytics API
export const analyticsAPI = {
  getStats: () => apiClient.get('/api/stats'),
  getDashboard: () => apiClient.get('/api/dashboard'),
  search: (query, entityType) => 
    apiClient.get('/api/search', { params: { q: query, entity_type: entityType } }),
};

// Health Check
export const healthAPI = {
  check: () => apiClient.get('/health'),
  getInfo: () => apiClient.get('/'),
};
```

### 4. React Hooks for API Integration (`src/hooks/useAPI.js`)
```javascript
import { useState, useEffect } from 'react';

// Generic API hook
export const useAPI = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiFunction();
        setData(response.data);
      } catch (err) {
        setError(err.response?.data || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error, refetch: fetchData };
};

// Specific hooks for different entities
export const useUsers = (params) => {
  return useAPI(() => usersAPI.getAll(params), [JSON.stringify(params)]);
};

export const useCandidates = (params) => {
  return useAPI(() => candidatesAPI.getAll(params), [JSON.stringify(params)]);
};

export const useInterviews = (params) => {
  return useAPI(() => interviewsAPI.getAll(params), [JSON.stringify(params)]);
};

export const useDashboard = () => {
  return useAPI(() => analyticsAPI.getDashboard(), []);
};
```

### 5. React Components Examples

#### Dashboard Component (`src/components/Dashboard.js`)
```javascript
import React from 'react';
import { useDashboard } from '../hooks/useAPI';

const Dashboard = () => {
  const { data: dashboardData, loading, error } = useDashboard();

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error: {error.message || 'Failed to load dashboard'}</div>;

  return (
    <div className="dashboard">
      <h1>Interview Scheduling Dashboard</h1>
      
      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-card">
          <h3>Today's Interviews</h3>
          <p>{dashboardData?.quick_stats?.total_interviews_today || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Pending Interviews</h3>
          <p>{dashboardData?.quick_stats?.pending_interviews || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Completed This Week</h3>
          <p>{dashboardData?.quick_stats?.completed_interviews_this_week || 0}</p>
        </div>
      </div>

      {/* Upcoming Interviews */}
      <div className="upcoming-interviews">
        <h2>Upcoming Interviews</h2>
        {dashboardData?.upcoming_interviews?.map(interview => (
          <div key={interview.id} className="interview-card">
            <h4>{interview.candidate_name}</h4>
            <p>Interviewer: {interview.interviewer_name}</p>
            <p>Time: {new Date(interview.scheduled_time).toLocaleString()}</p>
            <p>Type: {interview.type}</p>
          </div>
        ))}
      </div>

      {/* Recent Candidates */}
      <div className="recent-candidates">
        <h2>Recent Candidates</h2>
        {dashboardData?.recent_candidates?.map(candidate => (
          <div key={candidate.id} className="candidate-card">
            <h4>{candidate.name}</h4>
            <p>Position: {candidate.position}</p>
            <p>AI Score: {candidate.ai_score}/10</p>
            <p>Added: {new Date(candidate.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
```

#### Interview Form Component (`src/components/InterviewForm.js`)
```javascript
import React, { useState } from 'react';
import { interviewsAPI } from '../api/services';

const InterviewForm = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    candidate_id: '',
    interviewer_id: '',
    scheduled_time: '',
    duration: 60,
    type: 'technical',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await interviewsAPI.create({
        ...formData,
        scheduled_time: new Date(formData.scheduled_time).toISOString()
      });
      
      console.log('Interview scheduled:', response.data);
      onSuccess?.(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to schedule interview');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form onSubmit={handleSubmit} className="interview-form">
      <h2>Schedule Interview</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="form-group">
        <label>Candidate ID:</label>
        <input
          type="number"
          name="candidate_id"
          value={formData.candidate_id}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label>Interviewer ID:</label>
        <input
          type="number"
          name="interviewer_id"
          value={formData.interviewer_id}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label>Scheduled Time:</label>
        <input
          type="datetime-local"
          name="scheduled_time"
          value={formData.scheduled_time}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label>Duration (minutes):</label>
        <input
          type="number"
          name="duration"
          value={formData.duration}
          onChange={handleChange}
          min="15"
          max="480"
        />
      </div>

      <div className="form-group">
        <label>Interview Type:</label>
        <select name="type" value={formData.type} onChange={handleChange}>
          <option value="technical">Technical</option>
          <option value="behavioral">Behavioral</option>
          <option value="cultural_fit">Cultural Fit</option>
          <option value="final">Final</option>
          <option value="phone_screening">Phone Screening</option>
        </select>
      </div>

      <div className="form-group">
        <label>Notes:</label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows="3"
        />
      </div>

      <div className="form-actions">
        <button type="submit" disabled={loading}>
          {loading ? 'Scheduling...' : 'Schedule Interview'}
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
};

export default InterviewForm;
```

## Environment Configuration

### `.env` file for React app:
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

## Error Handling Best Practices

1. **Network Errors**: Check if API server is running
2. **Validation Errors**: Display field-specific error messages
3. **Authentication Errors**: Redirect to login page
4. **Server Errors**: Show user-friendly error messages

## Testing API Integration

```javascript
// Example test for API client
import { usersAPI } from '../api/services';

describe('Users API', () => {
  test('should fetch all users', async () => {
    const response = await usersAPI.getAll();
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
  });

  test('should create new user', async () => {
    const newUser = {
      email: 'test@example.com',
      name: 'Test User',
      role: 'interviewer'
    };
    
    const response = await usersAPI.create(newUser);
    expect(response.status).toBe(201);
    expect(response.data.email).toBe(newUser.email);
  });
});
```

This configuration provides a complete foundation for integrating the FastAPI backend with a React frontend, including proper error handling, loading states, and CORS support.
