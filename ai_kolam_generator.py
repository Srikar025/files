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
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        
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
    
    def _get_ai_guidance(self, prompt: str, grid_size: int) -> Dict:
        """Get AI guidance for pattern creation"""
        system_prompt = f"""
        As a Kolam art expert, analyze this request: "{prompt}"
        
        Provide guidance in this JSON format:
        {{
            "pattern_type": "flower/lotus/star/diamond/spiral/mandala/geometric",
            "symmetry_type": "rotational/bilateral/point/radial",
            "complexity": 1-9,
            "key_elements": ["element1", "element2"],
            "cultural_context": "brief description",
            "mathematical_properties": ["property1", "property2"],
            "suggested_count": number_of_petals_or_points,
            "drawing_instructions": ["step1", "step2", "step3"]
        }}
        
        Focus on mathematical precision and traditional Kolam principles.
        """
        
        try:
            response = self.model.generate_content(system_prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except:
            pass
        
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
        """Create precise flower pattern"""
        center = grid_size // 2
        petal_count = analysis.get('count', 8)
        complexity = analysis.get('complexity', 5)
        
        dots = [(center, center)]  # Center dot
        connections = []
        
        # Create petals
        petal_radius = min(center - 1, 2 + complexity // 3)
        for i in range(petal_count):
            angle = 2 * math.pi * i / petal_count
            
            # Main petal point
            x = center + int(petal_radius * math.cos(angle))
            y = center + int(petal_radius * math.sin(angle))
            
            if 0 <= x < grid_size and 0 <= y < grid_size:
                dots.append((x, y))
                connections.append(((center, center), (x, y)))
                
                # Add intermediate dots for complexity
                if complexity > 5:
                    mid_x = center + int((petal_radius * 0.6) * math.cos(angle))
                    mid_y = center + int((petal_radius * 0.6) * math.sin(angle))
                    if 0 <= mid_x < grid_size and 0 <= mid_y < grid_size:
                        dots.append((mid_x, mid_y))
                        connections.append(((center, center), (mid_x, mid_y)))
                        connections.append(((mid_x, mid_y), (x, y)))
        
        # Add connecting rings for higher complexity
        if complexity > 7:
            ring_radius = petal_radius // 2
            for i in range(petal_count):
                angle = 2 * math.pi * i / petal_count
                x = center + int(ring_radius * math.cos(angle))
                y = center + int(ring_radius * math.sin(angle))
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    dots.append((x, y))
                    # Connect to adjacent ring points
                    next_angle = 2 * math.pi * ((i + 1) % petal_count) / petal_count
                    next_x = center + int(ring_radius * math.cos(next_angle))
                    next_y = center + int(ring_radius * math.sin(next_angle))
                    if 0 <= next_x < grid_size and 0 <= next_y < grid_size:
                        connections.append(((x, y), (next_x, next_y)))
        
        return KolamPattern(
            dots=list(set(dots)),
            connections=connections,
            pattern_type="flower",
            symmetry=analysis.get('symmetry_type', 'rotational'),
            complexity=complexity,
            description=f"Flower pattern with {petal_count} petals",
            cultural_significance="Represents prosperity and natural beauty in Tamil culture",
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
        return self._create_flower_template(analysis, grid_size)
    
    def visualize_pattern(self, pattern: KolamPattern, title: str = "Generated Kolam") -> plt.Figure:
        """Visualize the generated Kolam pattern"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw connections first
        for start, end in pattern.connections:
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   'crimson', linewidth=2.5, alpha=0.8, zorder=1)
        
        # Draw dots
        if pattern.dots:
            x_coords = [dot[0] for dot in pattern.dots]
            y_coords = [dot[1] for dot in pattern.dots]
            ax.scatter(x_coords, y_coords, c='navy', s=120, 
                      marker='o', zorder=3, alpha=0.9, edgecolors='white', linewidths=1)
        
        # Configure plot
        ax.set_xlim(-0.5, pattern.grid_size - 0.5)
        ax.set_ylim(-0.5, pattern.grid_size - 0.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_title(f"{title}\n{pattern.description}", fontsize=14, fontweight='bold', pad=20)
        
        # Remove ticks for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add subtle background
        ax.set_facecolor('#fafafa')
        
        # Invert y-axis for traditional grid layout
        ax.invert_yaxis()
        
        # Add pattern info
        info_text = f"Type: {pattern.pattern_type.title()} | Symmetry: {pattern.symmetry.title()} | Complexity: {pattern.complexity}/9"
        ax.text(0.5, -0.05, info_text, transform=ax.transAxes, ha='center', 
                fontsize=10, style='italic', color='gray')
        
        plt.tight_layout()
        return fig

# Example usage and testing
def create_enhanced_interface():
    """Create the enhanced Kolam generator interface"""
    st.title("🎨 Enhanced AI Kolam Generator")
    st.markdown("Generate mathematically precise traditional Kolam patterns using AI guidance")
    
    # API key input
    api_key = st.text_input("Gemini API Key (optional for AI guidance)", type="password")
    
    # Initialize generator
    generator = EnhancedKolamGenerator(api_key if api_key else None)
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area(
            "🎨 Describe your Kolam pattern:",
            placeholder="e.g., 'Create a lotus flower with 8 petals and rotational symmetry' or 'Generate a complex star pattern with 6 points'",
            height=100
        )
        
        grid_size = st.selectbox("Grid Size:", options=[5, 7, 9, 11, 13], index=1)
    
    with col2:
        st.markdown("**🌟 Try these prompts:**")
        example_prompts = [
            "Simple flower with 6 petals",
            "Complex lotus with rotational symmetry",
            "Star pattern with 8 points",
            "Diamond geometric pattern",
            "Traditional spiral design",
            "Mandala with intricate details"
        ]
        
        for ex_prompt in example_prompts:
            if st.button(ex_prompt, key=f"ex_{hash(ex_prompt)}"):
                st.session_state.selected_prompt = ex_prompt
                st.rerun()
        
        # Use selected prompt if available
        if 'selected_prompt' in st.session_state:
            prompt = st.session_state.selected_prompt
    
    # Generate button
    if st.button("🚀 Generate Kolam", type="primary", disabled=not prompt.strip()):
        with st.spinner("Creating your Kolam pattern..."):
            result = generator.generate_kolam_from_prompt(prompt, grid_size)
            
            if result.get("success"):
                pattern = result["pattern"]
                
                # Visualize
                fig = generator.visualize_pattern(pattern, f"Generated from: '{prompt[:50]}...'")
                st.pyplot(fig)
                
                # Display pattern information
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pattern Type", pattern.pattern_type.title())
                with col2:
                    st.metric("Symmetry", pattern.symmetry.title())
                with col3:
                    st.metric("Complexity", f"{pattern.complexity}/9")
                with col4:
                    st.metric("Elements", f"{len(pattern.dots)} dots, {len(pattern.connections)} lines")
                
                # Additional information
                with st.expander("📖 Pattern Details"):
                    st.write(f"**Description:** {pattern.description}")
                    st.write(f"**Cultural Significance:** {pattern.cultural_significance}")
                    
                    # Technical details
                    st.json({
                        "dots_count": len(pattern.dots),
                        "connections_count": len(pattern.connections),
                        "grid_size": f"{pattern.grid_size}x{pattern.grid_size}",
                        "pattern_analysis": result.get("analysis", {})
                    })
                
                # Export options
                if st.button("💾 Export Pattern Data"):
                    pattern_data = {
                        "dots": pattern.dots,
                        "connections": pattern.connections,
                        "pattern_type": pattern.pattern_type,
                        "symmetry": pattern.symmetry,
                        "complexity": pattern.complexity,
                        "description": pattern.description,
                        "grid_size": pattern.grid_size
                    }
                    st.download_button(
                        "📥 Download JSON",
                        data=json.dumps(pattern_data, indent=2),
                        file_name=f"kolam_{pattern.pattern_type}_{pattern.complexity}.json",
                        mime="application/json"
                    )
            else:
                st.error(f"❌ {result.get('error', 'Unknown error')}")
    
    # Educational content
    with st.expander("📚 About Kolam Patterns"):
        st.markdown("""
        **Traditional Kolam Art:**
        - **Pulli Kolam**: Dot-based patterns with geometric precision
        - **Sikku Kolam**: Continuous line patterns without lifting the hand
        - **Kambi Kolam**: Line-based patterns with mathematical symmetry
        
        **Pattern Types:**
        - **Floral**: Lotus, flower petals, natural forms
        - **Geometric**: Stars, diamonds, polygons
        - **Spiral**: Representing cosmic energy and life cycles
        - **Mandala**: Circular patterns with spiritual significance
        
        **Symmetry Types:**
        - **Rotational**: Pattern looks same when rotated
        - **Bilateral**: Mirror symmetry along axis
        - **Radial**: Symmetry from central point
        """)

if __name__ == "__main__":
    create_enhanced_interface()