import { useState, useEffect } from 'react';
import { getCourses, getCategories, rateCourse, enrollCourse, unenrollCourse, getEnrollments } from '../api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './CoursesPage.css';

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [enrolledIds, setEnrolledIds] = useState(new Set());
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [loading, setLoading] = useState(true);
  const [ratingModal, setRatingModal] = useState(null);
  const [selectedRating, setSelectedRating] = useState(0);
  const [ratingLoading, setRatingLoading] = useState(false);
  const [enrollingId, setEnrollingId] = useState(null);
  const [dropConfirm, setDropConfirm] = useState(null);
  const [droppingId, setDroppingId] = useState(null);
  const { logout } = useAuth();
  const navigate = useNavigate();
  const username = localStorage.getItem('username');

  useEffect(() => { loadCategories(); loadEnrollments(); loadCourses(); }, []);
  useEffect(() => { const t = setTimeout(() => loadCourses(), 300); return () => clearTimeout(t); }, [search, category, difficulty]);

  const loadCategories = async () => { try { setCategories((await getCategories()).data); } catch (e) { console.error(e); } };
  const loadEnrollments = async () => { try { const res = await getEnrollments(); setEnrolledIds(new Set(res.data.map(e => e.course_id))); } catch (e) { console.error(e); } };

  const loadCourses = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (category) params.category = category;
      if (difficulty) params.difficulty = difficulty;
      setCourses((await getCourses(params)).data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleRate = async () => {
    if (!ratingModal || selectedRating === 0) return;
    setRatingLoading(true);
    try { await rateCourse(ratingModal.id, selectedRating); setRatingModal(null); setSelectedRating(0); await loadCourses(); }
    catch (e) { console.error(e); }
    finally { setRatingLoading(false); }
  };

  const handleEnroll = async (courseId) => {
    setEnrollingId(courseId);
    try { await enrollCourse(courseId); await loadEnrollments(); }
    catch (e) { console.error(e); }
    finally { setEnrollingId(null); }
  };

  const handleDrop = async (courseId) => {
    setDroppingId(courseId);
    try { await unenrollCourse(courseId); setDropConfirm(null); await loadEnrollments(); }
    catch (e) { console.error(e); }
    finally { setDroppingId(null); }
  };

  const getDiffColor = (d) => d === 'Beginner' ? '#10b981' : d === 'Intermediate' ? '#f59e0b' : '#ef4444';

  return (
    <div className="courses-page">
      <nav className="dash-nav">
        <div className="nav-brand" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <svg viewBox="0 0 32 32" fill="none" width="32" height="32"><rect rx="6" width="32" height="32" fill="url(#cng)" /><path d="M10 24V14l6-5 6 5v10l-6 3-6-3z" fill="rgba(255,255,255,0.9)" /><path d="M16 9l6 5v10l-6 3" fill="rgba(255,255,255,0.6)" /><defs><linearGradient id="cng" x1="0" y1="0" x2="32" y2="32"><stop stopColor="#7c3aed" /><stop offset="1" stopColor="#06b6d4" /></linearGradient></defs></svg>
          <span>LearnPath AI</span>
        </div>
        <div className="nav-center-links">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>Dashboard</button>
          <button className="nav-link active">Browse</button>
          <button className="nav-link" onClick={() => navigate('/catalog')}>Catalog</button>
        </div>
        <div className="nav-user">
          <div className="user-avatar">{(username || 'U')[0].toUpperCase()}</div>
          <span className="user-name">{username}</span>
          <button className="logout-btn" onClick={logout}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
          </button>
        </div>
      </nav>

      <div className="courses-header animate-fade-in">
        <h1>📚 Browse Courses</h1>
        <p>Browse all {courses.length} courses — enroll, drop, and track your progress</p>
        <div className="filters">
          <div className="search-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
            <input type="text" placeholder="Search courses..." value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All Categories</option>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="">All Levels</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="dash-loading" style={{ minHeight: '300px' }}><div className="loading-spinner" /></div>
      ) : (
        <div className="course-grid stagger">
          {courses.map((course) => {
            const isEnrolled = enrolledIds.has(course.id);
            return (
              <div className="course-card" key={course.id}>
                <div className="course-card-top">
                  <span className="course-category">{course.category}</span>
                  <span className="course-difficulty" style={{ color: getDiffColor(course.difficulty), borderColor: getDiffColor(course.difficulty) }}>{course.difficulty}</span>
                </div>
                <h3>{course.name}</h3>
                <p className="course-desc">{course.description}</p>
                <div className="course-skills">
                  {course.skills_covered.slice(0, 4).map((s) => <span className="skill-chip" key={s}>{s}</span>)}
                  {course.skills_covered.length > 4 && <span className="skill-chip more">+{course.skills_covered.length - 4}</span>}
                </div>
                <div className="course-module-count">
                  <span>📄 5 modules</span>
                </div>
                <div className="course-footer">
                  <div className="course-rating">
                    {course.avg_rating ? (
                      <><span className="stars">{'★'.repeat(Math.round(course.avg_rating))}{'☆'.repeat(5 - Math.round(course.avg_rating))}</span><span className="rating-num">{course.avg_rating.toFixed(1)}</span></>
                    ) : <span className="no-rating">No ratings</span>}
                  </div>
                  <div className="course-btns">
                    <button className="rate-btn-sm" onClick={() => { setRatingModal(course); setSelectedRating(0); }}>⭐ Rate</button>
                    {isEnrolled ? (
                      <>
                        <button className="enroll-btn-sm enrolled" onClick={() => navigate(`/learn/${course.id}`)}>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                          Learn
                        </button>
                        <button className="drop-btn-sm" onClick={() => setDropConfirm(course.id)} title="Drop course">🗑️</button>
                      </>
                    ) : (
                      <button className="enroll-btn-sm" onClick={() => handleEnroll(course.id)} disabled={enrollingId === course.id}>
                        {enrollingId === course.id ? '...' : '📘 Enroll'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!loading && courses.length === 0 && <div className="empty-state" style={{ margin: '0 32px' }}><p>No courses found.</p></div>}

      {ratingModal && (
        <div className="modal-overlay" onClick={() => setRatingModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Rate: {ratingModal.name}</h3>
            <p className="modal-subtitle">How would you rate this course?</p>
            <div className="star-picker">{[1, 2, 3, 4, 5].map((s) => <button key={s} className={`star ${selectedRating >= s ? 'filled' : ''}`} onClick={() => setSelectedRating(s)}>★</button>)}</div>
            {selectedRating > 0 && <p className="rating-label">{['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent'][selectedRating]}</p>}
            <div className="modal-actions">
              <button className="modal-cancel" onClick={() => setRatingModal(null)}>Cancel</button>
              <button className="modal-submit" onClick={handleRate} disabled={selectedRating === 0 || ratingLoading}>{ratingLoading ? <span className="spinner" /> : 'Submit'}</button>
            </div>
          </div>
        </div>
      )}

      {dropConfirm && (
        <div className="modal-overlay" onClick={() => setDropConfirm(null)}>
          <div className="modal drop-modal" onClick={(e) => e.stopPropagation()}>
            <div className="drop-icon">⚠️</div>
            <h3>Drop this course?</h3>
            <p className="modal-subtitle">All progress will be lost. This cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-cancel" onClick={() => setDropConfirm(null)}>Cancel</button>
              <button className="modal-submit danger-submit" onClick={() => handleDrop(dropConfirm)} disabled={droppingId === dropConfirm}>
                {droppingId === dropConfirm ? <span className="spinner" /> : 'Yes, Drop'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
