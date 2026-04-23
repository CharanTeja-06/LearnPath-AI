import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCourses, getCategories, enrollCourse, unenrollCourse, getEnrollments } from '../api';
import { useAuth } from '../context/AuthContext';
import './CatalogPage.css';

const CATEGORY_ICONS = {
  'Web Development': '🌐', 'Data Science': '📊', 'Machine Learning': '🤖',
  'Cloud Computing': '☁️', 'DevOps': '⚙️', 'Mobile Development': '📱',
  'Cybersecurity': '🔒', 'Database': '🗄️', 'Programming Fundamentals': '💻',
  'Software Engineering': '🏗️',
};

const DIFF_COLORS = { Beginner: '#10b981', Intermediate: '#f59e0b', Advanced: '#ef4444' };

export default function CatalogPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const username = localStorage.getItem('username');

  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [enrolledMap, setEnrolledMap] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [dropConfirm, setDropConfirm] = useState(null);

  useEffect(() => { loadAll(); }, []);
  useEffect(() => {
    if (courseId && courses.length) {
      const c = courses.find(c => c.id === parseInt(courseId));
      if (c) setSelectedCourse(c);
    }
  }, [courseId, courses]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [courseRes, catRes, enrollRes] = await Promise.all([
        getCourses({}), getCategories(), getEnrollments()
      ]);
      setCourses(courseRes.data);
      setCategories(catRes.data);
      const map = {};
      enrollRes.data.forEach(e => { map[e.course_id] = e; });
      setEnrolledMap(map);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleEnroll = async (courseId) => {
    setActionLoading(courseId);
    try { await enrollCourse(courseId); await loadAll(); }
    catch (e) { console.error(e); }
    finally { setActionLoading(null); }
  };

  const handleDrop = async (courseId) => {
    setActionLoading(courseId);
    try { await unenrollCourse(courseId); setDropConfirm(null); await loadAll(); }
    catch (e) { console.error(e); }
    finally { setActionLoading(null); }
  };

  const filtered = selectedCategory
    ? courses.filter(c => c.category === selectedCategory)
    : courses;

  // Group by category
  const grouped = {};
  filtered.forEach(c => {
    if (!grouped[c.category]) grouped[c.category] = [];
    grouped[c.category].push(c);
  });
  // Sort within each category by difficulty
  const DIFF_ORDER = { Beginner: 0, Intermediate: 1, Advanced: 2 };
  Object.keys(grouped).forEach(cat => {
    grouped[cat].sort((a, b) => (DIFF_ORDER[a.difficulty] || 0) - (DIFF_ORDER[b.difficulty] || 0));
  });

  const PAGE_TITLES = {
    'Web Development': ['HTML & CSS Foundations', 'JavaScript Essentials', 'Frameworks & Libraries', 'Backend & APIs', 'Deployment & DevOps'],
    'Data Science': ['Data Exploration & Pandas', 'Statistical Analysis', 'Data Visualization', 'Feature Engineering', 'Capstone Project'],
    'Machine Learning': ['ML Fundamentals', 'Supervised Learning', 'Unsupervised & Ensemble', 'Deep Learning', 'MLOps & Deployment'],
    'Cloud Computing': ['Cloud Fundamentals', 'Compute & Networking', 'Storage & Databases', 'Security & IAM', 'Infrastructure as Code'],
    'DevOps': ['Culture & Principles', 'CI/CD Pipelines', 'Docker & Containers', 'Kubernetes', 'Monitoring & Observability'],
    'Mobile Development': ['UI/UX Principles', 'Cross-Platform', 'State & Navigation', 'APIs & Storage', 'Publishing'],
    'Cybersecurity': ['Security Fundamentals', 'Network Security', 'App Security', 'Cryptography', 'Incident Response'],
    'Database': ['Relational Design', 'SQL Mastery', 'NoSQL Databases', 'Performance', 'Replication & Sharding'],
    'Programming Fundamentals': ['Variables & Control Flow', 'Functions & Data Structures', 'OOP', 'Algorithms', 'Version Control'],
    'Software Engineering': ['SDLC', 'System Design', 'Testing & QA', 'Clean Code', 'Documentation'],
  };
  const DEFAULT_PAGES = ['Introduction', 'Core Concepts', 'Hands-On Practice', 'Advanced Topics', 'Assessment'];

  if (loading) {
    return <div className="catalog-loading"><div className="loading-spinner" /><p>Loading course catalog...</p></div>;
  }

  return (
    <div className="catalog-page">
      {/* Nav */}
      <nav className="dash-nav">
        <div className="nav-brand" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <svg viewBox="0 0 32 32" fill="none" width="32" height="32"><rect rx="6" width="32" height="32" fill="url(#catng)" /><path d="M10 24V14l6-5 6 5v10l-6 3-6-3z" fill="rgba(255,255,255,0.9)" /><path d="M16 9l6 5v10l-6 3" fill="rgba(255,255,255,0.6)" /><defs><linearGradient id="catng" x1="0" y1="0" x2="32" y2="32"><stop stopColor="#7c3aed" /><stop offset="1" stopColor="#06b6d4" /></linearGradient></defs></svg>
          <span>LearnPath AI</span>
        </div>
        <div className="nav-center-links">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>Dashboard</button>
          <button className="nav-link" onClick={() => navigate('/courses')}>Browse</button>
          <button className="nav-link active">Catalog</button>
        </div>
        <div className="nav-user">
          <div className="user-avatar">{(username || 'U')[0].toUpperCase()}</div>
          <span className="user-name">{username}</span>
          <button className="logout-btn" onClick={logout}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
          </button>
        </div>
      </nav>

      {/* Header */}
      <header className="catalog-header animate-fade-in">
        <div className="catalog-header-text">
          <h1>📖 Course Catalog</h1>
          <p>Explore {courses.length} courses across {categories.length} categories — each course has 5 structured learning modules</p>
        </div>
      </header>

      {/* Category Pills */}
      <div className="category-pills animate-fade-in">
        <button className={`cat-pill ${selectedCategory === '' ? 'active' : ''}`} onClick={() => { setSelectedCategory(''); setSelectedCourse(null); }}>
          📋 All
        </button>
        {categories.map(cat => (
          <button key={cat} className={`cat-pill ${selectedCategory === cat ? 'active' : ''}`} onClick={() => { setSelectedCategory(cat); setSelectedCourse(null); }}>
            {CATEGORY_ICONS[cat] || '📚'} {cat}
          </button>
        ))}
      </div>

      <div className="catalog-layout">
        {/* Course List */}
        <div className="catalog-list">
          {Object.entries(grouped).map(([cat, catCourses]) => (
            <div key={cat} className="catalog-category-block">
              <div className="category-block-header">
                <span className="cat-icon">{CATEGORY_ICONS[cat] || '📚'}</span>
                <h2>{cat}</h2>
                <span className="cat-count">{catCourses.length} courses</span>
              </div>
              <div className="catalog-course-list">
                {catCourses.map(course => {
                  const enrolled = enrolledMap[course.id];
                  const isSelected = selectedCourse?.id === course.id;
                  return (
                    <div
                      key={course.id}
                      className={`catalog-course-item ${isSelected ? 'selected' : ''} ${enrolled ? 'is-enrolled' : ''}`}
                      onClick={() => { setSelectedCourse(course); navigate(`/catalog/${course.id}`, { replace: true }); }}
                    >
                      <div className="cci-left">
                        <div className="cci-diff-dot" style={{ background: DIFF_COLORS[course.difficulty] }} title={course.difficulty} />
                        <div className="cci-info">
                          <h4>{course.name}</h4>
                          <div className="cci-meta">
                            <span className="cci-diff" style={{ color: DIFF_COLORS[course.difficulty] }}>{course.difficulty}</span>
                            <span className="cci-pages">·  5 modules</span>
                            {enrolled && <span className="cci-enrolled-badge">✓ Enrolled</span>}
                          </div>
                        </div>
                      </div>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="cci-arrow"><polyline points="9 18 15 12 9 6" /></svg>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Course Detail Panel */}
        <div className={`catalog-detail ${selectedCourse ? 'open' : ''}`}>
          {selectedCourse ? (
            <div className="detail-inner animate-fade-in" key={selectedCourse.id}>
              <button className="detail-close" onClick={() => { setSelectedCourse(null); navigate('/catalog', { replace: true }); }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
              </button>

              <div className="detail-badge-row">
                <span className="detail-category">{CATEGORY_ICONS[selectedCourse.category] || '📚'} {selectedCourse.category}</span>
                <span className="detail-diff" style={{ color: DIFF_COLORS[selectedCourse.difficulty], borderColor: DIFF_COLORS[selectedCourse.difficulty] }}>{selectedCourse.difficulty}</span>
              </div>

              <h2 className="detail-title">{selectedCourse.name}</h2>
              <p className="detail-desc">{selectedCourse.description}</p>

              {/* Skills */}
              {selectedCourse.skills_covered?.length > 0 && (
                <div className="detail-skills">
                  <h4>Skills You'll Learn</h4>
                  <div className="skills-wrap">
                    {selectedCourse.skills_covered.map(s => <span key={s} className="skill-chip">{s}</span>)}
                  </div>
                </div>
              )}

              {/* 5 Pages Preview */}
              <div className="detail-modules">
                <h4>📄 5 Course Modules</h4>
                <div className="module-list">
                  {(PAGE_TITLES[selectedCourse.category] || DEFAULT_PAGES).map((title, i) => {
                    const enrollment = enrolledMap[selectedCourse.id];
                    const isCompleted = false; // We don't have page-level detail here
                    return (
                      <div key={i} className="module-item">
                        <div className="module-num">{i + 1}</div>
                        <div className="module-info">
                          <span className="module-title">{title}</span>
                          <span className="module-type">{i === 0 ? 'Foundation' : i === 4 ? 'Assessment' : 'Core Module'}</span>
                        </div>
                        {enrollment && (
                          <div className="module-status">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Rating */}
              {selectedCourse.avg_rating && (
                <div className="detail-rating-block">
                  <span className="detail-stars">{'★'.repeat(Math.round(selectedCourse.avg_rating))}{'☆'.repeat(5 - Math.round(selectedCourse.avg_rating))}</span>
                  <span className="detail-rating-num">{selectedCourse.avg_rating.toFixed(1)} / 5.0</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="detail-actions">
                {enrolledMap[selectedCourse.id] ? (
                  <>
                    <button className="detail-btn primary" onClick={() => navigate(`/learn/${selectedCourse.id}`)}>
                      📖 Continue Learning
                    </button>
                    <button className="detail-btn danger" onClick={() => setDropConfirm(selectedCourse.id)}>
                      🗑️ Drop Course
                    </button>
                  </>
                ) : (
                  <button className="detail-btn primary full" onClick={() => handleEnroll(selectedCourse.id)} disabled={actionLoading === selectedCourse.id}>
                    {actionLoading === selectedCourse.id ? <span className="spinner" /> : '📘 Enroll in Course'}
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="detail-empty">
              <div className="detail-empty-icon">📖</div>
              <h3>Select a Course</h3>
              <p>Click any course from the list to view its details, modules, and enrollment options.</p>
            </div>
          )}
        </div>
      </div>

      {/* Drop Confirmation Modal */}
      {dropConfirm && (
        <div className="modal-overlay" onClick={() => setDropConfirm(null)}>
          <div className="modal drop-modal" onClick={e => e.stopPropagation()}>
            <div className="drop-icon">⚠️</div>
            <h3>Drop this course?</h3>
            <p className="modal-subtitle">This will remove your enrollment and all progress. This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-cancel" onClick={() => setDropConfirm(null)}>Cancel</button>
              <button className="modal-submit danger-submit" onClick={() => handleDrop(dropConfirm)} disabled={actionLoading === dropConfirm}>
                {actionLoading === dropConfirm ? <span className="spinner" /> : 'Yes, Drop Course'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
