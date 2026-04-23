import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login as loginApi, signup as signupApi } from '../api';
import { useAuth } from '../context/AuthContext';
import './AuthPage.css';

const SKILL_OPTIONS = [
  'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'React', 'Node.js',
  'SQL', 'Machine Learning', 'Data Science', 'Docker', 'AWS', 'Git',
  'Django', 'Flask', 'HTML/CSS', 'Deep Learning', 'Kubernetes',
];

const INTEREST_OPTIONS = [
  'Web Development', 'AI/ML', 'Data Engineering', 'Cloud Computing',
  'DevOps', 'Mobile Development', 'Cybersecurity', 'Full Stack',
  'Backend Development', 'Frontend Development', 'Research',
];

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [skills, setSkills] = useState([]);
  const [interests, setInterests] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const toggleSkill = (skill) => {
    setSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const toggleInterest = (interest) => {
    setInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : [...prev, interest]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      let res;
      if (isLogin) {
        res = await loginApi({ email, password });
      } else {
        if (!username.trim()) {
          setError('Username is required');
          setLoading(false);
          return;
        }
        res = await signupApi({ username, email, password, skills, interests });
      }
      loginUser(res.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-orbs">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>

      <div className="auth-container animate-fade-in">
        <div className="auth-brand">
          <div className="auth-logo">
            <svg viewBox="0 0 40 40" fill="none">
              <rect rx="8" width="40" height="40" fill="url(#logo-gradient)" />
              <path d="M12 28V16l8-6 8 6v12l-8 4-8-4z" fill="rgba(255,255,255,0.9)" />
              <path d="M20 10l8 6v12l-8 4" fill="rgba(255,255,255,0.6)" />
              <defs>
                <linearGradient id="logo-gradient" x1="0" y1="0" x2="40" y2="40">
                  <stop stopColor="#7c3aed" />
                  <stop offset="1" stopColor="#06b6d4" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 className="auth-title">LearnPath AI</h1>
          <p className="auth-subtitle">
            {isLogin
              ? 'Welcome back! Sign in to continue learning.'
              : 'Create your account and get personalized recommendations.'}
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {error && (
            <div className="auth-error">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
              {error}
            </div>
          )}

          {!isLogin && (
            <div className="input-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          )}

          <div className="input-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {!isLogin && (
            <>
              <div className="chip-group">
                <label>Select Your Skills</label>
                <div className="chips">
                  {SKILL_OPTIONS.map((s) => (
                    <button
                      type="button"
                      key={s}
                      className={`chip ${skills.includes(s) ? 'active' : ''}`}
                      onClick={() => toggleSkill(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div className="chip-group">
                <label>Your Interests</label>
                <div className="chips">
                  {INTEREST_OPTIONS.map((i) => (
                    <button
                      type="button"
                      key={i}
                      className={`chip ${interests.includes(i) ? 'active' : ''}`}
                      onClick={() => toggleInterest(i)}
                    >
                      {i}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          <button
            type="submit"
            className="auth-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="spinner" />
            ) : isLogin ? (
              'Sign In'
            ) : (
              'Create Account'
            )}
          </button>

          <p className="auth-switch">
            {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
            <button
              type="button"
              className="switch-btn"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>

          {isLogin && (
            <div className="demo-hint">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
              Demo: use any seeded user email (e.g. user's email from DB) with password <code>password123</code>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
