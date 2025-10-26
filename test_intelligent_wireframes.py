#!/usr/bin/env python3
"""
Test script for intelligent wireframe generation
Demonstrates the new modular backend capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from backend.app.models.wireframe import WireframeRequest, LayoutType, WireframeStyle
from backend.app.services.wireframe_generator import WireframeGenerator
from backend.app.services.prompt_analyzer import PromptAnalyzer
from backend.app.services.layout_engine import LayoutEngine


async def test_intelligent_wireframes():
    """Test the intelligent wireframe generation"""
    
    print("🧪 Testing Intelligent Wireframe Generation")
    print("=" * 50)
    
    # Initialize services
    generator = WireframeGenerator()
    analyzer = PromptAnalyzer()
    
    # Test cases with different prompts
    test_cases = [
        {
            "prompt": "E-commerce product page with image gallery, price, and add to cart button",
            "description": "E-commerce Product Page"
        },
        {
            "prompt": "Mobile app login screen with email field, password field, and social login options",
            "description": "Mobile Login Screen"
        },
        {
            "prompt": "Analytics dashboard with charts, metrics, sidebar navigation, and user profile",
            "description": "Analytics Dashboard"
        },
        {
            "prompt": "Landing page with hero section, features, testimonials, and contact form",
            "description": "Marketing Landing Page"
        },
        {
            "prompt": "Blog homepage with article list, sidebar, search, and categories",
            "description": "Blog Homepage"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print("-" * 30)
        print(f"Prompt: \"{test_case['prompt']}\"")
        
        # Analyze the prompt
        analysis = analyzer.analyze_prompt(test_case['prompt'])
        
        print(f"📊 Analysis Results:")
        print(f"   Layout Type: {analysis['layout_type'].value}")
        print(f"   Style: {analysis['style'].value}")
        print(f"   Suggested Size: {analysis['suggested_width']}x{analysis['suggested_height']}")
        print(f"   Components: {[c.value for c in analysis['components']]}")
        print(f"   Confidence: {analysis['confidence']:.2f}")
        
        # Create wireframe request
        request = WireframeRequest(
            prompt=test_case['prompt'],
            layout_type=analysis['layout_type'],
            style=analysis['style'],
            width=analysis['suggested_width'],
            height=analysis['suggested_height'],
            use_ai=False  # Test algorithmic generation
        )
        
        try:
            # Generate wireframe
            response = await generator.generate_wireframe(request)
            
            print(f"✅ Generation Results:")
            print(f"   ID: {response.id}")
            print(f"   Generation Time: {response.generation_time:.3f}s")
            print(f"   Components Generated: {len(response.components)}")
            print(f"   Image Size: {len(response.image_base64)} chars")
            print(f"   SVG Size: {len(response.svg_code)} chars")
            print(f"   AI Enhanced: {response.metadata.get('ai_enhanced', False)}")
            
            # Save test wireframe
            import base64
            from PIL import Image
            import io
            
            # Decode and save image
            image_data = base64.b64decode(response.image_base64)
            image = Image.open(io.BytesIO(image_data))
            filename = f"test_intelligent_{analysis['layout_type'].value}_{i}.png"
            image.save(filename)
            print(f"   Saved: {filename}")
            
            # Save SVG
            svg_filename = f"test_intelligent_{analysis['layout_type'].value}_{i}.svg"
            with open(svg_filename, 'w') as f:
                f.write(response.svg_code)
            print(f"   Saved: {svg_filename}")
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
    
    print(f"\n🎉 Intelligent wireframe testing complete!")
    print("Check the generated PNG and SVG files to see the results.")


def test_prompt_analysis():
    """Test prompt analysis capabilities"""
    
    print("\n🔍 Testing Prompt Analysis")
    print("=" * 30)
    
    analyzer = PromptAnalyzer()
    
    test_prompts = [
        "Create a dashboard for sales analytics with charts and KPIs",
        "Mobile checkout flow with payment options and order summary", 
        "Blog post page with comments, related articles, and social sharing",
        "User profile settings page with form fields and preferences",
        "Product comparison table with features and pricing"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: \"{prompt}\"")
        analysis = analyzer.analyze_prompt(prompt)
        
        print(f"  → Layout: {analysis['layout_type'].value}")
        print(f"  → Components: {[c.value for c in analysis['components'][:3]]}...")
        print(f"  → Requirements: {list(analysis['requirements'].keys())[:3]}...")
        print(f"  → Confidence: {analysis['confidence']:.2f}")


if __name__ == "__main__":
    # Test prompt analysis first
    test_prompt_analysis()
    
    # Test full wireframe generation
    asyncio.run(test_intelligent_wireframes())
