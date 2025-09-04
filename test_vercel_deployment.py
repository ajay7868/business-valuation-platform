#!/usr/bin/env python3
"""
Test script to verify Vercel deployment readiness
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from flask_cors import CORS
        print("✅ Flask-CORS imported successfully")
    except ImportError as e:
        print(f"❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        import werkzeug
        print("✅ Werkzeug imported successfully")
    except ImportError as e:
        print(f"❌ Werkzeug import failed: {e}")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test app creation"""
    print("\n🧪 Testing app creation...")
    
    try:
        from app_vercel import app
        print("✅ Vercel app imported successfully")
        
        # Test basic app functionality
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_requirements():
    """Test requirements.txt"""
    print("\n🧪 Testing requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read().strip()
    
    expected_deps = ['Flask==2.3.3', 'Flask-CORS==4.0.0', 'Werkzeug==2.3.7', 'python-dotenv==1.0.0']
    
    for dep in expected_deps:
        if dep in requirements:
            print(f"✅ {dep} found in requirements.txt")
        else:
            print(f"❌ {dep} missing from requirements.txt")
            return False
    
    return True

def test_vercel_config():
    """Test Vercel configuration"""
    print("\n🧪 Testing Vercel configuration...")
    
    if not os.path.exists('vercel.json'):
        print("❌ vercel.json not found")
        return False
    
    if not os.path.exists('runtime.txt'):
        print("❌ runtime.txt not found")
        return False
    
    with open('runtime.txt', 'r') as f:
        runtime = f.read().strip()
    
    if runtime == 'python-3.9':
        print("✅ runtime.txt specifies Python 3.9")
    else:
        print(f"❌ runtime.txt has wrong version: {runtime}")
        return False
    
    print("✅ Vercel configuration files present")
    return True

def main():
    """Run all tests"""
    print("🚀 Vercel Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation,
        test_requirements,
        test_vercel_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n❌ Test failed: {test.__name__}")
            break
    
    print("\n" + "=" * 50)
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Ready for Vercel deployment!")
        return 0
    else:
        print(f"❌ {passed}/{total} tests passed")
        print("❌ Not ready for deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
