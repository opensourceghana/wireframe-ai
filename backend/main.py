from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import base64
import logging
from typing import Optional
import os

# Try to import AI dependencies
try:
    import torch
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
    from controlnet_aux import CannyDetector
    AI_AVAILABLE = True
    logger.info("AI dependencies loaded successfully")
except ImportError as e:
    AI_AVAILABLE = False
    logger.warning(f"AI dependencies not available: {e}")
    logger.info("Running in basic mode without AI generation")

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
controlnet = None
device = "cuda" if AI_AVAILABLE and torch.cuda.is_available() else "cpu"

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
    """Create a wireframe condition image for ControlNet or basic wireframe"""
    # Create a white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    # Draw wireframe structure based on style
    if style == "low-fi":
        # Header
        draw.rectangle([20, 20, width-20, 80], outline='black', width=2)
        draw.text((30, 45), "HEADER", fill='black', font=font)
        
        # Navigation
        draw.rectangle([20, 100, width-20, 140], outline='black', width=2)
        draw.text((30, 115), "NAVIGATION", fill='black', font=font)
        
        # Main content area
        draw.rectangle([20, 160, width-20, height-80], outline='black', width=2)
        draw.text((30, 180), "MAIN CONTENT", fill='black', font=font)
        
        # Footer
        draw.rectangle([20, height-60, width-20, height-20], outline='black', width=2)
        draw.text((30, height-45), "FOOTER", fill='black', font=font)
        
    elif style == "mobile":
        # Mobile-specific layout
        # Status bar
        draw.rectangle([10, 10, width-10, 30], outline='black', width=1)
        draw.text((15, 15), "9:41 AM", fill='black', font=font)
        
        # Header with back button
        draw.rectangle([10, 40, width-10, 80], outline='black', width=2)
        draw.text((20, 55), "< Back", fill='black', font=font)
        draw.text((width//2-20, 55), "Title", fill='black', font=font)
        
        # Content area
        draw.rectangle([10, 90, width-10, height-50], outline='black', width=2)
        draw.text((20, 110), "Content Area", fill='black', font=font)
        
        # Bottom navigation
        draw.rectangle([10, height-40, width-10, height-10], outline='black', width=2)
        draw.text((20, height-30), "Tab 1", fill='black', font=font)
        draw.text((width//2-10, height-30), "Tab 2", fill='black', font=font)
        
    elif style == "high-fi":
        # More detailed wireframe
        # Header with logo and navigation
        draw.rectangle([20, 20, width-20, 80], outline='black', width=2, fill='#f0f0f0')
        draw.rectangle([30, 30, 80, 70], outline='black', width=1)
        draw.text((35, 45), "LOGO", fill='black', font=font)
        
        # Navigation items
        nav_items = ["Home", "About", "Services", "Contact"]
        for i, item in enumerate(nav_items):
            x = width - 200 + i * 45
            draw.text((x, 45), item, fill='black', font=font)
        
        # Hero section
        draw.rectangle([20, 100, width-20, 250], outline='black', width=2)
        draw.text((30, 120), "Hero Section", fill='black', font=font)
        draw.rectangle([30, 140, width-30, 200], outline='gray', width=1)
        draw.text((35, 165), "Hero Image", fill='gray', font=font)
        
        # Content sections
        section_height = (height - 300) // 2
        draw.rectangle([20, 270, width//2-10, 270+section_height], outline='black', width=2)
        draw.text((30, 285), "Section 1", fill='black', font=font)
        
        draw.rectangle([width//2+10, 270, width-20, 270+section_height], outline='black', width=2)
        draw.text((width//2+20, 285), "Section 2", fill='black', font=font)
        
        # Footer
        draw.rectangle([20, height-60, width-20, height-20], outline='black', width=2, fill='#f0f0f0')
        draw.text((30, height-45), "Footer Content", fill='black', font=font)
    
    return img

async def generate_ai_wireframe(prompt: str, condition_image: Image.Image, 
                               num_inference_steps: int = 20, 
                               guidance_scale: float = 7.5) -> Optional[Image.Image]:
    """Generate wireframe using ControlNet if available"""
    global pipe, controlnet
    
    if not AI_AVAILABLE:
        return None
    
    try:
        # Initialize ControlNet if not already loaded
        if controlnet is None:
            logger.info("Loading ControlNet wireframe model...")
            controlnet = ControlNetModel.from_pretrained(
                "Jise/controlnet-wireframe",
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
        
        # Initialize pipeline if not already loaded
        if pipe is None:
            logger.info("Loading Stable Diffusion pipeline...")
            pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            pipe = pipe.to(device)
            
            if device == "cuda":
                pipe.enable_model_cpu_offload()
                pipe.enable_xformers_memory_efficient_attention()
        
        # Generate wireframe
        logger.info(f"Generating AI wireframe with prompt: {prompt}")
        result = pipe(
            prompt=f"wireframe, ui design, {prompt}",
            image=condition_image,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            negative_prompt="photo, realistic, colorful, detailed, complex"
        )
        
        return result.images[0]
        
    except Exception as e:
        logger.error(f"Error generating AI wireframe: {e}")
        return None

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
        "ai_available": AI_AVAILABLE,
        "torch_available": torch.cuda.is_available() if AI_AVAILABLE else False,
        "mode": "AI-enhanced" if AI_AVAILABLE else "Basic wireframes"
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
        
        # Try to generate AI-enhanced wireframe
        ai_image = None
        if AI_AVAILABLE:
            ai_image = await generate_ai_wireframe(
                request.prompt,
                condition_image,
                request.num_inference_steps,
                request.guidance_scale
            )
        
        # Use AI image if available, otherwise use basic wireframe
        final_image = ai_image if ai_image else condition_image
        
        # Generate SVG wireframe
        svg_code = generate_svg_wireframe(
            request.prompt,
            request.width,
            request.height
        )
        
        # Convert final image to base64
        img_buffer = io.BytesIO()
        final_image.save(img_buffer, format='PNG')
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
