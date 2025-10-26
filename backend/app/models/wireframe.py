"""
Wireframe data models and schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class LayoutType(str, Enum):
    """Supported layout types"""
    WEB_DESKTOP = "web-desktop"
    WEB_MOBILE = "web-mobile"
    MOBILE_APP = "mobile-app"
    DASHBOARD = "dashboard"
    LANDING_PAGE = "landing-page"
    FORM = "form"
    ECOMMERCE = "ecommerce"
    BLOG = "blog"


class WireframeStyle(str, Enum):
    """Wireframe fidelity styles"""
    LOW_FI = "low-fi"
    MID_FI = "mid-fi"
    HIGH_FI = "high-fi"
    SKETCH = "sketch"


class ComponentType(str, Enum):
    """UI component types"""
    HEADER = "header"
    NAVIGATION = "navigation"
    HERO = "hero"
    SIDEBAR = "sidebar"
    CONTENT = "content"
    FOOTER = "footer"
    FORM = "form"
    BUTTON = "button"
    IMAGE = "image"
    TEXT = "text"
    CARD = "card"
    LIST = "list"
    TABLE = "table"
    CHART = "chart"


class WireframeComponent(BaseModel):
    """Individual wireframe component"""
    type: ComponentType
    label: str
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any] = Field(default_factory=dict)
    children: List['WireframeComponent'] = Field(default_factory=list)


class WireframeRequest(BaseModel):
    """Request model for wireframe generation"""
    prompt: str = Field(..., description="Natural language description of the wireframe")
    layout_type: LayoutType = Field(default=LayoutType.WEB_DESKTOP, description="Type of layout to generate")
    style: WireframeStyle = Field(default=WireframeStyle.LOW_FI, description="Wireframe fidelity style")
    width: int = Field(default=1200, ge=200, le=2000, description="Canvas width in pixels")
    height: int = Field(default=800, ge=200, le=2000, description="Canvas height in pixels")
    color_scheme: Optional[str] = Field(default="monochrome", description="Color scheme preference")
    include_annotations: bool = Field(default=True, description="Include component labels and annotations")
    responsive: bool = Field(default=False, description="Generate responsive breakpoints")
    
    # AI-specific parameters
    use_ai: bool = Field(default=True, description="Use AI enhancement if available")
    num_inference_steps: int = Field(default=20, ge=1, le=50, description="AI inference steps")
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0, description="AI guidance scale")


class WireframeResponse(BaseModel):
    """Response model for generated wireframe"""
    id: str = Field(..., description="Unique wireframe ID")
    image_base64: str = Field(..., description="Generated wireframe as base64 PNG")
    svg_code: str = Field(..., description="SVG representation of the wireframe")
    components: List[WireframeComponent] = Field(..., description="Structured component data")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")
    generation_time: float = Field(..., description="Time taken to generate in seconds")
    layout_type: LayoutType = Field(..., description="Detected/used layout type")
    style: WireframeStyle = Field(..., description="Applied wireframe style")


class WireframeTemplate(BaseModel):
    """Predefined wireframe template"""
    id: str
    name: str
    description: str
    layout_type: LayoutType
    components: List[WireframeComponent]
    preview_image: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class StyleGuide(BaseModel):
    """Style guide for wireframe generation"""
    name: str
    colors: Dict[str, str]
    fonts: Dict[str, str]
    spacing: Dict[str, int]
    border_radius: int = 4
    line_width: int = 2


# Update forward references
WireframeComponent.model_rebuild()
