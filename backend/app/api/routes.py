"""
API routes for wireframe generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from typing import List, Dict, Any

from ..models.wireframe import (
    WireframeRequest, WireframeResponse, WireframeStyle, 
    LayoutType, WireframeTemplate
)
from ..services.wireframe_generator import WireframeGenerator
from ..core.ai_manager import ai_manager
from ..core.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
wireframe_generator = WireframeGenerator()


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "status": "running"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "ai_available": ai_manager.is_available,
        "ai_loaded": ai_manager.is_loaded,
        "device": ai_manager.device,
        "mode": "AI-enhanced" if ai_manager.is_available else "Algorithmic wireframes"
    }


@router.get("/wireframe-styles")
async def get_wireframe_styles():
    """Get available wireframe styles"""
    styles = [
        {
            "id": WireframeStyle.LOW_FI,
            "name": "Low Fidelity",
            "description": "Simple, clean wireframes with basic shapes and minimal detail"
        },
        {
            "id": WireframeStyle.MID_FI,
            "name": "Mid Fidelity", 
            "description": "Balanced wireframes with moderate detail and structure"
        },
        {
            "id": WireframeStyle.HIGH_FI,
            "name": "High Fidelity",
            "description": "Detailed wireframes with refined elements and realistic proportions"
        },
        {
            "id": WireframeStyle.SKETCH,
            "name": "Sketch Style",
            "description": "Hand-drawn style wireframes with artistic, sketchy appearance"
        }
    ]
    
    return {"styles": styles}


@router.get("/layout-types")
async def get_layout_types():
    """Get available layout types"""
    layouts = [
        {
            "id": LayoutType.WEB_DESKTOP,
            "name": "Web Desktop",
            "description": "Standard desktop web page layout"
        },
        {
            "id": LayoutType.WEB_MOBILE,
            "name": "Web Mobile",
            "description": "Mobile-responsive web page layout"
        },
        {
            "id": LayoutType.MOBILE_APP,
            "name": "Mobile App",
            "description": "Native mobile application interface"
        },
        {
            "id": LayoutType.DASHBOARD,
            "name": "Dashboard",
            "description": "Data dashboard with charts and metrics"
        },
        {
            "id": LayoutType.LANDING_PAGE,
            "name": "Landing Page",
            "description": "Marketing landing page with hero section"
        },
        {
            "id": LayoutType.FORM,
            "name": "Form",
            "description": "Form-focused layout for data input"
        },
        {
            "id": LayoutType.ECOMMERCE,
            "name": "E-commerce",
            "description": "Online store product listing and shopping"
        },
        {
            "id": LayoutType.BLOG,
            "name": "Blog",
            "description": "Blog or content publication layout"
        }
    ]
    
    return {"layout_types": layouts}


@router.post("/generate-wireframe", response_model=WireframeResponse)
async def generate_wireframe(request: WireframeRequest, background_tasks: BackgroundTasks):
    """Generate wireframe from text prompt"""
    try:
        logger.info(f"Received wireframe request: {request.prompt[:100]}...")
        
        # Validate request
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(request.prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt too long (max 1000 characters)")
        
        # Generate wireframe
        response = await wireframe_generator.generate_wireframe(request)
        
        # Log successful generation
        logger.info(f"Wireframe generated successfully: {response.id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating wireframe: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during wireframe generation")


@router.post("/analyze-prompt")
async def analyze_prompt(prompt_data: Dict[str, str]):
    """Analyze a prompt and return suggested parameters"""
    try:
        prompt = prompt_data.get("prompt", "")
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Use the prompt analyzer
        analysis = wireframe_generator.prompt_analyzer.analyze_prompt(prompt)
        
        return {
            "analysis": analysis,
            "suggestions": {
                "layout_type": analysis["layout_type"],
                "style": analysis["style"],
                "width": analysis["suggested_width"],
                "height": analysis["suggested_height"],
                "components": analysis["components"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing prompt")


@router.get("/templates")
async def get_templates():
    """Get predefined wireframe templates"""
    # This would typically come from a database
    templates = [
        {
            "id": "landing-hero",
            "name": "Landing Page with Hero",
            "description": "Marketing landing page with hero section, features, and CTA",
            "layout_type": LayoutType.LANDING_PAGE,
            "preview_url": "/templates/landing-hero.png",
            "tags": ["marketing", "hero", "cta"]
        },
        {
            "id": "dashboard-analytics",
            "name": "Analytics Dashboard",
            "description": "Data dashboard with charts, metrics, and sidebar navigation",
            "layout_type": LayoutType.DASHBOARD,
            "preview_url": "/templates/dashboard-analytics.png",
            "tags": ["dashboard", "analytics", "charts"]
        },
        {
            "id": "ecommerce-grid",
            "name": "Product Grid",
            "description": "E-commerce product listing with grid layout and filters",
            "layout_type": LayoutType.ECOMMERCE,
            "preview_url": "/templates/ecommerce-grid.png",
            "tags": ["ecommerce", "products", "grid"]
        },
        {
            "id": "mobile-app-tabs",
            "name": "Mobile App with Tabs",
            "description": "Mobile app interface with bottom tab navigation",
            "layout_type": LayoutType.MOBILE_APP,
            "preview_url": "/templates/mobile-app-tabs.png",
            "tags": ["mobile", "app", "tabs"]
        }
    ]
    
    return {"templates": templates}


@router.post("/ai/load-models")
async def load_ai_models(background_tasks: BackgroundTasks):
    """Load AI models in the background"""
    if not ai_manager.is_available:
        raise HTTPException(status_code=400, detail="AI functionality not available")
    
    if ai_manager.is_loaded:
        return {"message": "AI models already loaded", "status": "ready"}
    
    if ai_manager.is_loading:
        return {"message": "AI models currently loading", "status": "loading"}
    
    # Load models in background
    background_tasks.add_task(ai_manager.load_models)
    
    return {"message": "AI model loading started", "status": "loading"}


@router.get("/ai/status")
async def get_ai_status():
    """Get AI system status"""
    return {
        "available": ai_manager.is_available,
        "loaded": ai_manager.is_loaded,
        "loading": ai_manager.is_loading,
        "device": ai_manager.device,
        "model_info": {
            "controlnet_model": settings.controlnet_model,
            "base_model": settings.base_model
        } if ai_manager.is_available else None
    }


@router.post("/ai/unload-models")
async def unload_ai_models():
    """Unload AI models to free memory"""
    if not ai_manager.is_available:
        raise HTTPException(status_code=400, detail="AI functionality not available")
    
    ai_manager.unload_models()
    return {"message": "AI models unloaded successfully"}


@router.get("/stats")
async def get_stats():
    """Get API usage statistics"""
    # This would typically come from a database or metrics system
    return {
        "total_wireframes_generated": 0,  # Placeholder
        "ai_enhanced_count": 0,  # Placeholder
        "most_popular_layout": LayoutType.WEB_DESKTOP,
        "most_popular_style": WireframeStyle.LOW_FI,
        "average_generation_time": 0.5,  # Placeholder
        "uptime": "100%"  # Placeholder
    }
