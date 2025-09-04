# 🔐 Authentication System Setup Guide

## Overview

The Business Valuation Platform now includes a comprehensive authentication system with:

- **User Registration & Login**: Email/password authentication
- **Email Verification**: Required before accessing premium features
- **Rate Limiting**: Prevents abuse and encourages signup
- **Session Management**: Secure user sessions
- **Activity Logging**: Track user actions for audit purposes

## 🚀 Features

### 1. Rate Limiting
- **2 Free Attempts**: Users can upload files and generate reports twice
- **3rd Attempt**: Redirected to signup page
- **24-Hour Reset**: Limits reset daily for fair usage

### 2. User Authentication
- **Signup**: Email, password, confirm password, mobile (optional)
- **Email Verification**: Required before accessing reports
- **Login**: Secure authentication with session management
- **Profile Management**: View and manage account details

### 3. Access Control
- **File Upload**: Limited to 2 attempts for unauthenticated users
- **Report Generation**: Requires verified email authentication
- **AI Validation**: Available to all users during free attempts

## ⚙️ Setup Instructions

### 1. Environment Configuration

Copy `env.template` to `.env` and configure:

```bash
# Copy environment template
cp env.template .env

# Edit .env file with your settings
nano .env
```

#### Required Environment Variables:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///valuation_platform.db

# Email Configuration (for user verification)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# OpenAI Configuration (for AI validation)
OPENAI_API_KEY=your-openai-api-key
```

### 2. Email Setup (Gmail Example)

#### For Gmail:
1. Enable 2-Factor Authentication
2. Generate App Password:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the generated password in `MAIL_PASSWORD`

#### For Other Providers:
- Update `MAIL_SERVER`, `MAIL_PORT`, and `MAIL_USE_TLS`
- Use appropriate credentials

### 3. Database Setup

The system automatically creates SQLite database tables:

```bash
# Database will be created automatically on first run
# Location: valuation_platform.db
```

#### For Production (PostgreSQL):
```bash
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### 4. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install flask-login flask-sqlalchemy flask-mail flask-limiter
```

## 🔧 API Endpoints

### Authentication Endpoints

#### POST `/api/auth/signup`
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123",
  "mobile": "+1234567890"
}
```

#### POST `/api/auth/login`
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### GET `/api/auth/verify/<token>`
- Email verification endpoint
- Called automatically when user clicks verification link

#### POST `/api/auth/logout`
- Requires authentication
- Clears user session

#### GET `/api/auth/profile`
- Requires authentication
- Returns user profile information

#### GET `/api/auth/rate-limit-status`
- Returns current rate limit status for user

### Protected Endpoints

#### POST `/api/report/generate`
- **Requires**: Authenticated user with verified email
- **Rate Limit**: None (unlimited for verified users)

#### POST `/api/upload`
- **Rate Limit**: 2 attempts per 24 hours for unauthenticated users
- **Unlimited**: For authenticated users

## 📱 Frontend Integration

### Authentication Components

1. **Auth Modal** (`src/components/Auth.jsx`)
   - Signup/Login forms
   - Email verification prompts
   - Password strength validation

2. **User Profile** (`src/components/UserProfile.jsx`)
   - Display user information
   - Email verification status
   - Logout functionality

3. **Rate Limit Warnings**
   - Automatic display when limits exceeded
   - Signup prompts for blocked users

### User Flow

1. **First Visit**: User can upload files and generate reports (2 attempts)
2. **Rate Limit Reached**: System prompts for signup
3. **Signup Process**: User creates account with email verification
4. **Email Verification**: User clicks link in verification email
5. **Full Access**: Verified users have unlimited access to all features

## 🛡️ Security Features

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number

### Session Security
- Secure session management
- CSRF protection
- Secure cookie handling

### Rate Limiting
- IP-based tracking
- Device fingerprinting
- Configurable limits and timeouts

## 📊 Monitoring & Logging

### User Activities
- File uploads
- Report generation
- Login/logout events
- Failed authentication attempts

### Rate Limit Tracking
- Attempt counts
- Block durations
- IP addresses
- Device information

## 🚨 Troubleshooting

### Common Issues

#### Email Not Sending
1. Check SMTP credentials
2. Verify app password (Gmail)
3. Check firewall/network settings
4. Review email server logs

#### Database Errors
1. Ensure write permissions
2. Check disk space
3. Verify database URL format

#### Rate Limiting Issues
1. Check IP address detection
2. Verify timezone settings
3. Review rate limit configuration

### Debug Mode

Enable debug logging:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
```

## 🔄 Production Deployment

### Environment Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://username:password@localhost/dbname
MAIL_SERVER=your-smtp-server
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

### Security Considerations
1. Use strong, unique secret keys
2. Enable HTTPS
3. Configure proper CORS settings
4. Set up monitoring and alerting
5. Regular security updates

## 📈 Usage Analytics

The system tracks:
- User registration rates
- Email verification success rates
- Feature usage patterns
- Rate limit triggers
- User engagement metrics

## 🎯 Next Steps

1. **Configure Email Settings**: Set up SMTP for user verification
2. **Test Authentication Flow**: Verify signup, login, and verification
3. **Monitor Rate Limiting**: Ensure proper limits and user experience
4. **Customize UI**: Adjust authentication components as needed
5. **Production Setup**: Configure production environment variables

---

**Need Help?** Check the logs for detailed error messages and ensure all environment variables are properly configured.
