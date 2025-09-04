import React, { useState } from 'react';
import { toast } from 'react-toastify';

function UserProfile({ user, onLogout }) {
  const [loading, setLoading] = useState(false);

  // Add null check for user
  if (!user) {
    return (
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-2">Loading user profile...</p>
      </div>
    );
  }

  const handleLogout = async () => {
    setLoading(true);
    try {
      const sessionToken = localStorage.getItem('session_token');
      const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
      
      if (sessionToken) {
        const response = await fetch(`${baseUrl}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ session_token: sessionToken })
        });

        if (response.ok) {
          toast.success('Logged out successfully');
          onLogout();
        } else {
          const result = await response.json();
          toast.error(result.error || 'Logout failed');
        }
      } else {
        // No session token, just logout locally
        onLogout();
      }
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Network error during logout');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
        <div className="row">
          <div className="col-md-6">
            <p><strong>Email:</strong> {user.email}</p>
            {user.mobile && <p><strong>Mobile:</strong> {user.mobile}</p>}
            <p>
              <strong>Status:</strong> 
              <span className={`badge ms-2 ${user.email_verified ? 'bg-success' : 'bg-warning'}`}>
                {user.email_verified ? 'Verified' : 'Pending Verification'}
              </span>
            </p>
          </div>
          <div className="col-md-6">
            <p><strong>Member Since:</strong> {user.created_at ? new Date(user.created_at.replace(' ', 'T')).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : 'N/A'}</p>
            {user.last_login && (
              <p><strong>Last Login:</strong> {new Date(user.last_login.replace(' ', 'T')).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
            )}
          </div>
        </div>

        {!user.email_verified && (
          <div className="alert alert-warning mt-3">
            <i className="fas fa-exclamation-triangle me-2"></i>
            <strong>Email Verification Required</strong><br/>
            Please check your email and click the verification link to access all features.
          </div>
        )}

        <div className="d-grid gap-2 mt-3">
          <button
            className="btn btn-outline-danger"
            onClick={handleLogout}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Logging out...
              </>
            ) : (
              <>
                <i className="fas fa-sign-out-alt me-2"></i>
                Logout
              </>
            )}
          </button>
        </div>
    </div>
  );
}

export default UserProfile;
