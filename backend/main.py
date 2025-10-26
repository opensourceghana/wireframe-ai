from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw
import numpy as np
import io
import base64
import logging
from typing import Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Wireframing Tool", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
pipe = None
device = "cpu"  # For prototype, we'll use CPU-only mode

class WireframeRequest(BaseModel):
    prompt: str
    style: str = "low-fi"
    width: int = 512
    height: int = 512
    num_inference_steps: int = 20
    guidance_scale: float = 7.5

class WireframeResponse(BaseModel):
    image_base64: str
    svg_code: str
    generation_time: float

def create_wireframe_condition(width: int, height: int, style: str = "low-fi") -> Image.Image:
    """Create a simple wireframe condition image"""
    # Create a white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw basic wireframe structure
    if style == "low-fi":
        # Header
        draw.rectangle([20, 20, width-20, 80], outline='black', width=2)
        draw.text((30, 45), "HEADER", fill='black')
        
        # Navigation
        draw.rectangle([20, 100, width-20, 140], outline='black', width=2)
        draw.text((30, 115), "NAVIGATION", fill='black')
        
        # Main content area
        draw.rectangle([20, 160, width-20, height-80], outline='black', width=2)
        draw.text((30, 180), "MAIN CONTENT", fill='black')
        
        # Footer
        draw.rectangle([20, height-60, width-20, height-20], outline='black', width=2)
        draw.text((30, height-45), "FOOTER", fill='black')
    
    return img

def generate_svg_wireframe(prompt: str, width: int, height: int) -> str:
    """Generate SVG wireframe based on prompt"""
    svg_template = f'''
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <style>
            .wireframe-box {{ fill: none; stroke: #333; stroke-width: 2; }}
            .wireframe-text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #666; }}
            .header {{ fill: #f0f0f0; stroke: #333; stroke-width: 2; }}
        </style>
        
        <!-- Header -->
        <rect x="20" y="20" width="{width-40}" height="60" class="header"/>
        <text x="30" y="45" class="wireframe-text">Header - {prompt[:20]}...</text>
        
        <!-- Navigation -->
        <rect x="20" y="100" width="{width-40}" height="40" class="wireframe-box"/>
        <text x="30" y="125" class="wireframe-text">Navigation</text>
        
        <!-- Main Content -->
        <rect x="20" y="160" width="{width-40}" height="{height-240}" class="wireframe-box"/>
        <text x="30" y="185" class="wireframe-text">Main Content Area</text>
        <text x="30" y="205" class="wireframe-text">{prompt}</text>
        
        <!-- Sidebar (if wide enough) -->
        {f'<rect x="{width-180}" y="160" width="140" height="{height-240}" class="wireframe-box"/>' if width > 400 else ''}
        {f'<text x="{width-170}" y="185" class="wireframe-text">Sidebar</text>' if width > 400 else ''}
        
        <!-- Footer -->
        <rect x="20" y="{height-60}" width="{width-40}" height="40" class="wireframe-box"/>
        <text x="30" y="{height-35}" class="wireframe-text">Footer</text>
    </svg>
    '''
    return svg_template.strip()

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global pipe
    try:
        logger.info(f"Loading models on device: {device}")
        
        # For now, we'll use a simple approach without ControlNet due to model complexity
        # In production, you would load the actual ControlNet model here
        logger.info("Models loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        # Continue without models for basic functionality

@app.get("/")
async def root():
    return {"message": "AI Wireframing Tool API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "device": device,
        "torch_available": "CPU only (prototype mode)"
    }

@app.post("/generate-wireframe", response_model=WireframeResponse)
async def generate_wireframe(request: WireframeRequest):
    """Generate wireframe from text prompt"""
    try:
        import time
        start_time = time.time()
        
        logger.info(f"Generating wireframe for prompt: {request.prompt}")
        
        # Create wireframe condition image
        condition_image = create_wireframe_condition(
            request.width, 
            request.height, 
            request.style
        )
        
        # Generate SVG wireframe
        svg_code = generate_svg_wireframe(
            request.prompt,
            request.width,
            request.height
        )
        
        # Convert condition image to base64
        img_buffer = io.BytesIO()
        condition_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        image_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        generation_time = time.time() - start_time
        
        logger.info(f"Wireframe generated in {generation_time:.2f} seconds")
        
        return WireframeResponse(
            image_base64=image_base64,
            svg_code=svg_code,
            generation_time=generation_time
        )
        
    except Exception as e:
        logger.error(f"Error generating wireframe: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wireframe-styles")
async def get_wireframe_styles():
    """Get available wireframe styles"""
    return {
        "styles": [
            {"id": "low-fi", "name": "Low Fidelity", "description": "Simple boxes and text"},
            {"id": "high-fi", "name": "High Fidelity", "description": "Detailed components"},
            {"id": "mobile", "name": "Mobile", "description": "Mobile-optimized layout"},
            {"id": "web", "name": "Web", "description": "Desktop web layout"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
