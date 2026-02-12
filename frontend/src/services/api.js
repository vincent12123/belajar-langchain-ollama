import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API
export const chatWithAI = async (message, model = null) => {
  try {
    const response = await api.post('/chat', { query: message, model });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to chat with AI');
  }
};

// Attendance Trends API
export const getAttendanceTrends = async (params) => {
  try {
    const response = await api.post('/api/attendance/trends', params);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get attendance trends');
  }
};

// Geolocation Analysis API
export const getGeolocationAnalysis = async (params) => {
  try {
    const response = await api.post('/api/geolocation/analysis', params);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get geolocation analysis');
  }
};

// Class Comparison API
export const getClassComparison = async (params) => {
  try {
    const response = await api.post('/api/class/comparison', params);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get class comparison');
  }
};

// Student Search API
export const searchStudents = async (name) => {
  try {
    const response = await api.get(`/api/students/search?name=${encodeURIComponent(name)}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to search students');
  }
};

// Student Attendance API
export const getStudentAttendance = async (studentId, startDate = null, endDate = null) => {
  try {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;

    const response = await api.get(`/api/students/${studentId}/attendance`, { params });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get student attendance');
  }
};

export default api;