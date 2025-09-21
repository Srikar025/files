import streamlit as st
import google.generativeai as genai
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import json
from typing import Dict, List, Tuple
from config import get_gemini_api_key
from prompt_examples import PROMPT_CATEGORIES, get_random_prompt

class AIKolamGenerator:
    """AI-powered Kolam generator using Gemini API for prompt-based generation"""
    
    def __init__(self):
        api_key = get_gemini_api_key()
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def generate_kolam_from_prompt(self, prompt: str, grid_size: int = 7) -> Dict:
        """Generate Kolam pattern from text prompt using Gemini API"""
        if not self.model:
            return {"error": "Gemini API not configured"}
        
        try:
            # Create detailed prompt for Gemini
            system_prompt = f"""
            You are an expert in traditional Indian Kolam art and mathematics. 
            Generate a Kolam pattern based on the user's description.
            
            User Request: {prompt}
            Grid Size: {grid_size}x{grid_size}
            
            Please provide:
            1. A detailed description of the Kolam pattern
            2. The mathematical properties (symmetry type, complexity, etc.)
            3. Step-by-step instructions for drawing
            4. Cultural significance if any
            5. A JSON representation of the pattern with dot coordinates and connections
            
            Format the response as structured text with clear sections.
            For the JSON pattern, use this format:
            {{
                "pattern_type": "symmetric/rotational/floral/geometric",
                "symmetry": "horizontal/vertical/rotational/bilateral",
                "complexity": 1-10,
                "dots": [[x1,y1], [x2,y2], ...],
                "connections": [{{"start": [x1,y1], "end": [x2,y2]}}, ...],
                "description": "Detailed pattern description",
                "cultural_significance": "Cultural context if any"
            }}
            """
            
            response = self.model.generate_content(system_prompt)
            
            # Parse the response
            result = self._parse_gemini_response(response.text)
            
            return {
                "success": True,
                "prompt": prompt,
                "grid_size": grid_size,
                "raw_response": response.text,
                "pattern_data": result
            }
            
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini response to extract pattern data"""
        result = {
            "pattern_type": "symmetric",
            "symmetry": "bilateral", 
            "complexity": 5,
            "dots": [],
            "connections": [],
            "description": "AI-generated Kolam pattern",
            "cultural_significance": "Traditional Kolam art"
        }
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_json = json.loads(json_str)
                result.update(parsed_json)
            
            # Extract description if not in JSON
            if "description" not in result or not result["description"]:
                desc_match = re.search(r'description[:\s]*([^\n]+)', response_text, re.IGNORECASE)
                if desc_match:
                    result["description"] = desc_match.group(1).strip()
            
            # Extract complexity if not in JSON
            if result["complexity"] == 5:
                complexity_match = re.search(r'complexity[:\s]*(\d+)', response_text, re.IGNORECASE)
                if complexity_match:
                    result["complexity"] = int(complexity_match.group(1))
            
        except Exception as e:
            st.warning(f"Could not parse full response: {str(e)}")
        
        # Generate basic pattern if no dots provided
        if not result["dots"]:
            result["dots"] = self._generate_basic_pattern_from_description(result["description"])
        
        return result
    
    def _generate_basic_pattern_from_description(self, description: str) -> List[List[int]]:
        """Generate basic pattern coordinates from description"""
        dots = []
        center = 3  # For 7x7 grid
        
        # Simple pattern generation based on keywords
        desc_lower = description.lower()
        
        if "flower" in desc_lower or "floral" in desc_lower:
            # Floral pattern
            dots = [[center, center]]  # Center
            for angle in range(0, 360, 45):  # 8 petals
                import math
                x = center + int(2 * math.cos(math.radians(angle)))
                y = center + int(2 * math.sin(math.radians(angle)))
                if 0 <= x < 7 and 0 <= y < 7:
                    dots.append([x, y])
        
        elif "spiral" in desc_lower:
            # Spiral pattern
            dots = [[center, center]]
            for i in range(1, 4):
                for angle in [0, 90, 180, 270]:
                    import math
                    x = center + int(i * math.cos(math.radians(angle)))
                    y = center + int(i * math.sin(math.radians(angle)))
                    if 0 <= x < 7 and 0 <= y < 7:
                        dots.append([x, y])
        
        elif "diamond" in desc_lower or "square" in desc_lower:
            # Diamond pattern
            for i in range(7):
                for j in range(7):
                    if abs(i - center) + abs(j - center) <= 2:
                        dots.append([i, j])
        
        else:
            # Default symmetric pattern
            for i in range(1, 6, 2):  # Odd rows
                for j in range(1, 6, 2):  # Odd columns
                    dots.append([i, j])
        
        return dots
    
    def generate_connections(self, dots: List[List[int]], pattern_type: str) -> List[Dict]:
        """Generate connections between dots based on pattern type"""
        connections = []
        
        if not dots:
            return connections
        
        # Connect nearby dots based on pattern type
        for i, dot1 in enumerate(dots):
            for j, dot2 in enumerate(dots[i+1:], i+1):
                distance = ((dot1[0] - dot2[0])**2 + (dot1[1] - dot2[1])**2)**0.5
                
                if pattern_type == "floral":
                    # Connect center to petals
                    if dot1 == [3, 3] or dot2 == [3, 3]:
                        if distance <= 3:
                            connections.append({"start": dot1, "end": dot2})
                elif pattern_type == "spiral":
                    # Connect in spiral order
                    if distance <= 2:
                        connections.append({"start": dot1, "end": dot2})
                elif pattern_type == "geometric":
                    # Connect in geometric shapes
                    if distance <= 1.5:
                        connections.append({"start": dot1, "end": dot2})
                else:
                    # Default: connect nearby dots
                    if distance <= 2:
                        connections.append({"start": dot1, "end": dot2})
        
        return connections
    
    def draw_ai_generated_kolam(self, pattern_data: Dict, title: str = "AI-Generated Kolam") -> plt.Figure:
        """Draw the AI-generated Kolam pattern"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        dots = pattern_data.get("dots", [])
        connections = pattern_data.get("connections", [])
        
        # Draw dots
        if dots:
            dot_x = [dot[0] for dot in dots]
            dot_y = [dot[1] for dot in dots]
            ax.scatter(dot_x, dot_y, c='black', s=150, marker='o', zorder=3, label='Dots')
        
        # Draw connections
        for connection in connections:
            start = connection.get("start", [0, 0])
            end = connection.get("end", [0, 0])
            ax.plot([start[0], end[0]], [start[1], end[1]], 'r-', linewidth=3, alpha=0.7, zorder=2)
        
        # Configure plot
        ax.set_xlim(-0.5, 6.5)
        ax.set_ylim(-0.5, 6.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.legend()
        
        # Invert y-axis to match typical grid layout
        ax.invert_yaxis()
        
        return fig

def create_ai_generator_interface():
    """Create the AI Kolam generator interface"""
    st.subheader("🤖 AI-Powered Kolam Generator")
    st.write("Describe the Kolam pattern you want, and AI will generate it for you!")
    
    # Initialize generator
    generator = AIKolamGenerator()
    
    if not generator.model:
        st.error("❌ Gemini API not configured. Please set your API key in Settings.")
        return
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Prompt input
        default_prompt = st.session_state.get('ai_prompt', '')
        prompt = st.text_area(
            "🎨 Describe your Kolam pattern:",
            value=default_prompt,
            placeholder="e.g., 'Create a floral Kolam with 8 petals and rotational symmetry' or 'Generate a geometric diamond pattern with intricate connections'",
            height=100,
            help="Describe the type of Kolam pattern you want. Be as specific or general as you like!"
        )
        
        # Clear session state after using it
        if default_prompt:
            del st.session_state.ai_prompt
        
        # Grid size
        grid_size = st.selectbox(
            "📐 Grid Size:",
            options=[5, 7, 9, 11],
            index=1,
            help="Size of the dot grid"
        )
    
    with col2:
        st.subheader("💡 Prompt Ideas")
        
        # Random prompt button
        if st.button("🎲 Random Prompt", help="Get a random prompt idea"):
            random_prompt = get_random_prompt()
            st.session_state.ai_prompt = random_prompt
            st.rerun()
        
        # Categorized examples
        st.write("**Choose a category:**")
        
        for category, examples in PROMPT_CATEGORIES.items():
            with st.expander(category):
                for example in examples[:3]:  # Show first 3 examples
                    if st.button(example, key=f"example_{hash(example)}", help="Click to use this prompt"):
                        st.session_state.ai_prompt = example
                        st.rerun()
                
                if len(examples) > 3:
                    st.caption(f"... and {len(examples) - 3} more examples")
        
        # Quick prompt buttons
        st.write("**Quick Ideas:**")
        quick_prompts = [
            "Simple flower with 6 petals",
            "Complex geometric mandala", 
            "Traditional festival Kolam",
            "Modern abstract design",
            "Spiral with rotational symmetry"
        ]
        
        for quick_prompt in quick_prompts:
            if st.button(f"✨ {quick_prompt}", key=f"quick_{hash(quick_prompt)}", help="Quick prompt"):
                st.session_state.ai_prompt = quick_prompt
                st.rerun()
        
        # Advanced options
        st.subheader("⚙️ Options")
        show_details = st.checkbox("Show AI Analysis", value=True, help="Display detailed AI response")
        generate_connections = st.checkbox("Auto-generate Connections", value=True, help="Automatically connect nearby dots")
    
    # Generate button
    if st.button("🚀 Generate Kolam with AI", type="primary", disabled=not prompt.strip()):
        if prompt.strip():
            with st.spinner("🤖 AI is generating your Kolam pattern..."):
                result = generator.generate_kolam_from_prompt(prompt, grid_size)
                
                if result.get("success"):
                    pattern_data = result["pattern_data"]
                    
                    # Auto-generate connections if requested
                    if generate_connections and not pattern_data.get("connections"):
                        pattern_data["connections"] = generator.generate_connections(
                            pattern_data["dots"], 
                            pattern_data.get("pattern_type", "symmetric")
                        )
                    
                    # Store in session state
                    st.session_state.ai_generated_kolam = {
                        "pattern_data": pattern_data,
                        "prompt": prompt,
                        "grid_size": grid_size,
                        "raw_response": result["raw_response"]
                    }
                    
                    st.success("✅ AI-generated Kolam pattern created!")
                else:
                    st.error(f"❌ {result.get('error', 'Unknown error')}")
        else:
            st.warning("⚠️ Please enter a description for your Kolam pattern")
    
    # Display generated Kolam
    if 'ai_generated_kolam' in st.session_state:
        kolam_data = st.session_state.ai_generated_kolam
        pattern_data = kolam_data["pattern_data"]
        
        # Create visualization
        fig = generator.draw_ai_generated_kolam(pattern_data, f"AI-Generated: {kolam_data['prompt'][:30]}...")
        st.pyplot(fig)
        
        # Pattern information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pattern Type", pattern_data.get("pattern_type", "Unknown").title())
            st.metric("Symmetry", pattern_data.get("symmetry", "Unknown").title())
        
        with col2:
            st.metric("Complexity", f"{pattern_data.get('complexity', 5)}/10")
            st.metric("Dots", len(pattern_data.get("dots", [])))
        
        with col3:
            st.metric("Connections", len(pattern_data.get("connections", [])))
            st.metric("Grid Size", f"{kolam_data['grid_size']}x{kolam_data['grid_size']}")
        
        # Detailed information
        if show_details:
            with st.expander("📝 AI Analysis & Details"):
                st.subheader("🎨 Pattern Description")
                st.write(pattern_data.get("description", "No description available"))
                
                st.subheader("🏛️ Cultural Significance")
                st.write(pattern_data.get("cultural_significance", "Traditional Kolam art pattern"))
                
                st.subheader("🔍 Technical Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.json({
                        "pattern_type": pattern_data.get("pattern_type"),
                        "symmetry": pattern_data.get("symmetry"),
                        "complexity": pattern_data.get("complexity")
                    })
                with col2:
                    st.json({
                        "total_dots": len(pattern_data.get("dots", [])),
                        "total_connections": len(pattern_data.get("connections", [])),
                        "grid_size": kolam_data["grid_size"]
                    })
                
                # Full AI response
                st.subheader("🤖 Full AI Response")
                st.text_area("Complete AI Analysis", kolam_data["raw_response"], height=300)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Pattern"):
                # Save pattern data
                pattern_json = json.dumps(pattern_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=pattern_json,
                    file_name=f"ai_kolam_{pattern_data.get('pattern_type', 'pattern')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🔄 Generate Another"):
                if 'ai_generated_kolam' in st.session_state:
                    del st.session_state.ai_generated_kolam
                st.rerun()
        
        with col3:
            if st.button("✏️ Edit in Editor"):
                # Pass pattern to editor
                st.session_state.editor_pattern = pattern_data
                st.success("Pattern loaded into editor! Go to Interactive Editor page.")
    
    # Tips section
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        **🎯 For Best Results:**
        - Be specific about symmetry (rotational, bilateral, etc.)
        - Mention geometric shapes (diamond, square, circle)
        - Include complexity level (simple, intricate, complex)
        - Reference traditional elements (floral, geometric, mandala)
        
        **🌟 Example Prompts:**
        - "Create a simple 6-petaled flower Kolam with rotational symmetry"
        - "Generate a complex geometric diamond pattern with intricate connections"
        - "Design a traditional South Indian Kolam with floral motifs"
        - "Make a star-shaped Kolam with radiating lines and bilateral symmetry"
        
        **🔧 Technical Notes:**
        - AI generates patterns based on mathematical principles
        - Patterns respect traditional Kolam design rules
        - You can further customize in the Interactive Editor
        """)
