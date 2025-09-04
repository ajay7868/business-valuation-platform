# 🚀 Business Valuation Platform

**AI-powered Business Valuation Platform with comprehensive financial analysis, SWOT insights, and professional reporting.**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ajay7868/business-valuation-platform)

## ✨ Features

- **📊 Comprehensive Valuation Methods**: DCF, Asset-based, Market-based approaches
- **🤖 AI-Powered SWOT Analysis**: Strategic insights and positioning guidance
- **📁 Multi-Format Support**: PDF, Excel, CSV, and image file processing
- **📈 Professional Reports**: Detailed financial analysis and recommendations
- **🔒 Production Ready**: Secure, scalable, and optimized for deployment
- **📱 Modern UI**: Responsive React frontend with Bootstrap 5

## 🏗️ Tech Stack

### Backend
- **Python 3.9+** with Flask framework
- **Pandas** for data processing
- **PDFplumber** for PDF extraction
- **OpenPyXL** for Excel processing
- **ReportLab** for report generation

### Frontend
- **React 18** with modern hooks
- **Bootstrap 5** for responsive design
- **Chart.js** for data visualization
- **Axios** for API communication
- **React Dropzone** for file uploads

### Infrastructure
- **Vercel** for production deployment
- **Environment-based configuration**
- **CORS security** for production domains
- **File size validation** (100MB limit)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm 8+

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ajay7868/business-valuation-platform.git
   cd business-valuation-platform
   ```

2. **Backend Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   npm install
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5000

## 🌐 Production Deployment on Vercel

### 1. Push to GitHub
```bash
git add .
git commit -m "Production ready for Vercel deployment"
git push -u origin main
```

### 2. Deploy on Vercel
1. Visit [Vercel](https://vercel.com) and sign in with GitHub
2. Click "New Project" and import your repository
3. Configure environment variables:
   ```
   FLASK_ENV=production
   UPLOAD_FOLDER=/tmp/uploads
   REPORTS_FOLDER=/tmp/reports
   MAX_CONTENT_LENGTH=104857600
   ```
4. Deploy!

### 3. Update API Configuration
After deployment, update the API URL in `src/services/api.js`:
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-actual-domain.vercel.app/api'
  : '/api';
```

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check and status |
| `/api/upload` | POST | File upload and data extraction |
| `/api/valuation` | POST | Calculate business valuation |
| `/api/swot` | POST | Generate SWOT analysis |
| `/api/report/generate` | POST | Create comprehensive report |
| `/api/report/download/<filename>` | GET | Download generated report |

## 🔧 Configuration

### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=production
PORT=5000

# File Storage
UPLOAD_FOLDER=/tmp/uploads
REPORTS_FOLDER=/tmp/reports
MAX_CONTENT_LENGTH=104857600

# OpenAI (Optional)
OPENAI_API_KEY=your_openai_key_here
```

### CORS Configuration
The platform is configured for production with secure CORS settings:
```python
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-vercel-domain.vercel.app",
    "https://*.vercel.app"
])
```

## 📁 Project Structure
```
business-valuation-platform/
├── app.py                 # Flask backend application
├── valuation_engine.py    # Core valuation logic
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── vercel.json           # Vercel configuration
├── src/                  # React frontend source
│   ├── components/       # React components
│   ├── services/         # API services
│   └── App.jsx          # Main application
├── uploads/              # File upload directory
├── reports/              # Generated reports
└── README.md            # This file
```

## 🎯 Usage Workflow

1. **Upload Financial Documents**
   - Support for PDF, Excel, CSV, and image files
   - Automatic data extraction and validation
   - 100MB file size limit

2. **Generate Valuations**
   - Multiple valuation methodologies
   - Comprehensive financial analysis
   - Executive summary generation

3. **SWOT Analysis**
   - AI-powered strategic insights
   - Positioning guidance
   - Value drivers identification

4. **Professional Reports**
   - Detailed financial analysis
   - Methodology and assumptions
   - Actionable recommendations

## 🔒 Security Features

- **File Type Validation**: Only allowed file types accepted
- **File Size Limits**: Configurable maximum file sizes
- **CORS Protection**: Production domain restrictions
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error messages

## 🚀 Performance Optimizations

- **Async Processing**: Non-blocking file operations
- **Memory Management**: Efficient file handling
- **Caching**: Report generation optimization
- **Compression**: Optimized file transfers

## 📊 Sample Data

The platform includes sample financial data for testing:
- Company: Test Manufacturing Co
- Industry: Manufacturing
- Revenue: $5,000,000
- EBITDA: $800,000
- Total Assets: $3,000,000

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ajay7868/business-valuation-platform/issues)
- **Documentation**: [Wiki](https://github.com/ajay7868/business-valuation-platform/wiki)
- **Email**: [Your Email]

## 🗺️ Roadmap

- [ ] **Database Integration**: PostgreSQL/MongoDB support
- [ ] **User Authentication**: JWT-based auth system
- [ ] **Advanced AI**: GPT-4 integration for enhanced analysis
- [ ] **Real-time Updates**: WebSocket support
- [ ] **Mobile App**: React Native application
- [ ] **API Rate Limiting**: Advanced request management
- [ ] **Analytics Dashboard**: Usage metrics and insights

---

**Built with ❤️ by [Ajay Yadav](https://github.com/ajay7868)**

*Full Stack Developer | Business Valuation Expert | AI Enthusiast*
# Vercel deployment fix - Thu Sep  4 20:01:21 IST 2025
