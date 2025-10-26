"""
AI Model Management and Loading
"""

import logging
from typing import Optional
from PIL import Image
import asyncio
from .config import settings, get_ai_device

logger = logging.getLogger(__name__)


class AIManager:
    """Manages AI model loading and inference"""
    
    def __init__(self):
        self.device = get_ai_device()
        self.pipe = None
        self.controlnet = None
        self.is_loaded = False
        self.is_loading = False
        self._load_lock = asyncio.Lock()
        
        # Try to import AI dependencies
        try:
            import torch
            from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
            from controlnet_aux import CannyDetector
            
            self.torch = torch
            self.StableDiffusionControlNetPipeline = StableDiffusionControlNetPipeline
            self.ControlNetModel = ControlNetModel
            self.CannyDetector = CannyDetector
            self.ai_available = True
            
            logger.info(f"AI dependencies loaded successfully. Device: {self.device}")
            
        except ImportError as e:
            self.ai_available = False
            logger.warning(f"AI dependencies not available: {e}")
            logger.info("Running in basic mode without AI generation")
    
    @property
    def is_available(self) -> bool:
        """Check if AI is available"""
        return self.ai_available and settings.ai_enabled
    
    async def load_models(self) -> bool:
        """Load AI models asynchronously"""
        if not self.is_available:
            return False
            
        if self.is_loaded:
            return True
            
        async with self._load_lock:
            if self.is_loaded:  # Double-check after acquiring lock
                return True
                
            if self.is_loading:
                # Wait for ongoing loading
                while self.is_loading:
                    await asyncio.sleep(0.1)
                return self.is_loaded
            
            self.is_loading = True
            
            try:
                logger.info("Loading ControlNet wireframe model...")
                
                # Load ControlNet model
                self.controlnet = self.ControlNetModel.from_pretrained(
                    settings.controlnet_model,
                    cache_dir=settings.ai_model_cache_dir,
                    torch_dtype=self.torch.float16 if self.device == "cuda" else self.torch.float32
                )
                
                # Load Stable Diffusion pipeline
                logger.info("Loading Stable Diffusion pipeline...")
                self.pipe = self.StableDiffusionControlNetPipeline.from_pretrained(
                    settings.base_model,
                    controlnet=self.controlnet,
                    cache_dir=settings.ai_model_cache_dir,
                    torch_dtype=self.torch.float16 if self.device == "cuda" else self.torch.float32,
                    safety_checker=None,
                    requires_safety_checker=False
                )
                
                self.pipe = self.pipe.to(self.device)
                
                # Enable optimizations for CUDA
                if self.device == "cuda":
                    self.pipe.enable_model_cpu_offload()
                    try:
                        self.pipe.enable_xformers_memory_efficient_attention()
                    except Exception as e:
                        logger.warning(f"Could not enable xformers: {e}")
                
                self.is_loaded = True
                logger.info("AI models loaded successfully!")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load AI models: {e}")
                return False
            finally:
                self.is_loading = False
    
    async def generate_wireframe(
        self,
        prompt: str,
        condition_image: Image.Image,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5
    ) -> Optional[Image.Image]:
        """Generate AI-enhanced wireframe"""
        if not self.is_available:
            return None
        
        # Ensure models are loaded
        if not await self.load_models():
            return None
        
        try:
            logger.info(f"Generating AI wireframe with prompt: '{prompt}'")
            
            # Prepare prompt
            enhanced_prompt = f"wireframe, ui design, clean layout, {prompt}"
            negative_prompt = "photo, realistic, colorful, detailed, complex, cluttered, messy"
            
            # Generate wireframe
            result = self.pipe(
                prompt=enhanced_prompt,
                image=condition_image,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                negative_prompt=negative_prompt
            )
            
            return result.images[0]
            
        except Exception as e:
            logger.error(f"Error generating AI wireframe: {e}")
            return None
    
    def unload_models(self):
        """Unload models to free memory"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
        
        if self.controlnet is not None:
            del self.controlnet
            self.controlnet = None
        
        if self.ai_available and hasattr(self, 'torch'):
            if self.device == "cuda":
                self.torch.cuda.empty_cache()
        
        self.is_loaded = False
        logger.info("AI models unloaded")


# Global AI manager instance
ai_manager = AIManager()
