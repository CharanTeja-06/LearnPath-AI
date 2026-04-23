import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCourseContent, completePage } from '../api';
import { useAuth } from '../context/AuthContext';
import './CourseLearning.css';

export default function CourseLearning() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [course, setCourse] = useState(null);
  const [activePage, setActivePage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const username = localStorage.getItem('username');

  useEffect(() => { loadContent(); }, [courseId]);

  const loadContent = async () => {
    setLoading(true);
    try {
      const res = await getCourseContent(courseId);
      setCourse(res.data);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 403) navigate('/courses');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (pageNum) => {
    setCompleting(true);
    try {
      await completePage(courseId, pageNum);
      await loadContent();
      // Auto advance to next page
      if (pageNum < (course?.total_pages || 5)) setActivePage(pageNum + 1);
    } catch (err) {
      console.error(err);
    } finally {
      setCompleting(false);
    }
  };

  if (loading) {
    return (
      <div className="cl-loading">
        <div className="loading-spinner" />
        <p>Loading course content...</p>
      </div>
    );
  }

  if (!course) return null;

  const currentPage = course.pages.find(p => p.page_number === activePage);
  const allCompleted = course.completed_pages === course.total_pages;

  const getDiffColor = (d) => d === 'Beginner' ? '#10b981' : d === 'Intermediate' ? '#f59e0b' : '#ef4444';

  return (
    <div className="course-learning">
      {/* Nav */}
      <nav className="cl-nav">
        <div className="nav-brand" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <svg viewBox="0 0 32 32" fill="none" width="32" height="32">
            <rect rx="6" width="32" height="32" fill="url(#clng)" />
            <path d="M10 24V14l6-5 6 5v10l-6 3-6-3z" fill="rgba(255,255,255,0.9)" />
            <path d="M16 9l6 5v10l-6 3" fill="rgba(255,255,255,0.6)" />
            <defs><linearGradient id="clng" x1="0" y1="0" x2="32" y2="32"><stop stopColor="#7c3aed" /><stop offset="1" stopColor="#06b6d4" /></linearGradient></defs>
          </svg>
          <span>LearnPath AI</span>
        </div>
        <div className="cl-nav-center">
          <button className="nav-back" onClick={() => navigate('/courses')}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6" /></svg>
            Back to Courses
          </button>
        </div>
        <div className="nav-user">
          <div className="user-avatar">{(username || 'U')[0].toUpperCase()}</div>
          <span className="user-name">{username}</span>
        </div>
      </nav>

      {/* Course Header */}
      <header className="cl-header animate-fade-in">
        <div className="cl-header-left">
          <div className="cl-tags">
            <span className="tag category-tag">{course.category}</span>
            <span className="tag" style={{ color: getDiffColor(course.difficulty), borderColor: getDiffColor(course.difficulty), border: '1px solid' }}>
              {course.difficulty}
            </span>
          </div>
          <h1>{course.course_name}</h1>
          <p className="cl-desc">{course.description}</p>
        </div>
        <div className="cl-progress-ring">
          <svg viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
            <circle cx="60" cy="60" r="52" fill="none" stroke="url(#prog-gradient)" strokeWidth="8"
              strokeLinecap="round" strokeDasharray={`${2 * Math.PI * 52}`}
              strokeDashoffset={`${2 * Math.PI * 52 * (1 - course.progress_percent / 100)}`}
              transform="rotate(-90 60 60)" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
            <defs><linearGradient id="prog-gradient" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#7c3aed" /><stop offset="1" stopColor="#06b6d4" /></linearGradient></defs>
          </svg>
          <div className="ring-text">
            <span className="ring-value">{Math.round(course.progress_percent)}%</span>
            <span className="ring-label">Complete</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="cl-body">
        {/* Sidebar - Page List */}
        <aside className="cl-sidebar">
          <h3>Course Modules</h3>
          <div className="cl-page-list">
            {course.pages.map((page) => (
              <button
                key={page.page_number}
                className={`cl-page-item ${activePage === page.page_number ? 'active' : ''} ${page.completed ? 'completed' : ''}`}
                onClick={() => setActivePage(page.page_number)}
              >
                <div className="page-status">
                  {page.completed ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                  ) : (
                    <span className="page-num">{page.page_number}</span>
                  )}
                </div>
                <div className="page-info">
                  <span className="page-title">{page.title}</span>
                  <span className="page-meta">{page.completed ? 'Completed' : 'Not started'}</span>
                </div>
              </button>
            ))}
          </div>
          {/* Overall progress bar */}
          <div className="cl-sidebar-progress">
            <div className="progress-header">
              <span>Progress</span>
              <span>{course.completed_pages}/{course.total_pages}</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${course.progress_percent}%` }} />
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <main className="cl-content animate-fade-in">
          {currentPage && (
            <>
              <div className="content-header">
                <span className="content-badge">Module {currentPage.page_number} of {course.total_pages}</span>
                <h2>{currentPage.title}</h2>
              </div>

              <div className="content-body">
                <p className="content-text">{currentPage.content}</p>

                <div className="content-placeholder-sections">
                  <div className="placeholder-section">
                    <div className="placeholder-icon">📖</div>
                    <h4>Learning Material</h4>
                    <div className="placeholder-lines">
                      <div className="ph-line" style={{width:'100%'}} /><div className="ph-line" style={{width:'90%'}} />
                      <div className="ph-line" style={{width:'95%'}} /><div className="ph-line" style={{width:'80%'}} />
                      <div className="ph-line" style={{width:'85%'}} />
                    </div>
                  </div>

                  <div className="placeholder-section">
                    <div className="placeholder-icon">💻</div>
                    <h4>Code Examples</h4>
                    <div className="code-block">
                      <code>{`# ${course.course_name} - Module ${currentPage.page_number}\n# ${currentPage.title}\n\n# Practice exercises will appear here\n# Complete this module to unlock the next one`}</code>
                    </div>
                  </div>

                  <div className="placeholder-section">
                    <div className="placeholder-icon">📝</div>
                    <h4>Key Takeaways</h4>
                    <ul className="takeaway-list">
                      <li>Understand the core concepts of {currentPage.title.toLowerCase()}</li>
                      <li>Apply techniques from {course.category}</li>
                      <li>Build upon {course.difficulty.toLowerCase()}-level knowledge</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="content-footer">
                {activePage > 1 && (
                  <button className="cl-btn secondary" onClick={() => setActivePage(activePage - 1)}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6" /></svg>
                    Previous
                  </button>
                )}
                <div style={{flex: 1}} />
                {currentPage.completed ? (
                  activePage < course.total_pages ? (
                    <button className="cl-btn primary" onClick={() => setActivePage(activePage + 1)}>
                      Next Module
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
                    </button>
                  ) : (
                    <div className="completed-badge">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                      Course Completed!
                    </div>
                  )
                ) : (
                  <button className="cl-btn primary" onClick={() => handleComplete(currentPage.page_number)} disabled={completing}>
                    {completing ? <span className="spinner" /> : 'Mark as Complete'}
                    {!completing && <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>}
                  </button>
                )}
              </div>
            </>
          )}

          {allCompleted && (
            <div className="course-complete-banner">
              <div className="complete-icon">🎉</div>
              <h3>Congratulations!</h3>
              <p>You've completed all modules in <strong>{course.course_name}</strong>.</p>
              <button className="cl-btn primary" onClick={() => navigate('/courses')}>Explore More Courses</button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
