#!/bin/bash

# Production Deployment Script
# Business Valuation Platform

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."

# Check if we're in the right directory
if [ ! -f "app_sqlite.py" ]; then
    echo "❌ Error: app_sqlite.py not found. Please run this script from the project root."
    exit 1
fi

# Check if environment file exists
if [ ! -f "env.production" ]; then
    echo "❌ Error: env.production file not found. Please create it first."
    exit 1
fi

# Load environment variables
echo "📋 Loading production environment variables..."
export $(cat env.production | grep -v '^#' | xargs)

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads reports logs

# Set proper permissions
echo "🔐 Setting proper permissions..."
chmod 755 uploads reports logs
chmod 644 env.production

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python3 init_db.py

# Build frontend
echo "🏗️ Building frontend..."
npm install
npm run build

# Test backend
echo "🧪 Testing backend..."
python3 -c "
import sys
sys.path.append('.')
from app_sqlite import app
print('✅ Backend imports successfully')
"

# Test frontend build
echo "🧪 Testing frontend build..."
if [ -d "build" ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi

# Security checks
echo "🔒 Running security checks..."

# Check for hardcoded secrets
if grep -r "your-secret-key-change-in-production" . --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git; then
    echo "❌ Security Warning: Hardcoded secrets found!"
    exit 1
fi

# Check for localhost URLs in production build
if grep -r "localhost:5001" build/; then
    echo "❌ Security Warning: Localhost URLs found in production build!"
    exit 1
fi

echo "✅ Security checks passed"

# Create systemd service file (optional)
echo "⚙️ Creating systemd service file..."
cat > valuation-platform.service << EOF
[Unit]
Description=Business Valuation Platform
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app_sqlite:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Production deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy env.production to .env and update with your production values"
echo "2. Set up your production database (PostgreSQL recommended)"
echo "3. Configure your web server (nginx) to serve the frontend"
echo "4. Set up SSL certificates"
echo "5. Configure monitoring and logging"
echo "6. Test the deployment in a staging environment first"
echo ""
echo "⚠️  Remember to:"
echo "- Update ALLOWED_ORIGINS in env.production with your domain"
echo "- Set a strong SECRET_KEY"
echo "- Configure proper database credentials"
echo "- Set up email configuration for user verification"
echo "- Enable HTTPS in production"
