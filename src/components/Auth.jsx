import React, { useState } from 'react';
import { toast } from 'react-toastify';

function Auth({ onAuthSuccess, onClose }) {
  const [isLogin, setIsLogin] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    mobile: ''
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),

      });

      const result = await response.json();

      if (response.ok) {
        if (isLogin) {
          // Login successful
          toast.success(result.message);
          // Store session token and user data
          if (result.session_token) {
            localStorage.setItem('session_token', result.session_token);
            localStorage.setItem('user_data', JSON.stringify(result.user));
          }
          onAuthSuccess(result.user);
        } else {
          // Signup successful
          toast.success(result.message);
          if (result.email_sent) {
            toast.info('Please check your email for verification link');
          }
          // Switch to login mode
          setIsLogin(true);
          setFormData({ email: formData.email, password: '', confirm_password: '', mobile: '' });
        }
      } else {
        toast.error(result.error || 'Authentication failed');
      }
    } catch (error) {
      console.error('Auth error:', error);
      toast.error('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setFormData({ email: '', password: '', confirm_password: '', mobile: '' });
  };

  return (
    <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">
              {isLogin ? 'Login' : 'Sign Up'} - Business Valuation Platform
            </h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          
          <div className="modal-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Email *</label>
                <input
                  type="email"
                  className="form-control"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your email"
                />
              </div>

              {!isLogin && (
                <div className="mb-3">
                  <label className="form-label">Mobile Number (Optional)</label>
                  <input
                    type="tel"
                    className="form-control"
                    name="mobile"
                    value={formData.mobile}
                    onChange={handleInputChange}
                    placeholder="Enter mobile number"
                  />
                </div>
              )}

              <div className="mb-3">
                <label className="form-label">Password *</label>
                <input
                  type="password"
                  className="form-control"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter password"
                />
                {!isLogin && (
                  <small className="form-text text-muted">
                    Password must be at least 8 characters with uppercase, lowercase, and number
                  </small>
                )}
              </div>

              {!isLogin && (
                <div className="mb-3">
                  <label className="form-label">Confirm Password *</label>
                  <input
                    type="password"
                    className="form-control"
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleInputChange}
                    required
                    placeholder="Confirm password"
                  />
                </div>
              )}

              <div className="d-grid gap-2">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      {isLogin ? 'Logging in...' : 'Creating Account...'}
                    </>
                  ) : (
                    isLogin ? 'Login' : 'Sign Up'
                  )}
                </button>
              </div>
            </form>

            <div className="text-center mt-3">
              <button
                type="button"
                className="btn btn-link"
                onClick={toggleMode}
              >
                {isLogin 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Login"
                }
              </button>
            </div>

            {!isLogin && (
              <div className="alert alert-info mt-3">
                <small>
                  <strong>Why sign up?</strong><br/>
                  • Generate unlimited valuation reports<br/>
                  • Access AI-powered business analysis<br/>
                  • Download reports in multiple formats<br/>
                  • Track your valuation history
                </small>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Auth;
