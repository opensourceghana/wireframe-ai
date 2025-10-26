"""
Main wireframe generation service
"""

import uuid
import time
import logging
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import io
import base64

from ..models.wireframe import (
    WireframeRequest, WireframeResponse, WireframeComponent,
    ComponentType, LayoutType, WireframeStyle
)
from ..core.ai_manager import ai_manager
from .prompt_analyzer import PromptAnalyzer
from .layout_engine import LayoutEngine

logger = logging.getLogger(__name__)


class WireframeGenerator:
    """Main service for generating intelligent wireframes"""
    
    def __init__(self):
        self.prompt_analyzer = PromptAnalyzer()
        self.layout_engine = LayoutEngine()
        
        # Load default font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            self.title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            self.font = ImageFont.load_default()
            self.title_font = ImageFont.load_default()
    
    async def generate_wireframe(self, request: WireframeRequest) -> WireframeResponse:
        """Generate a complete wireframe from request"""
        start_time = time.time()
        wireframe_id = str(uuid.uuid4())
        
        logger.info(f"Generating wireframe {wireframe_id} for prompt: '{request.prompt}'")
        
        try:
            # 1. Analyze the prompt
            analysis = self.prompt_analyzer.analyze_prompt(request.prompt)
            logger.info(f"Prompt analysis: {analysis}")
            
            # 2. Update request with analyzed data if not explicitly set
            if request.layout_type == LayoutType.WEB_DESKTOP and analysis["layout_type"] != LayoutType.WEB_DESKTOP:
                request.layout_type = analysis["layout_type"]
            
            if request.width == 1200 and request.height == 800:
                request.width = analysis["suggested_width"]
                request.height = analysis["suggested_height"]
            
            # 3. Generate component layout
            components = self.layout_engine.generate_layout(
                request, 
                analysis["components"]
            )
            
            # 4. Create base wireframe image
            base_image = self._create_wireframe_image(request, components)
            
            # 5. Try AI enhancement if available and requested
            final_image = base_image
            ai_enhanced = False
            
            if request.use_ai and ai_manager.is_available:
                try:
                    ai_image = await ai_manager.generate_wireframe(
                        request.prompt,
                        base_image,
                        request.num_inference_steps,
                        request.guidance_scale
                    )
                    if ai_image:
                        final_image = ai_image
                        ai_enhanced = True
                        logger.info("AI enhancement applied successfully")
                except Exception as e:
                    logger.warning(f"AI enhancement failed, using base wireframe: {e}")
            
            # 6. Generate SVG representation
            svg_code = self._generate_svg(request, components)
            
            # 7. Convert to base64
            image_base64 = self._image_to_base64(final_image)
            
            # 8. Create response
            generation_time = time.time() - start_time
            
            response = WireframeResponse(
                id=wireframe_id,
                image_base64=image_base64,
                svg_code=svg_code,
                components=components,
                metadata={
                    "prompt_analysis": analysis,
                    "ai_enhanced": ai_enhanced,
                    "generation_method": "ai" if ai_enhanced else "algorithmic",
                    "component_count": len(components),
                    "canvas_size": f"{request.width}x{request.height}"
                },
                generation_time=generation_time,
                layout_type=request.layout_type,
                style=request.style
            )
            
            logger.info(f"Wireframe {wireframe_id} generated successfully in {generation_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error generating wireframe {wireframe_id}: {e}")
            raise
    
    def _create_wireframe_image(
        self, 
        request: WireframeRequest, 
        components: List[WireframeComponent]
    ) -> Image.Image:
        """Create the base wireframe image"""
        
        # Create canvas
        image = Image.new('RGB', (request.width, request.height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Style configuration
        style_config = self._get_style_config(request.style)
        
        # Draw components
        for component in components:
            self._draw_component(draw, component, style_config, request.include_annotations)
        
        return image
    
    def _draw_component(
        self, 
        draw: ImageDraw.Draw, 
        component: WireframeComponent,
        style_config: Dict[str, Any],
        include_annotations: bool = True
    ):
        """Draw a single component on the canvas"""
        
        x, y, w, h = component.x, component.y, component.width, component.height
        
        # Component-specific drawing
        if component.type == ComponentType.HEADER:
            self._draw_header(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.NAVIGATION:
            self._draw_navigation(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.HERO:
            self._draw_hero(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.CONTENT:
            self._draw_content(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.SIDEBAR:
            self._draw_sidebar(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.FOOTER:
            self._draw_footer(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.FORM:
            self._draw_form(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.BUTTON:
            self._draw_button(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.CARD:
            self._draw_card(draw, x, y, w, h, component, style_config)
        elif component.type == ComponentType.CHART:
            self._draw_chart(draw, x, y, w, h, component, style_config)
        else:
            # Generic component
            self._draw_generic(draw, x, y, w, h, component, style_config)
        
        # Add label if annotations are enabled
        if include_annotations and component.label:
            self._draw_label(draw, x, y, component.label, style_config)
    
    def _draw_header(self, draw, x, y, w, h, component, style):
        """Draw header component"""
        # Background
        if component.properties.get("background"):
            draw.rectangle([x, y, x+w, y+h], fill=style["bg_color"], outline=style["border_color"], width=style["line_width"])
        else:
            draw.rectangle([x, y, x+w, y+h], outline=style["border_color"], width=style["line_width"])
        
        # Logo area
        if component.properties.get("logo"):
            logo_w = min(120, w // 4)
            draw.rectangle([x+16, y+12, x+16+logo_w, y+h-12], outline=style["accent_color"], width=1)
            draw.text((x+20, y+h//2-6), "LOGO", fill=style["text_color"], font=self.font)
        
        # Navigation items (if in header)
        if component.properties.get("navigation"):
            nav_items = ["Home", "About", "Services", "Contact"]
            item_width = 80
            start_x = x + w - len(nav_items) * item_width - 20
            
            for i, item in enumerate(nav_items):
                item_x = start_x + i * item_width
                draw.text((item_x, y+h//2-6), item, fill=style["text_color"], font=self.font)
        
        # User menu
        if component.properties.get("user_menu"):
            draw.circle((x+w-40, y+h//2), 12, outline=style["border_color"], width=1)
    
    def _draw_navigation(self, draw, x, y, w, h, component, style):
        """Draw navigation component"""
        draw.rectangle([x, y, x+w, y+h], outline=style["border_color"], width=style["line_width"])
        
        if component.properties.get("tabs"):
            tabs = component.properties["tabs"]
            tab_width = w // len(tabs)
            
            for i, tab in enumerate(tabs):
                tab_x = x + i * tab_width
                if i > 0:
                    draw.line([tab_x, y, tab_x, y+h], fill=style["border_color"], width=1)
                
                # Tab text
                text_x = tab_x + tab_width//2 - len(tab)*3
                draw.text((text_x, y+h//2-6), tab, fill=style["text_color"], font=self.font)
        
        # Back button for mobile
        if component.properties.get("has_back_button"):
            draw.text((x+16, y+h//2-6), "< Back", fill=style["accent_color"], font=self.font)
            
            # Title
            title = component.properties.get("title", "Title")
            title_x = x + w//2 - len(title)*4
            draw.text((title_x, y+h//2-6), title, fill=style["text_color"], font=self.title_font)
    
    def _draw_hero(self, draw, x, y, w, h, component, style):
        """Draw hero section"""
        # Background
        draw.rectangle([x, y, x+w, y+h], fill=style["bg_light"], outline=style["border_color"], width=style["line_width"])
        
        # Hero image placeholder
        if component.properties.get("background_image"):
            img_h = h // 2
            draw.rectangle([x+40, y+40, x+w-40, y+40+img_h], outline=style["border_color"], width=1)
            draw.text((x+w//2-30, y+40+img_h//2-6), "Hero Image", fill=style["text_light"], font=self.font)
        
        # Headline
        if component.properties.get("headline"):
            headline_y = y + h//2 + 20
            draw.text((x+40, headline_y), "Main Headline", fill=style["text_color"], font=self.title_font)
        
        # Subheadline
        if component.properties.get("subheadline"):
            sub_y = y + h//2 + 50
            draw.text((x+40, sub_y), "Supporting text and description", fill=style["text_color"], font=self.font)
        
        # CTA Button
        if component.properties.get("cta_button"):
            btn_w, btn_h = 120, 40
            btn_x = x + 40
            btn_y = y + h//2 + 80
            draw.rectangle([btn_x, btn_y, btn_x+btn_w, btn_y+btn_h], fill=style["accent_color"], outline=style["accent_color"])
            draw.text((btn_x+25, btn_y+btn_h//2-6), "Get Started", fill="white", font=self.font)
    
    def _draw_content(self, draw, x, y, w, h, component, style):
        """Draw content area"""
        draw.rectangle([x, y, x+w, y+h], outline=style["border_color"], width=style["line_width"])
        
        # Content lines
        line_height = 20
        lines = min(h // line_height - 2, 10)
        
        for i in range(lines):
            line_y = y + 20 + i * line_height
            line_w = w - 40 if i % 3 == 0 else w - 60  # Vary line lengths
            draw.rectangle([x+20, line_y, x+20+line_w, line_y+2], fill=style["text_light"])
    
    def _draw_sidebar(self, draw, x, y, w, h, component, style):
        """Draw sidebar"""
        draw.rectangle([x, y, x+w, y+h], fill=style["bg_light"], outline=style["border_color"], width=style["line_width"])
        
        # Navigation items
        if component.properties.get("navigation_items"):
            items = component.properties["navigation_items"]
            item_height = 40
            
            for i, item in enumerate(items):
                item_y = y + 20 + i * item_height
                if i == 0:  # Highlight first item
                    draw.rectangle([x+8, item_y-4, x+w-8, item_y+24], fill=style["accent_light"])
                
                draw.text((x+16, item_y), item, fill=style["text_color"], font=self.font)
    
    def _draw_footer(self, draw, x, y, w, h, component, style):
        """Draw footer"""
        draw.rectangle([x, y, x+w, y+h], fill=style["bg_color"], outline=style["border_color"], width=style["line_width"])
        
        # Footer links
        if component.properties.get("links"):
            links = ["Privacy", "Terms", "Contact", "About"]
            link_width = 80
            start_x = x + 20
            
            for i, link in enumerate(links):
                link_x = start_x + i * link_width
                draw.text((link_x, y+20), link, fill=style["text_color"], font=self.font)
        
        # Copyright
        if component.properties.get("copyright"):
            draw.text((x+20, y+h-30), "© 2024 Company Name", fill=style["text_light"], font=self.font)
    
    def _draw_form(self, draw, x, y, w, h, component, style):
        """Draw form field"""
        # Field background
        draw.rectangle([x, y, x+w, y+h], fill="white", outline=style["border_color"], width=1)
        
        # Placeholder text
        placeholder = component.properties.get("placeholder", component.label)
        draw.text((x+12, y+h//2-6), placeholder, fill=style["text_light"], font=self.font)
    
    def _draw_button(self, draw, x, y, w, h, component, style):
        """Draw button"""
        is_primary = component.properties.get("primary", False)
        
        if is_primary:
            draw.rectangle([x, y, x+w, y+h], fill=style["accent_color"], outline=style["accent_color"])
            text_color = "white"
        else:
            draw.rectangle([x, y, x+w, y+h], outline=style["border_color"], width=style["line_width"])
            text_color = style["text_color"]
        
        # Button text
        text = component.properties.get("text", component.label)
        text_x = x + w//2 - len(text)*4
        draw.text((text_x, y+h//2-6), text, fill=text_color, font=self.font)
    
    def _draw_card(self, draw, x, y, w, h, component, style):
        """Draw card component"""
        draw.rectangle([x, y, x+w, y+h], fill="white", outline=style["border_color"], width=1)
        
        # Image area
        if component.properties.get("image"):
            img_h = h // 2
            draw.rectangle([x+8, y+8, x+w-8, y+8+img_h], fill=style["bg_light"], outline=style["border_color"])
            draw.text((x+w//2-20, y+8+img_h//2-6), "Image", fill=style["text_light"], font=self.font)
        
        # Title
        if component.properties.get("title"):
            draw.text((x+12, y+h//2+10), "Card Title", fill=style["text_color"], font=self.title_font)
        
        # Price (for product cards)
        if component.properties.get("price"):
            draw.text((x+12, y+h-30), "$99.99", fill=style["accent_color"], font=self.font)
    
    def _draw_chart(self, draw, x, y, w, h, component, style):
        """Draw chart component"""
        draw.rectangle([x, y, x+w, y+h], fill="white", outline=style["border_color"], width=style["line_width"])
        
        # Chart title
        chart_type = component.properties.get("chart_type", "chart")
        draw.text((x+12, y+12), component.label, fill=style["text_color"], font=self.title_font)
        
        # Simple chart visualization
        chart_area_y = y + 40
        chart_area_h = h - 60
        
        if "line" in chart_type:
            # Draw line chart
            points = [(x+20, chart_area_y+chart_area_h-20), (x+w//3, chart_area_y+30), 
                     (x+2*w//3, chart_area_y+chart_area_h//2), (x+w-20, chart_area_y+20)]
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill=style["accent_color"], width=2)
        elif "bar" in chart_type:
            # Draw bar chart
            bars = 4
            bar_width = (w - 40) // bars - 10
            for i in range(bars):
                bar_x = x + 20 + i * (bar_width + 10)
                bar_height = (i + 1) * chart_area_h // (bars + 1)
                bar_y = chart_area_y + chart_area_h - bar_height
                draw.rectangle([bar_x, bar_y, bar_x+bar_width, chart_area_y+chart_area_h], 
                             fill=style["accent_color"])
        else:
            # Generic chart placeholder
            draw.text((x+w//2-25, y+h//2-6), "Chart Data", fill=style["text_light"], font=self.font)
    
    def _draw_generic(self, draw, x, y, w, h, component, style):
        """Draw generic component"""
        draw.rectangle([x, y, x+w, y+h], outline=style["border_color"], width=style["line_width"])
        
        # Component type label
        label_x = x + w//2 - len(component.type.value)*4
        draw.text((label_x, y+h//2-6), component.type.value.upper(), fill=style["text_color"], font=self.font)
    
    def _draw_label(self, draw, x, y, label, style):
        """Draw component label"""
        # Small label above component
        draw.text((x, y-16), label, fill=style["accent_color"], font=self.font)
    
    def _get_style_config(self, style: WireframeStyle) -> Dict[str, Any]:
        """Get style configuration for drawing"""
        
        base_config = {
            "line_width": 2,
            "border_color": "#333333",
            "text_color": "#333333",
            "text_light": "#666666",
            "bg_color": "#f8f9fa",
            "bg_light": "#f1f3f4",
            "accent_color": "#007bff",
            "accent_light": "#e3f2fd"
        }
        
        if style == WireframeStyle.HIGH_FI:
            base_config.update({
                "line_width": 1,
                "border_color": "#dee2e6",
                "bg_color": "#ffffff",
                "bg_light": "#f8f9fa"
            })
        elif style == WireframeStyle.SKETCH:
            base_config.update({
                "line_width": 1,
                "border_color": "#666666",
                "text_color": "#444444"
            })
        
        return base_config
    
    def _generate_svg(self, request: WireframeRequest, components: List[WireframeComponent]) -> str:
        """Generate SVG representation of the wireframe"""
        
        svg_parts = [
            f'<svg width="{request.width}" height="{request.height}" xmlns="http://www.w3.org/2000/svg">',
            '<defs>',
            '<style>',
            '.wireframe-border { fill: none; stroke: #333; stroke-width: 2; }',
            '.wireframe-text { font-family: Arial, sans-serif; font-size: 12px; fill: #333; }',
            '.wireframe-bg { fill: #f8f9fa; stroke: #333; stroke-width: 1; }',
            '.wireframe-accent { fill: #007bff; }',
            '</style>',
            '</defs>'
        ]
        
        # Add components
        for component in components:
            svg_parts.append(self._component_to_svg(component))
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)
    
    def _component_to_svg(self, component: WireframeComponent) -> str:
        """Convert component to SVG element"""
        x, y, w, h = component.x, component.y, component.width, component.height
        
        svg = f'<g id="{component.type.value}-{id(component)}">'
        svg += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="wireframe-border"/>'
        
        # Add component label
        label_x = x + 8
        label_y = y + 20
        svg += f'<text x="{label_x}" y="{label_y}" class="wireframe-text">{component.label}</text>'
        
        svg += '</g>'
        return svg
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
