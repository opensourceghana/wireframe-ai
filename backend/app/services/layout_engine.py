"""
Intelligent layout engine for wireframe component positioning
"""

from typing import List, Dict, Tuple, Optional
from ..models.wireframe import (
    WireframeComponent, ComponentType, LayoutType, 
    WireframeStyle, WireframeRequest
)
import math


class LayoutEngine:
    """Generates intelligent layouts based on design principles"""
    
    def __init__(self):
        self.grid_size = 8  # Base grid unit for alignment
        self.margin = 20
        self.component_spacing = 16
        
        # Component priority for layout ordering
        self.component_priority = {
            ComponentType.HEADER: 1,
            ComponentType.NAVIGATION: 2,
            ComponentType.HERO: 3,
            ComponentType.SIDEBAR: 4,
            ComponentType.CONTENT: 5,
            ComponentType.FORM: 6,
            ComponentType.CARD: 7,
            ComponentType.LIST: 8,
            ComponentType.TABLE: 9,
            ComponentType.CHART: 10,
            ComponentType.IMAGE: 11,
            ComponentType.TEXT: 12,
            ComponentType.BUTTON: 13,
            ComponentType.FOOTER: 14
        }
    
    def generate_layout(
        self, 
        request: WireframeRequest, 
        components: List[ComponentType]
    ) -> List[WireframeComponent]:
        """Generate intelligent layout for components"""
        
        canvas_width = request.width
        canvas_height = request.height
        layout_type = request.layout_type
        style = request.style
        
        # Sort components by priority
        sorted_components = sorted(
            components, 
            key=lambda c: self.component_priority.get(c, 99)
        )
        
        # Generate layout based on type
        if layout_type == LayoutType.MOBILE_APP:
            return self._generate_mobile_layout(sorted_components, canvas_width, canvas_height, style)
        elif layout_type == LayoutType.DASHBOARD:
            return self._generate_dashboard_layout(sorted_components, canvas_width, canvas_height, style)
        elif layout_type == LayoutType.LANDING_PAGE:
            return self._generate_landing_layout(sorted_components, canvas_width, canvas_height, style)
        elif layout_type == LayoutType.FORM:
            return self._generate_form_layout(sorted_components, canvas_width, canvas_height, style)
        elif layout_type == LayoutType.ECOMMERCE:
            return self._generate_ecommerce_layout(sorted_components, canvas_width, canvas_height, style)
        elif layout_type == LayoutType.BLOG:
            return self._generate_blog_layout(sorted_components, canvas_width, canvas_height, style)
        else:
            return self._generate_web_layout(sorted_components, canvas_width, canvas_height, style)
    
    def _generate_mobile_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate mobile app layout"""
        layout = []
        current_y = 0
        
        # Status bar (if mobile)
        if ComponentType.HEADER in components:
            status_bar = WireframeComponent(
                type=ComponentType.HEADER,
                label="Status Bar",
                x=0,
                y=current_y,
                width=width,
                height=44,
                properties={"background": "#f8f9fa", "text": "9:41 AM"}
            )
            layout.append(status_bar)
            current_y += 44
            
            # Navigation header
            nav_header = WireframeComponent(
                type=ComponentType.NAVIGATION,
                label="Navigation Header",
                x=0,
                y=current_y,
                width=width,
                height=56,
                properties={"has_back_button": True, "title": "Screen Title"}
            )
            layout.append(nav_header)
            current_y += 56 + self.component_spacing
        
        # Main content area
        if ComponentType.CONTENT in components:
            content_height = height - current_y - 80  # Reserve space for bottom nav
            content = WireframeComponent(
                type=ComponentType.CONTENT,
                label="Main Content",
                x=self.margin,
                y=current_y,
                width=width - (2 * self.margin),
                height=content_height,
                properties={"scrollable": True}
            )
            layout.append(content)
        
        # Bottom navigation (if navigation exists)
        if ComponentType.NAVIGATION in components and len([c for c in components if c == ComponentType.NAVIGATION]) > 1:
            bottom_nav = WireframeComponent(
                type=ComponentType.NAVIGATION,
                label="Bottom Navigation",
                x=0,
                y=height - 80,
                width=width,
                height=80,
                properties={"tabs": ["Home", "Search", "Profile", "More"]}
            )
            layout.append(bottom_nav)
        
        return layout
    
    def _generate_dashboard_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate dashboard layout"""
        layout = []
        
        # Header
        if ComponentType.HEADER in components:
            header = WireframeComponent(
                type=ComponentType.HEADER,
                label="Dashboard Header",
                x=0,
                y=0,
                width=width,
                height=60,
                properties={"logo": True, "user_menu": True, "search": True}
            )
            layout.append(header)
        
        # Sidebar
        sidebar_width = 250
        content_x = 0
        content_width = width
        
        if ComponentType.SIDEBAR in components:
            sidebar = WireframeComponent(
                type=ComponentType.SIDEBAR,
                label="Navigation Sidebar",
                x=0,
                y=60,
                width=sidebar_width,
                height=height - 60,
                properties={"navigation_items": ["Dashboard", "Analytics", "Users", "Settings"]}
            )
            layout.append(sidebar)
            content_x = sidebar_width + self.component_spacing
            content_width = width - sidebar_width - self.component_spacing
        
        # Main content area with charts
        if ComponentType.CHART in components:
            # Create a grid of charts
            chart_grid = self._create_chart_grid(
                content_x + self.margin,
                60 + self.margin,
                content_width - (2 * self.margin),
                height - 60 - (2 * self.margin),
                components.count(ComponentType.CHART) or 4
            )
            layout.extend(chart_grid)
        
        return layout
    
    def _generate_landing_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate landing page layout"""
        layout = []
        current_y = 0
        
        # Header with navigation
        if ComponentType.HEADER in components:
            header = WireframeComponent(
                type=ComponentType.HEADER,
                label="Site Header",
                x=0,
                y=current_y,
                width=width,
                height=80,
                properties={"logo": True, "navigation": True, "cta_button": True}
            )
            layout.append(header)
            current_y += 80
        
        # Hero section
        if ComponentType.HERO in components:
            hero = WireframeComponent(
                type=ComponentType.HERO,
                label="Hero Section",
                x=0,
                y=current_y,
                width=width,
                height=400,
                properties={
                    "headline": True, 
                    "subheadline": True, 
                    "cta_button": True,
                    "background_image": True
                }
            )
            layout.append(hero)
            current_y += 400 + self.component_spacing
        
        # Content sections
        if ComponentType.CONTENT in components:
            # Create multiple content sections
            section_height = 300
            sections = ["Features", "Benefits", "Testimonials"]
            
            for i, section_name in enumerate(sections):
                section = WireframeComponent(
                    type=ComponentType.CONTENT,
                    label=f"{section_name} Section",
                    x=self.margin,
                    y=current_y,
                    width=width - (2 * self.margin),
                    height=section_height,
                    properties={"section_type": section_name.lower()}
                )
                layout.append(section)
                current_y += section_height + self.component_spacing
        
        # Footer
        if ComponentType.FOOTER in components:
            footer = WireframeComponent(
                type=ComponentType.FOOTER,
                label="Site Footer",
                x=0,
                y=current_y,
                width=width,
                height=120,
                properties={"links": True, "social": True, "copyright": True}
            )
            layout.append(footer)
        
        return layout
    
    def _generate_form_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate form-focused layout"""
        layout = []
        
        # Center the form
        form_width = min(400, width - (2 * self.margin))
        form_x = (width - form_width) // 2
        current_y = self.margin * 2
        
        # Header
        if ComponentType.HEADER in components:
            header = WireframeComponent(
                type=ComponentType.HEADER,
                label="Form Title",
                x=form_x,
                y=current_y,
                width=form_width,
                height=60,
                properties={"title": "Sign Up", "subtitle": "Create your account"}
            )
            layout.append(header)
            current_y += 80
        
        # Form fields
        if ComponentType.FORM in components:
            form_fields = [
                "Email Address",
                "Password",
                "Confirm Password",
                "Full Name"
            ]
            
            for field_name in form_fields:
                field = WireframeComponent(
                    type=ComponentType.FORM,
                    label=field_name,
                    x=form_x,
                    y=current_y,
                    width=form_width,
                    height=48,
                    properties={"field_type": "input", "placeholder": field_name}
                )
                layout.append(field)
                current_y += 48 + 16
        
        # Submit button
        if ComponentType.BUTTON in components:
            button = WireframeComponent(
                type=ComponentType.BUTTON,
                label="Submit Button",
                x=form_x,
                y=current_y + 16,
                width=form_width,
                height=48,
                properties={"text": "Create Account", "primary": True}
            )
            layout.append(button)
        
        return layout
    
    def _generate_ecommerce_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate e-commerce layout"""
        layout = []
        current_y = 0
        
        # Header with search
        if ComponentType.HEADER in components:
            header = WireframeComponent(
                type=ComponentType.HEADER,
                label="Store Header",
                x=0,
                y=current_y,
                width=width,
                height=80,
                properties={"logo": True, "search": True, "cart": True, "account": True}
            )
            layout.append(header)
            current_y += 80
        
        # Navigation
        if ComponentType.NAVIGATION in components:
            nav = WireframeComponent(
                type=ComponentType.NAVIGATION,
                label="Category Navigation",
                x=0,
                y=current_y,
                width=width,
                height=50,
                properties={"categories": ["Electronics", "Clothing", "Home", "Sports"]}
            )
            layout.append(nav)
            current_y += 50 + self.component_spacing
        
        # Product grid
        if ComponentType.CARD in components:
            products_per_row = 4 if width > 1000 else 3 if width > 600 else 2
            card_width = (width - (2 * self.margin) - ((products_per_row - 1) * self.component_spacing)) // products_per_row
            card_height = card_width + 100  # Add space for product info
            
            rows = 3
            for row in range(rows):
                for col in range(products_per_row):
                    card_x = self.margin + col * (card_width + self.component_spacing)
                    card_y = current_y + row * (card_height + self.component_spacing)
                    
                    card = WireframeComponent(
                        type=ComponentType.CARD,
                        label=f"Product {row * products_per_row + col + 1}",
                        x=card_x,
                        y=card_y,
                        width=card_width,
                        height=card_height,
                        properties={"image": True, "title": True, "price": True, "rating": True}
                    )
                    layout.append(card)
        
        return layout
    
    def _generate_blog_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate blog layout"""
        layout = []
        current_y = 0
        
        # Header
        if ComponentType.HEADER in components:
            header = WireframeComponent(
                type=ComponentType.HEADER,
                label="Blog Header",
                x=0,
                y=current_y,
                width=width,
                height=80,
                properties={"site_title": True, "navigation": True, "search": True}
            )
            layout.append(header)
            current_y += 80 + self.component_spacing
        
        # Two-column layout
        sidebar_width = 300
        content_width = width - sidebar_width - (3 * self.margin)
        
        # Main content
        if ComponentType.CONTENT in components:
            content = WireframeComponent(
                type=ComponentType.CONTENT,
                label="Blog Posts",
                x=self.margin,
                y=current_y,
                width=content_width,
                height=height - current_y - 100,
                properties={"post_list": True, "pagination": True}
            )
            layout.append(content)
        
        # Sidebar
        if ComponentType.SIDEBAR in components:
            sidebar = WireframeComponent(
                type=ComponentType.SIDEBAR,
                label="Blog Sidebar",
                x=width - sidebar_width - self.margin,
                y=current_y,
                width=sidebar_width,
                height=height - current_y - 100,
                properties={"recent_posts": True, "categories": True, "tags": True}
            )
            layout.append(sidebar)
        
        return layout
    
    def _generate_web_layout(
        self, 
        components: List[ComponentType], 
        width: int, 
        height: int, 
        style: WireframeStyle
    ) -> List[WireframeComponent]:
        """Generate standard web layout"""
        layout = []
        current_y = 0
        
        # Header
        if ComponentType.HEADER in components:
            header = WireframeComponent(
                type=ComponentType.HEADER,
                label="Site Header",
                x=0,
                y=current_y,
                width=width,
                height=80,
                properties={"logo": True, "navigation": True}
            )
            layout.append(header)
            current_y += 80
        
        # Navigation (if separate from header)
        if ComponentType.NAVIGATION in components and ComponentType.HEADER in components:
            nav = WireframeComponent(
                type=ComponentType.NAVIGATION,
                label="Main Navigation",
                x=0,
                y=current_y,
                width=width,
                height=50,
                properties={"menu_items": ["Home", "About", "Services", "Contact"]}
            )
            layout.append(nav)
            current_y += 50 + self.component_spacing
        
        # Main content
        if ComponentType.CONTENT in components:
            content = WireframeComponent(
                type=ComponentType.CONTENT,
                label="Main Content",
                x=self.margin,
                y=current_y,
                width=width - (2 * self.margin),
                height=height - current_y - 120,  # Reserve space for footer
                properties={"scrollable": True}
            )
            layout.append(content)
        
        # Footer
        if ComponentType.FOOTER in components:
            footer = WireframeComponent(
                type=ComponentType.FOOTER,
                label="Site Footer",
                x=0,
                y=height - 100,
                width=width,
                height=100,
                properties={"copyright": True, "links": True}
            )
            layout.append(footer)
        
        return layout
    
    def _create_chart_grid(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        chart_count: int
    ) -> List[WireframeComponent]:
        """Create a grid of charts for dashboard"""
        charts = []
        
        # Determine grid dimensions
        cols = 2 if chart_count <= 4 else 3
        rows = math.ceil(chart_count / cols)
        
        chart_width = (width - ((cols - 1) * self.component_spacing)) // cols
        chart_height = (height - ((rows - 1) * self.component_spacing)) // rows
        
        chart_types = ["Line Chart", "Bar Chart", "Pie Chart", "Area Chart", "Metric Card"]
        
        for i in range(chart_count):
            row = i // cols
            col = i % cols
            
            chart_x = x + col * (chart_width + self.component_spacing)
            chart_y = y + row * (chart_height + self.component_spacing)
            
            chart = WireframeComponent(
                type=ComponentType.CHART,
                label=chart_types[i % len(chart_types)],
                x=chart_x,
                y=chart_y,
                width=chart_width,
                height=chart_height,
                properties={"chart_type": chart_types[i % len(chart_types)].lower().replace(" ", "_")}
            )
            charts.append(chart)
        
        return charts
