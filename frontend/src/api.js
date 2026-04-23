import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const signup = (data) => api.post('/signup', data);
export const login = (data) => api.post('/login', data);
export const getProfile = () => api.get('/profile');
export const getCourses = (params) => api.get('/courses', { params });
export const getCategories = () => api.get('/categories');
export const getRecommendations = (userId) => api.get(`/recommendations/${userId}`);
export const rateCourse = (courseId, rating) => api.post('/rate-course', { course_id: courseId, rating });
export const getUserStats = (userId) => api.get(`/user-stats/${userId}`);
export const getEvaluation = () => api.get('/evaluation');

// Enrollment & Progress
export const enrollCourse = (courseId) => api.post('/enroll', { course_id: courseId });
export const unenrollCourse = (courseId) => api.delete(`/unenroll/${courseId}`);
export const getEnrollments = () => api.get('/enrollments');
export const getCourseContent = (courseId) => api.get(`/course-content/${courseId}`);
export const completePage = (courseId, pageNumber) => api.post('/complete-page', { course_id: courseId, page_number: pageNumber });

export default api;
