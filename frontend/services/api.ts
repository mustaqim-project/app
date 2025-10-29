import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

const BACKEND_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL || '';

const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('user_id');
      // Navigation will be handled by AuthContext
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  register: (data: any) => api.post('/auth/register', data),
  login: (data: any) => api.post('/auth/login', data),
  verifyFace: (selfie: string) => api.post('/auth/verify-face', { selfie_photo: selfie }),
};

// Assessment API
export const assessmentAPI = {
  getQuestions: (testType: string) => api.get(`/assessment/questions/${testType}`),
  submitAnswers: (testType: string, answers: number[]) => api.post('/assessment/submit', { test_type: testType, answers }),
  getStatus: () => api.get('/assessment/status'),
};

// Discovery API
export const discoveryAPI = {
  getUsers: (radius: number, page: number) => api.get(`/discover?radius=${radius}&page=${page}`),
  likeUser: (userId: string) => api.post('/like', { target_user_id: userId }),
  getMatches: () => api.get('/matches'),
};

// Chat API
export const chatAPI = {
  getMessages: (matchId: string, page: number) => api.get(`/chat/${matchId}/messages?page=${page}`),
  sendMessage: (matchId: string, content: string, type: string = 'text') => api.post(`/chat/${matchId}/messages`, { match_id: matchId, content, message_type: type }),
};

// Feed API
export const feedAPI = {
  getFeeds: (page: number) => api.get(`/feeds?page=${page}`),
  createFeed: (content: string, images: string[]) => api.post('/feeds', { content, images }),
};

// Profile API
export const profileAPI = {
  getMyProfile: () => api.get('/profile'),
  getUserProfile: (userId: string) => api.get(`/profile/${userId}`),
};

// Consultation API
export const consultationAPI = {
  getCounselors: () => api.get('/consultations'),
  bookConsultation: (data: any) => api.post('/consultations/book', data),
};

// Report API
export const reportAPI = {
  report: (targetType: string, targetId: string, reason: string) => api.post('/report', { target_type: targetType, target_id: targetId, reason }),
  blockUser: (userId: string) => api.post(`/block/${userId}`),
};