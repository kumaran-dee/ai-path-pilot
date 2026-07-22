import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Resume API
export const uploadResume = (formData) => api.post('/resume/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
export const getResumeDetails = () => api.get('/resume/details');

// Opportunity API
export const getOpportunities = () => api.get('/opportunity/match');

// Dashboard API
export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getLinks = () => api.get('/dashboard/links');
export const updateLinks = (data) => api.post('/dashboard/links', data);
export const scanProfile = () => api.post('/dashboard/scan');

// Skill Gap API
export const getSkillGapAnalysis = () => api.get('/skill_gap/analyze');

// Roadmap API
export const getLearningRoadmap = (data) => api.post('/roadmap/generate', data);

// Chat API
export const sendChatMessage = (message) => api.post('/chat/message', { message });

// Compare API
export const compareResumeToJob = (formData) => api.post('/compare/match', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export default api;
