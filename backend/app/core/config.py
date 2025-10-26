"""
Application configuration and settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "AI Wireframing Tool"
    app_version: str = "1.0.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
    ]
    
    # AI Configuration
    ai_enabled: bool = True
    ai_device: str = "auto"  # auto, cpu, cuda
    ai_model_cache_dir: str = "./models"
    controlnet_model: str = "Jise/controlnet-wireframe"
    base_model: str = "runwayml/stable-diffusion-v1-5"
    
    # Generation Defaults
    default_width: int = 1200
    default_height: int = 800
    max_width: int = 2000
    max_height: int = 2000
    max_inference_steps: int = 50
    
    # Performance
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    max_concurrent_generations: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Storage
    output_dir: str = "./outputs"
    temp_dir: str = "./temp"
    
    class Config:
        env_file = ".env"
        env_prefix = "WIREFRAME_"


# Global settings instance
settings = Settings()


def get_ai_device() -> str:
    """Determine the best device for AI operations"""
    if settings.ai_device == "auto":
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"
    return settings.ai_device


def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        settings.ai_model_cache_dir,
        settings.output_dir,
        settings.temp_dir
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
