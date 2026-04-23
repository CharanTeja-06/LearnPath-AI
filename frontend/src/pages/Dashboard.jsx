import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getRecommendations, getUserStats, rateCourse, enrollCourse, unenrollCourse, getEnrollments } from '../api';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from 'recharts';
import './Dashboard.css';

const COLORS = ['#7c3aed', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#ec4899', '#8b5cf6', '#14b8a6'];
const DIFF_ORDER = { Beginner: 0, Intermediate: 1, Advanced: 2 };

export default function Dashboard() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [recs, setRecs] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [stats, setStats] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ratingModal, setRatingModal] = useState(null);
  const [selectedRating, setSelectedRating] = useState(0);
  const [ratingLoading, setRatingLoading] = useState(false);
  const [enrollingId, setEnrollingId] = useState(null);
  const [droppingId, setDroppingId] = useState(null);
  const [dropConfirm, setDropConfirm] = useState(null);
  const [activeTab, setActiveTab] = useState('recommendations');
  const [expandedRec, setExpandedRec] = useState(null);

  const userId = localStorage.getItem('user_id');
  const username = localStorage.getItem('username');

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [recRes, statRes, enrollRes] = await Promise.all([
        getRecommendations(userId),
        getUserStats(userId),
        getEnrollments(),
      ]);
      setRecs(recRes.data.recommendations);
      setModelInfo(recRes.data.model_info);
      setStats(statRes.data);
      setEnrollments(enrollRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async () => {
    if (!ratingModal || selectedRating === 0) return;
    setRatingLoading(true);
    try {
      await rateCourse(ratingModal.course_id, selectedRating);
      setRatingModal(null); setSelectedRating(0);
      await loadData();
    } catch (err) { console.error(err); }
    finally { setRatingLoading(false); }
  };

  const handleEnroll = async (courseId) => {
    setEnrollingId(courseId);
    try {
      await enrollCourse(courseId);
      await loadData();
    } catch (err) { console.error(err); }
    finally { setEnrollingId(null); }
  };

  const handleDrop = async (courseId) => {
    setDroppingId(courseId);
    try {
      await unenrollCourse(courseId);
      setDropConfirm(null);
      await loadData();
    } catch (err) { console.error(err); }
    finally { setDroppingId(null); }
  };

  const getDiffColor = (d) => d === 'Beginner' ? '#10b981' : d === 'Intermediate' ? '#f59e0b' : '#ef4444';

  if (loading) {
    return <div className="dash-loading"><div className="loading-spinner" /><p>Loading your personalized dashboard...</p></div>;
  }

  const overallProgress = stats?.avg_progress || 0;

  return (
    <div className="dashboard">
      <nav className="dash-nav">
        <div className="nav-brand">
          <svg viewBox="0 0 32 32" fill="none" width="32" height="32"><rect rx="6" width="32" height="32" fill="url(#ng)" /><path d="M10 24V14l6-5 6 5v10l-6 3-6-3z" fill="rgba(255,255,255,0.9)" /><path d="M16 9l6 5v10l-6 3" fill="rgba(255,255,255,0.6)" /><defs><linearGradient id="ng" x1="0" y1="0" x2="32" y2="32"><stop stopColor="#7c3aed" /><stop offset="1" stopColor="#06b6d4" /></linearGradient></defs></svg>
          <span>LearnPath AI</span>
        </div>
        <div className="nav-tabs">
          {['recommendations', 'my-courses', 'analytics', 'model'].map((tab) => (
            <button key={tab} className={`nav-tab ${activeTab === tab ? 'active' : ''}`} onClick={() => setActiveTab(tab)}>
              {tab === 'recommendations' && '🎯'}{tab === 'my-courses' && '📚'}{tab === 'analytics' && '📊'}{tab === 'model' && '🧠'}
              <span>{tab === 'my-courses' ? 'My Courses' : tab.charAt(0).toUpperCase() + tab.slice(1)}</span>
            </button>
          ))}
        </div>
        <div className="nav-user">
          <button className="nav-catalog-btn" onClick={() => navigate('/catalog')}>📖 Catalog</button>
          <div className="user-avatar">{(username || 'U')[0].toUpperCase()}</div>
          <span className="user-name">{username}</span>
          <button className="logout-btn" onClick={logout}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>
          </button>
        </div>
      </nav>

      <header className="dash-header animate-fade-in">
        <div className="header-content">
          <h1>Welcome back, <span className="gradient-text">{username}</span> 👋</h1>
          <p>Your personalized learning path — courses ordered from Beginner to Advanced by priority.</p>
        </div>
        <div className="header-stats">
          <div className="stat-pill"><span className="stat-value">{stats?.total_enrolled || 0}</span><span className="stat-label">Enrolled</span></div>
          <div className="stat-pill"><span className="stat-value">{Math.round(overallProgress)}%</span><span className="stat-label">Avg Progress</span></div>
          <div className="stat-pill"><span className="stat-value">{stats?.total_courses_rated || 0}</span><span className="stat-label">Rated</span></div>
          <div className="stat-pill"><span className="stat-value">{recs.length}</span><span className="stat-label">Picks</span></div>
        </div>
      </header>

      {/* ═══ RECOMMENDATIONS TAB ═══ */}
      {activeTab === 'recommendations' && (
        <section className="dash-section animate-fade-in-up">
          <div className="section-header">
            <h2>🎯 Learning Path Recommendations</h2>
            <p>Courses in priority order (Beginner → Advanced) — click "Why?" to see why each was recommended</p>
          </div>
          <div className="rec-grid stagger">
            {recs.map((rec, i) => (
              <div className={`rec-card ${expandedRec === rec.course_id ? 'expanded' : ''}`} key={rec.course_id} style={{ '--delay': `${i * 0.08}s` }}>
                <div className="rec-rank" style={{ background: getDiffColor(rec.difficulty) }}>
                  <span className="rank-priority">P{rec.priority || i + 1}</span>
                  <span className="rank-diff-label">{rec.difficulty[0]}</span>
                </div>
                <div className="rec-body">
                  <div className="rec-header">
                    <div>
                      <h3>{rec.course_name}</h3>
                      <div className="rec-priority-badge">{rec.priority_reason}</div>
                    </div>
                    <div className="rec-score"><span className="score-value">{rec.predicted_score.toFixed(1)}</span><span className="score-label">/ 5.0</span></div>
                  </div>
                  <div className="rec-tags">
                    <span className="tag category-tag">{rec.category}</span>
                    <span className="tag difficulty-tag" style={{ borderColor: getDiffColor(rec.difficulty), color: getDiffColor(rec.difficulty) }}>{rec.difficulty}</span>
                    <button className="tag why-tag" onClick={() => setExpandedRec(expandedRec === rec.course_id ? null : rec.course_id)}>
                      {expandedRec === rec.course_id ? '▲ Hide' : '❓ Why?'}
                    </button>
                  </div>
                  
                  {/* Why This Course Was Recommended */}
                  {expandedRec === rec.course_id && (
                    <div className="rec-why-panel animate-fade-in">
                      <div className="why-header">💡 Why this course was recommended</div>
                      <p className="why-explanation">{rec.explanation}</p>
                      <div className="why-signals">
                        <div className="why-signal">
                          <span className="signal-label">Priority Rank</span>
                          <span className="signal-value">#{rec.priority || i + 1} of {recs.length}</span>
                        </div>
                        <div className="why-signal">
                          <span className="signal-label">Predicted Score</span>
                          <span className="signal-value">{rec.predicted_score.toFixed(2)} / 5.0</span>
                        </div>
                        <div className="why-signal">
                          <span className="signal-label">Difficulty</span>
                          <span className="signal-value" style={{ color: getDiffColor(rec.difficulty) }}>{rec.difficulty}</span>
                        </div>
                        <div className="why-signal">
                          <span className="signal-label">Category</span>
                          <span className="signal-value">{rec.category}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="rec-actions">
                    {rec.is_enrolled ? (
                      <>
                        <button className="enroll-btn enrolled" onClick={() => navigate(`/learn/${rec.course_id}`)}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                          Continue
                        </button>
                        <button className="drop-btn" onClick={() => setDropConfirm(rec.course_id)}>🗑️ Drop</button>
                      </>
                    ) : (
                      <button className="enroll-btn" onClick={() => handleEnroll(rec.course_id)} disabled={enrollingId === rec.course_id}>
                        {enrollingId === rec.course_id ? <span className="spinner" /> : '📘 Enroll'}
                      </button>
                    )}
                    <button className="rate-btn" onClick={() => { setRatingModal(rec); setSelectedRating(0); }}>⭐ Rate</button>
                    <div className="score-bar-wrapper"><div className="score-bar" style={{ width: `${(rec.predicted_score / 5) * 100}%` }} /></div>
                  </div>
                </div>
              </div>
            ))}
            {recs.length === 0 && <div className="empty-state"><p>No recommendations available yet. Rate some courses to get started!</p></div>}
          </div>
        </section>
      )}

      {/* ═══ MY COURSES TAB (with progress bars & drop) ═══ */}
      {activeTab === 'my-courses' && (
        <section className="dash-section animate-fade-in-up">
          <div className="section-header">
            <h2>📚 My Enrolled Courses</h2>
            <p>Track your progress across all enrolled courses — sorted from Beginner to Advanced</p>
          </div>
          {enrollments.length === 0 ? (
            <div className="empty-state">
              <p>You haven't enrolled in any courses yet.</p>
              <button className="enroll-btn" onClick={() => setActiveTab('recommendations')} style={{ marginTop: 16 }}>Browse Recommendations</button>
            </div>
          ) : (
            <div className="enrolled-grid">
              {enrollments.map((e) => (
                <div className="enrolled-card" key={e.enrollment_id}>
                  <div className="enrolled-card-header">
                    <div className="enrolled-diff" style={{ background: getDiffColor(e.difficulty) }}>{e.difficulty}</div>
                    <span className="enrolled-category">{e.category}</span>
                    <button className="enrolled-drop-btn" onClick={() => setDropConfirm(e.course_id)} title="Drop course">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" /></svg>
                    </button>
                  </div>
                  <h3>{e.course_name}</h3>
                  <div className="enrolled-progress">
                    <div className="enrolled-progress-header">
                      <span>{e.completed_pages}/{e.total_pages} modules</span>
                      <span className="enrolled-pct">{e.progress_percent}%</span>
                    </div>
                    <div className="enrolled-bar">
                      <div className="enrolled-bar-fill" style={{
                        width: `${e.progress_percent}%`,
                        background: e.progress_percent === 100 ? 'var(--success)' : 'var(--accent-gradient)'
                      }} />
                    </div>
                    {e.progress_percent === 100 && <span className="complete-label">✅ Completed</span>}
                  </div>
                  <button className="cl-btn primary enrolled-continue" onClick={() => navigate(`/learn/${e.course_id}`)}>
                    {e.progress_percent === 100 ? 'Review Course' : 'Continue Learning'}
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* ═══ ANALYTICS TAB ═══ */}
      {activeTab === 'analytics' && stats && (
        <section className="dash-section animate-fade-in-up">
          <div className="section-header"><h2>📊 Learning Analytics</h2><p>Your learning patterns and engagement metrics</p></div>
          <div className="charts-grid">
            <div className="chart-card">
              <h3>Ratings by Category</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.ratings_by_category} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis dataKey="category" tick={{ fill: '#9ca3af', fontSize: 11 }} angle={-20} textAnchor="end" height={60} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} domain={[0, 5]} />
                  <Tooltip contentStyle={{ background: '#1f2028', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#f0f0f5' }} />
                  <Bar dataKey="avg_rating" radius={[6, 6, 0, 0]}>{(stats.ratings_by_category || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-card">
              <h3>Rating Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={stats.rating_distribution} dataKey="count" nameKey="stars" cx="50%" cy="50%" outerRadius={100} innerRadius={50} paddingAngle={3} label={({ stars, count }) => `${stars}★ (${count})`}>
                    {(stats.rating_distribution || []).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1f2028', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#f0f0f5' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            {stats.ratings_by_category && stats.ratings_by_category.length >= 3 && (
              <div className="chart-card chart-wide">
                <h3>Category Engagement</h3>
                <ResponsiveContainer width="100%" height={350}>
                  <RadarChart data={stats.ratings_by_category}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="category" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                    <Radar dataKey="count" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.3} />
                    <Radar dataKey="avg_rating" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.2} />
                    <Tooltip contentStyle={{ background: '#1f2028', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#f0f0f5' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ═══ MODEL TAB ═══ */}
      {activeTab === 'model' && modelInfo && (
        <section className="dash-section animate-fade-in-up">
          <div className="section-header"><h2>🧠 Model Information</h2><p>Technical details about the recommendation engine</p></div>
          <div className="model-grid">
            <div className="model-card"><div className="model-icon">⚙️</div><h4>Algorithm</h4><p>{modelInfo.algorithm}</p></div>
            <div className="model-card"><div className="model-icon">🤝</div><h4>CF Weight</h4><p>{(modelInfo.cf_weight * 100).toFixed(0)}%</p><span className="model-detail">{modelInfo.cf_method}</span></div>
            <div className="model-card"><div className="model-icon">📝</div><h4>CBF Weight</h4><p>{(modelInfo.cbf_weight * 100).toFixed(0)}%</p><span className="model-detail">{modelInfo.cbf_method}</span></div>
            <div className="model-card"><div className="model-icon">👥</div><h4>K Neighbors</h4><p>{modelInfo.n_neighbors}</p><span className="model-detail">Similar learners considered</span></div>
            <div className="model-card formula-card"><h4>Scoring Formula</h4><code className="formula">Score = a x CF_norm + (1-a) x CBF_norm</code><p className="formula-desc">Final scores normalized to [0,1] then scaled to [1,5]. a = {modelInfo.cf_weight}.</p></div>
          </div>
        </section>
      )}

      {/* ═══ RATING MODAL ═══ */}
      {ratingModal && (
        <div className="modal-overlay" onClick={() => setRatingModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Rate: {ratingModal.course_name}</h3>
            <p className="modal-subtitle">How would you rate this course?</p>
            <div className="star-picker">
              {[1, 2, 3, 4, 5].map((star) => (
                <button key={star} className={`star ${selectedRating >= star ? 'filled' : ''}`} onClick={() => setSelectedRating(star)}>★</button>
              ))}
            </div>
            {selectedRating > 0 && <p className="rating-label">{['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent'][selectedRating]}</p>}
            <div className="modal-actions">
              <button className="modal-cancel" onClick={() => setRatingModal(null)}>Cancel</button>
              <button className="modal-submit" onClick={handleRate} disabled={selectedRating === 0 || ratingLoading}>
                {ratingLoading ? <span className="spinner" /> : 'Submit Rating'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══ DROP CONFIRM MODAL ═══ */}
      {dropConfirm && (
        <div className="modal-overlay" onClick={() => setDropConfirm(null)}>
          <div className="modal drop-modal" onClick={(e) => e.stopPropagation()}>
            <div className="drop-icon">⚠️</div>
            <h3>Drop this course?</h3>
            <p className="modal-subtitle">All your progress will be lost. This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="modal-cancel" onClick={() => setDropConfirm(null)}>Keep Enrolled</button>
              <button className="modal-submit danger-submit" onClick={() => handleDrop(dropConfirm)} disabled={droppingId === dropConfirm}>
                {droppingId === dropConfirm ? <span className="spinner" /> : 'Yes, Drop Course'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
