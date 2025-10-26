#!/usr/bin/env python3
"""
End-to-End Testing Script for AI Wireframing Tool
Tests the complete pipeline from API request to response
"""

import requests
import json
import base64
import time
from PIL import Image
import io

# Test configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_health_endpoint():
    """Test if the API health endpoint is working"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data['status']}")
            print(f"   Device: {health_data['device']}")
            print(f"   AI Available: {health_data.get('ai_available', 'Unknown')}")
            print(f"   Mode: {health_data.get('mode', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_wireframe_styles():
    """Test wireframe styles endpoint"""
    print("\n🎨 Testing wireframe styles endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/wireframe-styles", timeout=5)
        if response.status_code == 200:
            styles = response.json()
            print(f"✅ Styles endpoint working: {len(styles['styles'])} styles available")
            for style in styles['styles']:
                print(f"   - {style['id']}: {style['name']}")
            return True
        else:
            print(f"❌ Styles endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Styles endpoint error: {e}")
        return False

def test_wireframe_generation(prompt, style="low-fi", width=400, height=300):
    """Test wireframe generation with different parameters"""
    print(f"\n🖼️  Testing wireframe generation...")
    print(f"   Prompt: '{prompt}'")
    print(f"   Style: {style}, Size: {width}x{height}")
    
    try:
        start_time = time.time()
        
        payload = {
            "prompt": prompt,
            "style": style,
            "width": width,
            "height": height,
            "num_inference_steps": 10,  # Reduced for faster testing
            "guidance_scale": 7.5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/generate-wireframe",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generation_time = time.time() - start_time
            
            print(f"✅ Wireframe generated successfully!")
            print(f"   Generation time: {result['generation_time']:.2f}s")
            print(f"   Total request time: {generation_time:.2f}s")
            print(f"   Image data length: {len(result['image_base64'])} chars")
            print(f"   SVG code length: {len(result['svg_code'])} chars")
            
            # Validate image data
            try:
                image_data = base64.b64decode(result['image_base64'])
                image = Image.open(io.BytesIO(image_data))
                print(f"   Image format: {image.format}, Size: {image.size}")
                
                # Save test image
                image.save(f"test_wireframe_{style}_{int(time.time())}.png")
                print(f"   Test image saved successfully")
                
            except Exception as e:
                print(f"⚠️  Image validation failed: {e}")
            
            # Validate SVG
            if result['svg_code'].strip().startswith('<svg'):
                print(f"   SVG format validated")
            else:
                print(f"⚠️  SVG format may be invalid")
            
            return True
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False

def test_cors():
    """Test CORS configuration for frontend integration"""
    print(f"\n🌐 Testing CORS configuration...")
    try:
        # Simulate a preflight request from the frontend
        response = requests.options(
            f"{API_BASE_URL}/generate-wireframe",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ CORS preflight request successful")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
            
            return True
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def run_comprehensive_tests():
    """Run all end-to-end tests"""
    print("🚀 Starting End-to-End Tests for AI Wireframing Tool")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health check
    total_tests += 1
    if test_health_endpoint():
        tests_passed += 1
    
    # Test 2: Wireframe styles
    total_tests += 1
    if test_wireframe_styles():
        tests_passed += 1
    
    # Test 3: CORS configuration
    total_tests += 1
    if test_cors():
        tests_passed += 1
    
    # Test 4: Basic wireframe generation
    test_cases = [
        ("Login page with email field, password field, and submit button", "low-fi"),
        ("Dashboard with sidebar navigation and charts", "high-fi"),
        ("Mobile app home screen with bottom navigation", "mobile"),
        ("E-commerce product page with image gallery", "web")
    ]
    
    for prompt, style in test_cases:
        total_tests += 1
        if test_wireframe_generation(prompt, style):
            tests_passed += 1
    
    # Results summary
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The wireframing tool is working correctly.")
        return True
    else:
        print(f"⚠️  {total_tests - tests_passed} tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
