/**
 * Frontend Integration Test
 * Tests the frontend's ability to communicate with the backend API
 */

// Simple integration test that can be run in the browser console
const testFrontendIntegration = async () => {
  console.log('🧪 Starting Frontend Integration Test...');
  
  const API_BASE_URL = 'http://localhost:8000';
  
  try {
    // Test 1: Health check
    console.log('1️⃣ Testing health endpoint...');
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('✅ Health check:', healthData);
    
    // Test 2: Wireframe styles
    console.log('2️⃣ Testing wireframe styles...');
    const stylesResponse = await fetch(`${API_BASE_URL}/wireframe-styles`);
    const stylesData = await stylesResponse.json();
    console.log('✅ Styles:', stylesData.styles.map(s => s.name));
    
    // Test 3: Generate wireframe
    console.log('3️⃣ Testing wireframe generation...');
    const generateResponse = await fetch(`${API_BASE_URL}/generate-wireframe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: 'Simple login form with email and password',
        style: 'low-fi',
        width: 300,
        height: 200,
        num_inference_steps: 10,
        guidance_scale: 7.5
      })
    });
    
    if (generateResponse.ok) {
      const wireframeData = await generateResponse.json();
      console.log('✅ Wireframe generated successfully!');
      console.log(`   Generation time: ${wireframeData.generation_time}s`);
      console.log(`   Image data length: ${wireframeData.image_base64.length} chars`);
      console.log(`   SVG code length: ${wireframeData.svg_code.length} chars`);
      
      // Display the generated wireframe in the console (as data URL)
      const imageDataUrl = `data:image/png;base64,${wireframeData.image_base64}`;
      console.log('🖼️ Generated wireframe (copy this URL to browser to view):');
      console.log(imageDataUrl);
      
      return {
        success: true,
        data: wireframeData,
        imageUrl: imageDataUrl
      };
    } else {
      throw new Error(`Generation failed: ${generateResponse.status}`);
    }
    
  } catch (error) {
    console.error('❌ Integration test failed:', error);
    return { success: false, error: error.message };
  }
};

// Export for use in browser console or testing framework
if (typeof window !== 'undefined') {
  window.testFrontendIntegration = testFrontendIntegration;
}

// Instructions for manual testing
console.log(`
🧪 Frontend Integration Test Available!

To run this test:
1. Open browser developer tools (F12)
2. Navigate to the Console tab
3. Run: testFrontendIntegration()

This will test the frontend's ability to communicate with the backend API.
`);

export default testFrontendIntegration;
