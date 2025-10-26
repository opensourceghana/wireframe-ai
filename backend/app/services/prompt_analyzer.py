"""
Intelligent prompt analysis for wireframe generation
"""

import re
from typing import List, Dict, Set, Tuple
from ..models.wireframe import LayoutType, ComponentType, WireframeStyle


class PromptAnalyzer:
    """Analyzes natural language prompts to extract wireframe requirements"""
    
    def __init__(self):
        self.layout_keywords = {
            LayoutType.LANDING_PAGE: [
                "landing", "homepage", "home page", "marketing", "hero section", 
                "call to action", "cta", "features", "testimonials"
            ],
            LayoutType.DASHBOARD: [
                "dashboard", "admin", "analytics", "charts", "metrics", "stats",
                "data visualization", "kpi", "overview", "control panel"
            ],
            LayoutType.ECOMMERCE: [
                "shop", "store", "ecommerce", "e-commerce", "product", "cart",
                "checkout", "payment", "catalog", "inventory", "buy", "purchase"
            ],
            LayoutType.FORM: [
                "form", "signup", "sign up", "register", "login", "contact",
                "survey", "questionnaire", "input", "fields", "submit"
            ],
            LayoutType.BLOG: [
                "blog", "article", "post", "news", "content", "reading",
                "publication", "journal", "magazine"
            ],
            LayoutType.MOBILE_APP: [
                "mobile", "app", "ios", "android", "phone", "touch",
                "swipe", "tab bar", "navigation bar", "mobile first"
            ],
            LayoutType.WEB_MOBILE: [
                "responsive", "mobile web", "mobile version", "phone web",
                "mobile responsive", "mobile friendly"
            ]
        }
        
        self.component_keywords = {
            ComponentType.HEADER: [
                "header", "top bar", "navigation bar", "nav bar", "menu bar",
                "title bar", "brand", "logo area"
            ],
            ComponentType.NAVIGATION: [
                "navigation", "nav", "menu", "sidebar", "side menu",
                "breadcrumb", "tabs", "links"
            ],
            ComponentType.HERO: [
                "hero", "banner", "main banner", "featured", "spotlight",
                "hero section", "main visual", "key visual"
            ],
            ComponentType.FORM: [
                "form", "input", "field", "text field", "email field",
                "password", "submit", "button", "checkbox", "radio"
            ],
            ComponentType.CONTENT: [
                "content", "main content", "body", "text", "paragraph",
                "description", "details", "information"
            ],
            ComponentType.SIDEBAR: [
                "sidebar", "side panel", "aside", "secondary nav",
                "filters", "categories"
            ],
            ComponentType.FOOTER: [
                "footer", "bottom", "copyright", "links", "contact info",
                "social media", "newsletter"
            ],
            ComponentType.CARD: [
                "card", "tile", "box", "panel", "item", "product card",
                "feature card", "info card"
            ],
            ComponentType.LIST: [
                "list", "items", "menu items", "options", "choices",
                "catalog", "directory"
            ],
            ComponentType.TABLE: [
                "table", "grid", "data table", "spreadsheet", "rows",
                "columns", "data grid"
            ],
            ComponentType.CHART: [
                "chart", "graph", "visualization", "analytics", "metrics",
                "statistics", "data viz", "plot"
            ],
            ComponentType.IMAGE: [
                "image", "photo", "picture", "gallery", "thumbnail",
                "media", "visual", "illustration"
            ]
        }
        
        self.style_keywords = {
            WireframeStyle.LOW_FI: [
                "simple", "basic", "minimal", "clean", "low fidelity",
                "sketch", "rough", "wireframe"
            ],
            WireframeStyle.MID_FI: [
                "medium", "moderate", "balanced", "mid fidelity",
                "structured", "organized"
            ],
            WireframeStyle.HIGH_FI: [
                "detailed", "polished", "refined", "high fidelity",
                "professional", "complete", "finished"
            ],
            WireframeStyle.SKETCH: [
                "hand drawn", "sketchy", "artistic", "rough sketch",
                "pencil", "drawn", "sketch style"
            ]
        }
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """Analyze prompt and extract wireframe requirements"""
        prompt_lower = prompt.lower()
        
        # Detect layout type
        layout_type = self._detect_layout_type(prompt_lower)
        
        # Extract components
        components = self._extract_components(prompt_lower)
        
        # Determine style
        style = self._detect_style(prompt_lower)
        
        # Extract specific requirements
        requirements = self._extract_requirements(prompt_lower)
        
        # Suggest dimensions based on layout type
        dimensions = self._suggest_dimensions(layout_type)
        
        return {
            "layout_type": layout_type,
            "components": components,
            "style": style,
            "requirements": requirements,
            "suggested_width": dimensions[0],
            "suggested_height": dimensions[1],
            "confidence": self._calculate_confidence(prompt_lower, layout_type, components)
        }
    
    def _detect_layout_type(self, prompt: str) -> LayoutType:
        """Detect the most likely layout type from prompt"""
        scores = {}
        
        for layout_type, keywords in self.layout_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt)
            if score > 0:
                scores[layout_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # Default based on common patterns
        if any(word in prompt for word in ["login", "signup", "register", "contact"]):
            return LayoutType.FORM
        elif any(word in prompt for word in ["mobile", "app", "phone"]):
            return LayoutType.MOBILE_APP
        else:
            return LayoutType.WEB_DESKTOP
    
    def _extract_components(self, prompt: str) -> List[ComponentType]:
        """Extract likely components from prompt"""
        found_components = set()
        
        for component_type, keywords in self.component_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                found_components.add(component_type)
        
        # Add implied components based on layout type
        layout_type = self._detect_layout_type(prompt)
        implied = self._get_implied_components(layout_type)
        found_components.update(implied)
        
        return list(found_components)
    
    def _detect_style(self, prompt: str) -> WireframeStyle:
        """Detect wireframe style preference"""
        for style, keywords in self.style_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                return style
        
        return WireframeStyle.LOW_FI  # Default
    
    def _extract_requirements(self, prompt: str) -> Dict:
        """Extract specific requirements and constraints"""
        requirements = {
            "responsive": any(word in prompt for word in ["responsive", "mobile friendly", "adaptive"]),
            "dark_mode": any(word in prompt for word in ["dark", "dark mode", "night mode"]),
            "accessibility": any(word in prompt for word in ["accessible", "a11y", "accessibility"]),
            "animations": any(word in prompt for word in ["animated", "animation", "interactive"]),
            "search": "search" in prompt,
            "user_auth": any(word in prompt for word in ["login", "signup", "register", "auth"]),
            "social_features": any(word in prompt for word in ["social", "share", "like", "comment"]),
            "ecommerce": any(word in prompt for word in ["cart", "checkout", "payment", "buy"])
        }
        
        return requirements
    
    def _suggest_dimensions(self, layout_type: LayoutType) -> Tuple[int, int]:
        """Suggest optimal dimensions based on layout type"""
        dimension_map = {
            LayoutType.WEB_DESKTOP: (1200, 800),
            LayoutType.WEB_MOBILE: (375, 667),
            LayoutType.MOBILE_APP: (375, 812),
            LayoutType.DASHBOARD: (1440, 900),
            LayoutType.LANDING_PAGE: (1200, 1200),
            LayoutType.FORM: (600, 800),
            LayoutType.ECOMMERCE: (1200, 1000),
            LayoutType.BLOG: (800, 1000)
        }
        
        return dimension_map.get(layout_type, (1200, 800))
    
    def _get_implied_components(self, layout_type: LayoutType) -> Set[ComponentType]:
        """Get components typically found in each layout type"""
        component_map = {
            LayoutType.WEB_DESKTOP: {ComponentType.HEADER, ComponentType.NAVIGATION, ComponentType.CONTENT, ComponentType.FOOTER},
            LayoutType.WEB_MOBILE: {ComponentType.HEADER, ComponentType.NAVIGATION, ComponentType.CONTENT},
            LayoutType.MOBILE_APP: {ComponentType.HEADER, ComponentType.CONTENT},
            LayoutType.DASHBOARD: {ComponentType.HEADER, ComponentType.SIDEBAR, ComponentType.CONTENT, ComponentType.CHART},
            LayoutType.LANDING_PAGE: {ComponentType.HEADER, ComponentType.HERO, ComponentType.CONTENT, ComponentType.FOOTER},
            LayoutType.FORM: {ComponentType.HEADER, ComponentType.FORM, ComponentType.BUTTON},
            LayoutType.ECOMMERCE: {ComponentType.HEADER, ComponentType.NAVIGATION, ComponentType.CONTENT, ComponentType.CARD, ComponentType.FOOTER},
            LayoutType.BLOG: {ComponentType.HEADER, ComponentType.NAVIGATION, ComponentType.CONTENT, ComponentType.SIDEBAR, ComponentType.FOOTER}
        }
        
        return component_map.get(layout_type, {ComponentType.HEADER, ComponentType.CONTENT})
    
    def _calculate_confidence(self, prompt: str, layout_type: LayoutType, components: List[ComponentType]) -> float:
        """Calculate confidence score for the analysis"""
        base_score = 0.5
        
        # Boost confidence if layout keywords are found
        layout_keywords = self.layout_keywords.get(layout_type, [])
        layout_matches = sum(1 for keyword in layout_keywords if keyword in prompt)
        layout_boost = min(layout_matches * 0.1, 0.3)
        
        # Boost confidence if component keywords are found
        component_boost = min(len(components) * 0.05, 0.2)
        
        confidence = base_score + layout_boost + component_boost
        return min(confidence, 1.0)
