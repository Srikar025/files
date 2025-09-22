import streamlit as st
import google.generativeai as genai
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import json
import math
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from config import get_gemini_api_key

@dataclass
class KolamPattern:
    """Data class for Kolam pattern structure"""
    dots: List[Tuple[int, int]]
    connections: List[Tuple[Tuple[int, int], Tuple[int, int]]]
    pattern_type: str
    symmetry: str
    complexity: int
    description: str
    cultural_significance: str
    grid_size: int

class EnhancedKolamGenerator:
    """Enhanced AI-powered Kolam generator with mathematical precision"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Use provided API key or get from config
        self.api_key = api_key or get_gemini_api_key()
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                st.success("✅ AI guidance enabled with Gemini API")
            except Exception as e:
                self.model = None
                st.error(f"❌ Failed to initialize Gemini API: {str(e)}")
        else:
            self.model = None
            st.info("ℹ️ AI guidance disabled - API key not provided")
        
        # Traditional Kolam pattern templates
        self.pattern_templates = {
            'flower': self._create_flower_template,
            'lotus': self._create_lotus_template,
            'star': self._create_star_template,
            'diamond': self._create_diamond_template,
            'spiral': self._create_spiral_template,
            'mandala': self._create_mandala_template,
            'geometric': self._create_geometric_template,
            'traditional': self._create_traditional_template
        }
    
    def generate_kolam_from_prompt(self, prompt: str, grid_size: int = 7) -> Dict:
        """Generate accurate Kolam pattern from text prompt"""
        try:
            # Analyze prompt to extract pattern characteristics
            pattern_analysis = self._analyze_prompt(prompt)
            
            # Generate pattern using AI guidance and mathematical precision
            if self.model:
                ai_guidance = self._get_ai_guidance(prompt, grid_size)
                pattern_analysis.update(ai_guidance)
            
            # Create the actual pattern
            kolam_pattern = self._create_pattern_from_analysis(pattern_analysis, grid_size)
            
            return {
                "success": True,
                "pattern": kolam_pattern,
                "analysis": pattern_analysis,
                "prompt": prompt
            }
            
        except Exception as e:
            return {"error": f"Pattern generation failed: {str(e)}"}
    
    def _analyze_prompt(self, prompt: str) -> Dict:
        """Analyze user prompt to extract pattern characteristics"""
        prompt_lower = prompt.lower()
        
        analysis = {
            'pattern_type': 'geometric',
            'symmetry_type': 'bilateral',
            'complexity': 5,
            'elements': [],
            'style': 'traditional',
            'special_features': []
        }
        
        # Pattern type detection
        pattern_keywords = {
            'flower': ['flower', 'petal', 'bloom', 'floral'],
            'lotus': ['lotus', 'padma'],
            'star': ['star', 'stellar', 'pointed'],
            'diamond': ['diamond', 'rhombus'],
            'spiral': ['spiral', 'swirl', 'coil'],
            'mandala': ['mandala', 'circular', 'radial'],
            'geometric': ['geometric', 'square', 'triangle', 'polygon'],
            'traditional': ['traditional', 'classical', 'ancient']
        }
        
        for pattern_type, keywords in pattern_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                analysis['pattern_type'] = pattern_type
                break
        
        # Symmetry detection
        symmetry_keywords = {
            'rotational': ['rotational', 'rotate', 'spinning', 'radial'],
            'bilateral': ['bilateral', 'mirror', 'symmetric'],
            'point': ['point', 'central'],
            'none': ['asymmetric', 'irregular']
        }
        
        for symmetry, keywords in symmetry_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                analysis['symmetry_type'] = symmetry
                break
        
        # Complexity detection
        complexity_keywords = {
            1: ['very simple', 'basic', 'minimal'],
            3: ['simple', 'easy'],
            5: ['medium', 'moderate'],
            7: ['complex', 'detailed', 'intricate'],
            9: ['very complex', 'elaborate', 'sophisticated']
        }
        
        for level, keywords in complexity_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                analysis['complexity'] = level
                break
        
        # Number extraction (for petals, points, etc.)
        numbers = re.findall(r'\b(\d+)\b', prompt)
        if numbers:
            analysis['count'] = int(numbers[0])
        else:
            analysis['count'] = 8  # Default
        
        return analysis
    
    def _validate_ai_guidance(self, guidance: Dict) -> Dict:
        """Validate and sanitize AI guidance"""
        valid_patterns = ['flower', 'lotus', 'star', 'diamond', 'spiral', 'mandala', 'geometric', 'traditional']
        valid_symmetries = ['rotational', 'bilateral', 'point', 'radial']
        
        # Ensure valid pattern type
        if guidance.get('pattern_type') not in valid_patterns:
            guidance['pattern_type'] = 'flower'
        
        # Ensure valid symmetry type
        if guidance.get('symmetry_type') not in valid_symmetries:
            guidance['symmetry_type'] = 'rotational'
        
        # Ensure complexity is in valid range
        complexity = guidance.get('complexity', 5)
        if not isinstance(complexity, int) or complexity < 1 or complexity > 9:
            guidance['complexity'] = 5
        
        # Ensure count is reasonable
        count = guidance.get('suggested_count', 8)
        if not isinstance(count, int) or count < 3 or count > 16:
            guidance['suggested_count'] = 8
        
        # Ensure lists exist
        if not isinstance(guidance.get('key_elements'), list):
            guidance['key_elements'] = ['center', 'symmetry', 'balance']
        
        if not isinstance(guidance.get('drawing_instructions'), list):
            guidance['drawing_instructions'] = ['Start from center', 'Create symmetric elements', 'Connect with flowing lines']
        
        return guidance
    
    def _get_ai_guidance(self, prompt: str, grid_size: int) -> Dict:
        """Get AI guidance for pattern creation"""
        system_prompt = f"""
        As a traditional Tamil Kolam art expert, analyze this request: "{prompt}"
        
        Consider these aspects:
        - Traditional Kolam principles (Pulli, Sikku, Kambi styles)
        - Mathematical symmetry and geometric precision
        - Cultural and spiritual significance
        - Grid size constraints ({grid_size}x{grid_size})
        
        Provide guidance in this EXACT JSON format:
        {{
            "pattern_type": "flower",
            "symmetry_type": "rotational",
            "complexity": 7,
            "key_elements": ["center_dot", "petals", "connecting_lines"],
            "cultural_context": "Traditional lotus symbolizing purity",
            "mathematical_properties": ["8-fold_rotational_symmetry", "radial_balance"],
            "suggested_count": 8,
            "drawing_instructions": ["Place center dot", "Create 8 petal points", "Connect with flowing lines"],
            "color_suggestions": ["crimson", "navy", "gold"],
            "traditional_significance": "Represents prosperity and divine blessing"
        }}
        
        Ensure pattern_type is one of: flower, lotus, star, diamond, spiral, mandala, geometric, traditional
        Ensure symmetry_type is one of: rotational, bilateral, point, radial
        Complexity should be 1-9 based on detail level.
        """
        
        try:
            response = self.model.generate_content(system_prompt)
            
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Clean up the JSON string
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)  # Remove control characters
                guidance = json.loads(json_str)
                
                # Validate and sanitize the guidance
                guidance = self._validate_ai_guidance(guidance)
                
                # Display AI insights
                with st.expander("🤖 AI Insights", expanded=True):
                    st.write(f"**Cultural Context:** {guidance.get('cultural_context', 'Traditional Kolam pattern')}")
                    st.write(f"**Traditional Significance:** {guidance.get('traditional_significance', 'Sacred geometric art')}")
                    if guidance.get('drawing_instructions'):
                        st.write("**Drawing Instructions:**")
                        for i, instruction in enumerate(guidance['drawing_instructions'], 1):
                            st.write(f"{i}. {instruction}")
                
                return guidance
                
        except json.JSONDecodeError as e:
            st.warning(f"⚠️ AI response parsing failed: {str(e)}")
        except Exception as e:
            st.warning(f"⚠️ AI guidance failed: {str(e)}")
        
        return {}
    
    def _create_pattern_from_analysis(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise Kolam pattern based on analysis"""
        pattern_type = analysis.get('pattern_type', 'geometric')
        
        if pattern_type in self.pattern_templates:
            creator_func = self.pattern_templates[pattern_type]
            return creator_func(analysis, grid_size)
        else:
            return self._create_geometric_template(analysis, grid_size)
    
    def _create_flower_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise flower pattern with enhanced connections"""
        center = grid_size // 2
        petal_count = analysis.get('suggested_count', analysis.get('count', 8))
        complexity = analysis.get('complexity', 5)
        
        dots = [(center, center)]  # Center dot
        connections = []
        
        # Create petals with better spacing
        petal_radius = min(center - 1, max(2, 1 + complexity // 2))
        petal_points = []
        
        for i in range(petal_count):
            angle = 2 * math.pi * i / petal_count
            
            # Main petal point
            x = center + int(petal_radius * math.cos(angle))
            y = center + int(petal_radius * math.sin(angle))
            
            if 0 <= x < grid_size and 0 <= y < grid_size:
                petal_points.append((x, y))
                dots.append((x, y))
                connections.append(((center, center), (x, y)))
                
                # Add intermediate dots for higher complexity
                if complexity > 5:
                    mid_radius = petal_radius * 0.6
                    mid_x = center + int(mid_radius * math.cos(angle))
                    mid_y = center + int(mid_radius * math.sin(angle))
                    if 0 <= mid_x < grid_size and 0 <= mid_y < grid_size:
                        dots.append((mid_x, mid_y))
                        connections.append(((center, center), (mid_x, mid_y)))
                        connections.append(((mid_x, mid_y), (x, y)))
        
        # Create petal-to-petal connections for traditional look
        if complexity > 3 and len(petal_points) > 2:
            for i in range(len(petal_points)):
                next_i = (i + 1) % len(petal_points)
                # Create curved connection through intermediate points
                if complexity > 6:
                    # Add curved connections
                    p1, p2 = petal_points[i], petal_points[next_i]
                    mid_angle = math.atan2((p1[1] + p2[1])/2 - center, (p1[0] + p2[0])/2 - center)
                    curve_radius = petal_radius * 0.8
                    curve_x = center + int(curve_radius * math.cos(mid_angle))
                    curve_y = center + int(curve_radius * math.sin(mid_angle))
                    
                    if 0 <= curve_x < grid_size and 0 <= curve_y < grid_size:
                        curve_point = (curve_x, curve_y)
                        if curve_point not in dots:
                            dots.append(curve_point)
                        connections.append((p1, curve_point))
                        connections.append((curve_point, p2))
        
        # Add decorative ring for high complexity
        if complexity > 7:
            ring_radius = max(1, petal_radius // 2)
            ring_points = []
            for i in range(petal_count * 2):  # Double the points for finer detail
                angle = 2 * math.pi * i / (petal_count * 2)
                x = center + int(ring_radius * math.cos(angle))
                y = center + int(ring_radius * math.sin(angle))
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    ring_points.append((x, y))
                    dots.append((x, y))
            
            # Connect ring points
            for i in range(len(ring_points)):
                next_i = (i + 1) % len(ring_points)
                connections.append((ring_points[i], ring_points[next_i]))
        
        return KolamPattern(
            dots=list(set(dots)),
            connections=connections,
            pattern_type="flower",
            symmetry=analysis.get('symmetry_type', 'rotational'),
            complexity=complexity,
            description=f"Enhanced flower pattern with {petal_count} petals",
            cultural_significance=analysis.get('cultural_context', "Represents prosperity and natural beauty in Tamil culture"),
            grid_size=grid_size
        )
    
    def _create_lotus_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise lotus pattern"""
        center = grid_size // 2
        complexity = analysis.get('complexity', 5)
        petal_count = analysis.get('count', 8)
        
        dots = [(center, center)]
        connections = []
        
        # Inner petals
        inner_radius = max(1, center - 2)
        for i in range(petal_count):
            angle = 2 * math.pi * i / petal_count
            x = center + int(inner_radius * math.cos(angle))
            y = center + int(inner_radius * math.sin(angle))
            if 0 <= x < grid_size and 0 <= y < grid_size:
                dots.append((x, y))
                connections.append(((center, center), (x, y)))
        
        # Outer petals (offset)
        if complexity > 4:
            outer_radius = min(center, inner_radius + 1)
            for i in range(petal_count):
                angle = 2 * math.pi * (i + 0.5) / petal_count  # Offset by half
                x = center + int(outer_radius * math.cos(angle))
                y = center + int(outer_radius * math.sin(angle))
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    dots.append((x, y))
                    # Connect to nearest inner petal
                    nearest_inner_angle = 2 * math.pi * i / petal_count
                    inner_x = center + int(inner_radius * math.cos(nearest_inner_angle))
                    inner_y = center + int(inner_radius * math.sin(nearest_inner_angle))
                    connections.append(((inner_x, inner_y), (x, y)))
        
        return KolamPattern(
            dots=list(set(dots)),
            connections=connections,
            pattern_type="lotus",
            symmetry="rotational",
            complexity=complexity,
            description=f"Lotus pattern with {petal_count} petals",
            cultural_significance="Sacred flower representing purity and enlightenment",
            grid_size=grid_size
        )
    
    def _create_star_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise star pattern"""
        center = grid_size // 2
        points = analysis.get('count', 6)
        complexity = analysis.get('complexity', 5)
        
        dots = [(center, center)]
        connections = []
        
        # Outer points
        outer_radius = center - 1
        outer_points = []
        for i in range(points):
            angle = 2 * math.pi * i / points
            x = center + int(outer_radius * math.cos(angle))
            y = center + int(outer_radius * math.sin(angle))
            if 0 <= x < grid_size and 0 <= y < grid_size:
                outer_points.append((x, y))
                dots.append((x, y))
        
        # Inner points (for star effect)
        inner_radius = max(1, outer_radius // 2)
        inner_points = []
        for i in range(points):
            angle = 2 * math.pi * (i + 0.5) / points  # Offset for star shape
            x = center + int(inner_radius * math.cos(angle))
            y = center + int(inner_radius * math.sin(angle))
            if 0 <= x < grid_size and 0 <= y < grid_size:
                inner_points.append((x, y))
                dots.append((x, y))
        
        # Create star connections
        for i in range(points):
            # Connect outer point to adjacent inner points
            outer_point = outer_points[i]
            prev_inner = inner_points[i - 1]
            curr_inner = inner_points[i]
            
            connections.append((prev_inner, outer_point))
            connections.append((outer_point, curr_inner))
            
            # Connect to center for higher complexity
            if complexity > 6:
                connections.append(((center, center), outer_point))
        
        return KolamPattern(
            dots=list(set(dots)),
            connections=connections,
            pattern_type="star",
            symmetry="rotational",
            complexity=complexity,
            description=f"Star pattern with {points} points",
            cultural_significance="Represents guidance and celestial harmony",
            grid_size=grid_size
        )
    
    def _create_diamond_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise diamond pattern"""
        center = grid_size // 2
        complexity = analysis.get('complexity', 5)
        
        dots = []
        connections = []
        
        # Create diamond shape
        max_radius = center - 1
        for radius in range(1, max_radius + 1):
            if radius % (10 - complexity) == 0 or radius == max_radius:
                # Top
                if center - radius >= 0:
                    dots.append((center, center - radius))
                # Bottom
                if center + radius < grid_size:
                    dots.append((center, center + radius))
                # Left
                if center - radius >= 0:
                    dots.append((center - radius, center))
                # Right
                if center + radius < grid_size:
                    dots.append((center + radius, center))
                
                # Diagonal points for complex diamonds
                if complexity > 6:
                    diag_offset = radius // 2
                    for dx, dy in [(diag_offset, diag_offset), (-diag_offset, diag_offset),
                                   (diag_offset, -diag_offset), (-diag_offset, -diag_offset)]:
                        x, y = center + dx, center + dy
                        if 0 <= x < grid_size and 0 <= y < grid_size:
                            dots.append((x, y))
        
        # Create connections
        dots = list(set(dots))
        # Connect points forming diamond shapes
        for i, dot1 in enumerate(dots):
            for dot2 in dots[i+1:]:
                dist = math.sqrt((dot1[0] - dot2[0])**2 + (dot1[1] - dot2[1])**2)
                if 1 <= dist <= 2.5:  # Connect nearby points
                    connections.append((dot1, dot2))
        
        return KolamPattern(
            dots=dots,
            connections=connections,
            pattern_type="diamond",
            symmetry="bilateral",
            complexity=complexity,
            description="Diamond geometric pattern",
            cultural_significance="Represents stability and balance",
            grid_size=grid_size
        )
    
    def _create_spiral_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise spiral pattern"""
        center = grid_size // 2
        complexity = analysis.get('complexity', 5)
        
        dots = []
        connections = []
        
        # Create spiral
        angle_step = 2 * math.pi / (8 + complexity)
        radius_step = 0.3 + (complexity / 20)
        
        prev_dot = None
        for i in range(int(20 + complexity * 2)):
            angle = i * angle_step
            radius = i * radius_step
            
            if radius >= center - 1:
                break
            
            x = center + int(radius * math.cos(angle))
            y = center + int(radius * math.sin(angle))
            
            if 0 <= x < grid_size and 0 <= y < grid_size:
                current_dot = (x, y)
                dots.append(current_dot)
                
                if prev_dot:
                    connections.append((prev_dot, current_dot))
                
                prev_dot = current_dot
        
        return KolamPattern(
            dots=list(set(dots)),
            connections=connections,
            pattern_type="spiral",
            symmetry="rotational",
            complexity=complexity,
            description="Spiral pattern representing cosmic energy",
            cultural_significance="Represents the cycle of life and cosmic energy",
            grid_size=grid_size
        )
    
    def _create_mandala_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create precise mandala pattern"""
        center = grid_size // 2
        complexity = analysis.get('complexity', 5)
        segments = analysis.get('count', 8)
        
        dots = [(center, center)]
        connections = []
        
        # Multiple concentric rings
        for ring in range(1, center):
            if ring % max(1, (10 - complexity) // 2) == 0:
                ring_dots = []
                points_in_ring = segments * ring
                
                for i in range(points_in_ring):
                    angle = 2 * math.pi * i / points_in_ring
                    x = center + int(ring * math.cos(angle))
                    y = center + int(ring * math.sin(angle))
                    
                    if 0 <= x < grid_size and 0 <= y < grid_size:
                        ring_dots.append((x, y))
                        dots.append((x, y))
                
                # Connect within ring
                for i in range(len(ring_dots)):
                    next_i = (i + 1) % len(ring_dots)
                    connections.append((ring_dots[i], ring_dots[next_i]))
                    
                    # Connect to center or inner ring
                    if ring == 1:
                        connections.append(((center, center), ring_dots[i]))
        
        return KolamPattern(
            dots=list(set(dots)),
            connections=connections,
            pattern_type="mandala",
            symmetry="rotational",
            complexity=complexity,
            description=f"Mandala pattern with {segments} segments",
            cultural_significance="Represents wholeness and cosmic order",
            grid_size=grid_size
        )
    
    def _create_geometric_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create geometric pattern"""
        center = grid_size // 2
        complexity = analysis.get('complexity', 5)
        
        dots = []
        connections = []
        
        # Create regular grid with geometric connections
        step = max(1, (10 - complexity) // 3)
        for i in range(0, grid_size, step):
            for j in range(0, grid_size, step):
                if i < grid_size and j < grid_size:
                    dots.append((i, j))
        
        # Create geometric connections
        for i, dot1 in enumerate(dots):
            for dot2 in dots[i+1:]:
                dist = math.sqrt((dot1[0] - dot2[0])**2 + (dot1[1] - dot2[1])**2)
                if dist <= step * 1.5:
                    connections.append((dot1, dot2))
        
        return KolamPattern(
            dots=dots,
            connections=connections,
            pattern_type="geometric",
            symmetry=analysis.get('symmetry_type', 'bilateral'),
            complexity=complexity,
            description="Geometric grid pattern",
            cultural_significance="Represents mathematical harmony",
            grid_size=grid_size
        )
    
    def _create_traditional_template(self, analysis: Dict, grid_size: int) -> KolamPattern:
        """Create traditional Tamil Kolam pattern"""
        # This would implement traditional patterns like Pulli Kolam
        # For now, create a flower-based traditional pattern
        # Use enhanced flower template with traditional elements
        analysis['pattern_type'] = 'flower'
        return self._create_flower_template(analysis, grid_size)
    
    def visualize_pattern(self, pattern: KolamPattern, title: str = "Generated Kolam", fill_rangoli: bool = False, color_palette: Optional[List[str]] = None) -> plt.Figure:
        """Enhanced visualization of the generated Kolam pattern.
        When fill_rangoli is True, uses a colorful rangoli-style rendering.
        """
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Set background color
        ax.set_facecolor('#fefefe')
        fig.patch.set_facecolor('white')
        
        # Choose palette
        default_palette = ['#e53935', '#fb8c00', '#fdd835', '#43a047', '#1e88e5', '#8e24aa', '#ff4081']
        palette = color_palette if (color_palette and len(color_palette) > 0) else default_palette

        # Draw connections first with better styling
        for idx, (start, end) in enumerate(pattern.connections):
            if fill_rangoli:
                # Rangoli style: bold, colorful strokes cycling through palette
                color = palette[idx % len(palette)]
                ax.plot([start[0], end[0]], [start[1], end[1]],
                        color=color, linewidth=6, alpha=0.9, zorder=1)
            else:
                # Create slightly curved lines for more organic look
                if len(pattern.connections) > 10:  # For complex patterns
                    # Add slight curve to lines
                    mid_x = (start[0] + end[0]) / 2
                    mid_y = (start[1] + end[1]) / 2
                    
                    # Calculate perpendicular offset for curve
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = math.sqrt(dx*dx + dy*dy)
                    
                    if length > 0:
                        # Normalize and get perpendicular
                        norm_x = -dy / length
                        norm_y = dx / length
                        
                        # Small curve offset
                        curve_offset = 0.1
                        curve_x = mid_x + norm_x * curve_offset
                        curve_y = mid_y + norm_y * curve_offset
                        
                        # Draw curved line using quadratic bezier approximation
                        t = np.linspace(0, 1, 20)
                        curve_xs = (1-t)**2 * start[0] + 2*(1-t)*t * curve_x + t**2 * end[0]
                        curve_ys = (1-t)**2 * start[1] + 2*(1-t)*t * curve_y + t**2 * end[1]
                        
                        ax.plot(curve_xs, curve_ys, color='#8B0000', linewidth=3, alpha=0.8, zorder=1)
                    else:
                        ax.plot([start[0], end[0]], [start[1], end[1]], 
                               color='#8B0000', linewidth=3, alpha=0.8, zorder=1)
                else:
                    ax.plot([start[0], end[0]], [start[1], end[1]], 
                           color='#8B0000', linewidth=3, alpha=0.8, zorder=1)
        
        # Draw dots with enhanced styling (with optional rangoli fill)
        if pattern.dots:
            x_coords = [dot[0] for dot in pattern.dots]
            y_coords = [dot[1] for dot in pattern.dots]
            
            if fill_rangoli:
                # Soft colored fills behind dots
                colors_cycle = [palette[i % len(palette)] for i in range(len(x_coords))]
                ax.scatter(x_coords, y_coords, c=colors_cycle, s=600, 
                           marker='o', zorder=0, alpha=0.25, edgecolors='none')
                # Bright centers
                ax.scatter(x_coords, y_coords, c=colors_cycle, s=180, 
                           marker='o', zorder=3, alpha=0.95, edgecolors='white', linewidths=2)
            else:
                # Main dots (default look)
                ax.scatter(x_coords, y_coords, c='#000080', s=200, 
                          marker='o', zorder=3, alpha=0.9, edgecolors='white', linewidths=2)
                
                # Add inner highlight
                ax.scatter(x_coords, y_coords, c='#4169E1', s=80, 
                          marker='o', zorder=4, alpha=0.7)
        
        # Configure plot with better styling
        ax.set_xlim(-0.8, pattern.grid_size - 0.2)
        ax.set_ylim(-0.8, pattern.grid_size - 0.2)
        ax.set_aspect('equal')
        
        # Enhanced grid
        ax.grid(True, alpha=0.2, linestyle=':', color='gray')
        
        # Better title formatting
        ax.set_title(f"{title}\n{pattern.description}", 
                    fontsize=16, fontweight='bold', pad=25, 
                    color='#2E4057')
        
        # Remove ticks for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Invert y-axis for traditional grid layout
        ax.invert_yaxis()
        
        # Enhanced pattern info with better formatting
        info_text = f"Type: {pattern.pattern_type.title()} • Symmetry: {pattern.symmetry.title()} • Complexity: {pattern.complexity}/9"
        ax.text(0.5, -0.08, info_text, transform=ax.transAxes, ha='center', 
                fontsize=12, style='italic', color='#555555', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#f0f0f0', alpha=0.8))
        
        # Add cultural significance
        cultural_text = pattern.cultural_significance[:80] + "..." if len(pattern.cultural_significance) > 80 else pattern.cultural_significance
        ax.text(0.5, -0.12, cultural_text, transform=ax.transAxes, ha='center', 
                fontsize=10, color='#666666', style='italic')
        
        plt.tight_layout()
        return fig

# Example usage and testing
def create_ai_generator_interface():
    """Create the enhanced Kolam generator interface"""
    st.title("🎨 Enhanced AI Kolam Generator")
    st.markdown("Generate mathematically precise traditional Kolam patterns using AI guidance")
    
    # Initialize session state for persistent prompt management
    if 'current_ai_prompt' not in st.session_state:
        st.session_state.current_ai_prompt = ""
    
    # API key management
    current_api_key = get_gemini_api_key()
    
    # Show API key status
    if current_api_key:
        st.success("✅ Gemini API Connected - AI guidance enabled")
    else:
        st.warning("⚠️ Gemini API not configured")
        st.info("For enhanced AI guidance, configure your API key in Settings. Basic mathematical patterns will still work.")
    
    # Initialize generator with current API key
    generator = EnhancedKolamGenerator(current_api_key)
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use session state for prompt persistence
        prompt = st.text_area(
            "🎨 Describe your Kolam pattern:",
            value=st.session_state.current_ai_prompt,
            placeholder="e.g., 'Create a lotus flower with 8 petals and rotational symmetry' or 'Generate a complex star pattern with 6 points'",
            height=100,
            key="ai_prompt_input"
        )
        
        # Update session state when prompt changes
        if prompt != st.session_state.current_ai_prompt:
            st.session_state.current_ai_prompt = prompt
        
        grid_size = st.selectbox("Grid Size:", options=[5, 7, 9, 11, 13], index=1)
        
        # Rangoli fill option (minimal, single feature)
        fill_rangoli = st.checkbox("🎨 Fill with colours (Rangoli style)", value=False)
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col_a, col_b = st.columns(2)
            with col_a:
                force_pattern = st.selectbox(
                    "Force Pattern Type (optional):",
                    options=["Auto (AI decides)", "flower", "lotus", "star", "diamond", "spiral", "mandala", "geometric"],
                    index=0
                )
            with col_b:
                force_complexity = st.slider(
                    "Force Complexity (optional):",
                    min_value=1, max_value=9, value=5,
                    help="1=Simple, 9=Very Complex"
                )
    
    with col2:
        st.markdown("**🌟 Try these prompts:**")
        example_prompts = [
            "Simple flower with 6 petals",
            "Complex lotus with rotational symmetry", 
            "Star pattern with 8 points",
            "Diamond geometric pattern",
            "Traditional spiral design",
            "Mandala with intricate details",
            "Pulli kolam with 5x5 grid",
            "Sikku kolam with flowing lines"
        ]
        
        for ex_prompt in example_prompts:
            if st.button(ex_prompt, key=f"ex_{hash(ex_prompt)}", use_container_width=True):
                st.session_state.current_ai_prompt = ex_prompt
                st.rerun()
    
    # Generate button
    if st.button("🚀 Generate Kolam", type="primary", disabled=not prompt.strip()):
        with st.spinner("✨ Creating your Kolam pattern..."):
            # Apply advanced options if specified
            advanced_prompt = prompt
            if force_pattern != "Auto (AI decides)":
                advanced_prompt += f" (pattern type: {force_pattern})"
            advanced_prompt += f" (complexity level: {force_complexity})"
            
            result = generator.generate_kolam_from_prompt(advanced_prompt, grid_size)
            
            if result.get("success"):
                pattern = result["pattern"]
                
                # Extract Gemini color suggestions if available
                palette = None
                analysis = result.get("analysis") or {}
                if isinstance(analysis, dict) and analysis.get("color_suggestions"):
                    try:
                        # Normalize to hex or names as-is
                        palette = [str(c) for c in analysis.get("color_suggestions", []) if c]
                    except Exception:
                        palette = None
                
                # Visualize with optional rangoli fill
                fig = generator.visualize_pattern(
                    pattern,
                    f"Generated from: '{prompt[:50]}...'",
                    fill_rangoli=fill_rangoli,
                    color_palette=palette,
                )
                st.pyplot(fig)
                
                # Display comprehensive pattern information
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🎭 Pattern Type", pattern.pattern_type.title())
                with col2:
                    st.metric("🔄 Symmetry", pattern.symmetry.title())
                with col3:
                    st.metric("🏆 Complexity", f"{pattern.complexity}/9")
                with col4:
                    st.metric("🔢 Elements", f"{len(pattern.dots)} dots, {len(pattern.connections)} lines")
                
                # Enhanced pattern details
                with st.expander("📚 Pattern Details & Cultural Context", expanded=True):
                    col_detail1, col_detail2 = st.columns(2)
                    
                    with col_detail1:
                        st.write(f"**🌿 Description:** {pattern.description}")
                        st.write(f"**📜 Cultural Significance:** {pattern.cultural_significance}")
                        
                        # Display AI analysis if available
                        if result.get("analysis"):
                            analysis = result["analysis"]
                            if analysis.get('key_elements'):
                                st.write("**🔑 Key Elements:**")
                                for element in analysis['key_elements']:
                                    st.write(f"• {element}")
                    
                    with col_detail2:
                        # Technical details
                        st.json({
                            "technical_specs": {
                                "dots_count": len(pattern.dots),
                                "connections_count": len(pattern.connections),
                                "grid_size": f"{pattern.grid_size}x{pattern.grid_size}",
                                "density": round(len(pattern.dots) / (pattern.grid_size * pattern.grid_size), 2)
                            },
                            "pattern_analysis": result.get("analysis", {})
                        })
                
                # Enhanced export options
                st.markdown("---")
                col_export1, col_export2, col_export3 = st.columns(3)
                
                with col_export1:
                    if st.button("💾 Export Pattern Data", use_container_width=True):
                        pattern_data = {
                            "metadata": {
                                "generated_from": prompt,
                                "ai_enhanced": current_api_key is not None
                            },
                            "pattern": {
                                "dots": pattern.dots,
                                "connections": pattern.connections,
                                "pattern_type": pattern.pattern_type,
                                "symmetry": pattern.symmetry,
                                "complexity": pattern.complexity,
                                "description": pattern.description,
                                "cultural_significance": pattern.cultural_significance,
                                "grid_size": pattern.grid_size
                            },
                            "analysis": result.get("analysis", {})
                        }
                        st.download_button(
                            "📁 Download JSON",
                            data=json.dumps(pattern_data, indent=2),
                            file_name=f"kolam_{pattern.pattern_type}_{pattern.complexity}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                with col_export2:
                    if st.button("✏️ Edit in Editor", use_container_width=True):
                        # Transfer pattern to editor
                        st.session_state['editor_pattern'] = {
                            'dots': pattern.dots,
                            'connections': [{'start': conn[0], 'end': conn[1], 'type': 'line'} for conn in pattern.connections],
                            'grid_size': pattern.grid_size,
                            'pattern_type': pattern.pattern_type
                        }
                        st.success("✅ Pattern transferred to editor! Go to Interactive Editor tab.")
                
                with col_export3:
                    if st.button("🔄 Generate Variation", use_container_width=True):
                        # Generate a variation with slightly different parameters
                        variation_prompt = prompt + " (create a variation with different details)"
                        st.session_state.current_ai_prompt = variation_prompt
                        st.rerun()
            
            else:
                st.error(f"❌ {result.get('error', 'Unknown error')}")
                st.info("💡 Try simplifying your prompt or check your API key configuration.")
    
    # Educational content with enhanced information
    with st.expander("📚 About Traditional Kolam Art", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🏛️ Tradition", "🔢 Mathematics", "🎨 Techniques"])
        
        with tab1:
            st.markdown("""
            **Traditional Kolam Art:**
            - **Pulli Kolam**: Dot-based patterns with geometric precision, created by connecting dots in specific ways
            - **Sikku Kolam**: Continuous line patterns drawn without lifting the hand, representing life's continuity
            - **Kambi Kolam**: Line-based patterns with mathematical symmetry and spiritual significance
            
            **Cultural Significance:**
            - **Daily Practice**: Traditionally drawn every morning at the entrance of homes
            - **Spiritual Meaning**: Represents prosperity, protection, and welcome to visitors
            - **Seasonal Variations**: Different patterns for festivals and special occasions
            """)
        
        with tab2:
            st.markdown("""
            **Mathematical Principles:**
            - **Symmetry Types**: Rotational, bilateral, translational, and point symmetry
            - **Geometric Patterns**: Based on circles, polygons, and recursive structures
            - **Fractal Properties**: Many traditional patterns exhibit self-similar characteristics
            
            **Pattern Complexity:**
            - **Level 1-3**: Simple symmetric patterns with basic connections
            - **Level 4-6**: Intermediate patterns with multiple elements and curves
            - **Level 7-9**: Complex designs with intricate details and advanced symmetry
            """)
        
        with tab3:
            st.markdown("""
            **Drawing Techniques:**
            - **Grid Method**: Start with a dot grid and connect according to rules
            - **Flow Method**: Use continuous flowing lines to create organic patterns
            - **Symmetry Method**: Build patterns using mathematical symmetry principles
            
            **AI Enhancement Features:**
            - **Prompt Analysis**: AI interprets your description and suggests appropriate patterns
            - **Cultural Context**: AI provides traditional significance and meaning
            - **Mathematical Precision**: AI ensures proper symmetry and geometric accuracy
            """)

if __name__ == "__main__":
    create_ai_generator_interface()