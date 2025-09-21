import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
from typing import Dict, List, Any
from config import GEMINI_API_KEY

class GeminiKolamAnalyzer:
    """Integration with Gemini API for advanced Kolam analysis and generation"""
    
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.model_vision = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            self.model_vision = None
            st.warning("⚠️ Gemini API key not configured. Please set GEMINI_API_KEY in your environment.")
    
    def analyze_kolam_design(self, design_data: Dict) -> Dict:
        """Analyze Kolam design data using Gemini API"""
        if not self.model:
            return {"error": "Gemini API not configured"}
        
        try:
            # Create a description of the design
            design_description = self._create_design_description(design_data)
            
            prompt = f"""
            Analyze this Kolam design data and provide insights:
            
            Design Data: {design_description}
            
            Please provide analysis on:
            1. Mathematical Properties: What mathematical patterns or rules are present?
            2. Symmetry Analysis: What types of symmetry does this design exhibit?
            3. Cultural Significance: Any traditional or cultural elements?
            4. Complexity Assessment: Rate the complexity and explain why
            5. Design Principles: What design principles are being used?
            6. Suggestions: How could this design be improved or extended?
            
            Format your response as a structured analysis.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "analysis": response.text,
                "design_description": design_description,
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def generate_kolam_suggestions(self, user_preferences: Dict) -> List[str]:
        """Generate Kolam design suggestions based on user preferences"""
        if not self.model:
            return ["Gemini API not configured"]
        
        try:
            preferences_text = json.dumps(user_preferences, indent=2)
            
            prompt = f"""
            Based on these user preferences for Kolam design:
            {preferences_text}
            
            Generate 5 creative Kolam design suggestions. For each suggestion, provide:
            1. Design name
            2. Brief description
            3. Key features
            4. Difficulty level (1-5)
            5. Cultural significance (if any)
            
            Format as a numbered list with clear sections for each suggestion.
            """
            
            response = self.model.generate_content(prompt)
            suggestions = response.text.split('\n\n')
            
            return [s.strip() for s in suggestions if s.strip()]
            
        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]
    
    def explain_kolam_tradition(self, topic: str) -> str:
        """Get educational content about Kolam traditions using Gemini"""
        if not self.model:
            return "Gemini API not configured"
        
        try:
            prompt = f"""
            Provide educational information about Kolam art tradition, specifically about: {topic}
            
            Include:
            1. Historical background
            2. Cultural significance
            3. Traditional techniques
            4. Regional variations
            5. Modern adaptations
            
            Make it informative and engaging for someone learning about this art form.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error getting information: {str(e)}"
    
    def analyze_uploaded_kolam(self, image: Image.Image) -> Dict:
        """Analyze uploaded Kolam image with detailed Gemini analysis"""
        if not self.model_vision:
            return {"error": "Gemini API not configured"}
        
        try:
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            prompt = """
            Analyze this Kolam (traditional Indian art form) image comprehensively:
            
            1. **Pattern Classification**: 
               - Is this dot-grid based, freehand, or mixed?
               - What is the grid structure (if any)?
            
            2. **Symmetry Analysis**:
               - What types of symmetry are present?
               - Rate the symmetry quality (1-10)
            
            3. **Design Elements**:
               - What geometric shapes are used?
               - What curves or motifs are present?
               - Any traditional symbols or patterns?
            
            4. **Mathematical Properties**:
               - What mathematical concepts are demonstrated?
               - Any fractal or recursive patterns?
            
            5. **Cultural Significance**:
               - Any religious or cultural symbolism?
               - Regional style indicators?
            
            6. **Technical Quality**:
               - Complexity level (1-10)
               - Precision of execution
               - Artistic merit
            
            7. **Suggestions**:
               - How could this design be improved?
               - Similar traditional patterns?
               - Modern adaptations possible?
            
            Provide detailed analysis in a structured format.
            """
            
            response = self.model_vision.generate_content([
                prompt, 
                {"mime_type": "image/png", "data": img_byte_arr}
            ])
            
            # Parse the response into structured data
            analysis = self._parse_comprehensive_response(response.text)
            
            return {
                "comprehensive_analysis": response.text,
                "structured_analysis": analysis,
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _create_design_description(self, design_data: Dict) -> str:
        """Create a text description of the design data"""
        grid_size = design_data.get('grid_size', 0)
        dots = design_data.get('dots', [])
        connections = design_data.get('connections', [])
        
        description = f"""
        Grid Size: {grid_size}x{grid_size}
        Number of Dots: {len(dots)}
        Number of Connections: {len(connections)}
        Dot Positions: {dots[:10]}{'...' if len(dots) > 10 else ''}
        Connection Types: {[c.get('type', 'line') for c in connections[:5]]}{'...' if len(connections) > 5 else ''}
        """
        
        return description
    
    def _parse_comprehensive_response(self, response_text: str) -> Dict:
        """Parse Gemini's comprehensive response into structured data"""
        analysis = {
            "pattern_classification": "Unknown",
            "symmetry_type": "Unknown",
            "symmetry_quality": 5,
            "design_elements": [],
            "mathematical_properties": [],
            "cultural_significance": "Standard Kolam",
            "complexity_level": 5,
            "technical_quality": "Good",
            "suggestions": []
        }
        
        # Simple parsing (in production, use more sophisticated NLP)
        lines = response_text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Pattern classification
            if 'dot-grid' in line_lower or 'grid-based' in line_lower:
                analysis["pattern_classification"] = "Dot-Grid Based"
            elif 'freehand' in line_lower:
                analysis["pattern_classification"] = "Freehand"
            
            # Symmetry
            if 'rotational' in line_lower:
                analysis["symmetry_type"] = "Rotational"
            elif 'reflectional' in line_lower:
                analysis["symmetry_type"] = "Reflectional"
            elif 'translational' in line_lower:
                analysis["symmetry_type"] = "Translational"
            
            # Extract numbers for quality/level ratings
            import re
            quality_match = re.search(r'quality[:\s]*(\d+)', line_lower)
            if quality_match:
                analysis["symmetry_quality"] = int(quality_match.group(1))
            
            complexity_match = re.search(r'complexity[:\s]*(\d+)', line_lower)
            if complexity_match:
                analysis["complexity_level"] = int(complexity_match.group(1))
        
        return analysis
    
    def get_learning_content(self) -> Dict[str, str]:
        """Get educational content about Kolam"""
        topics = {
            "history": "Historical origins and evolution of Kolam art",
            "techniques": "Traditional drawing techniques and methods",
            "cultural_significance": "Cultural and religious importance",
            "regional_variations": "Different regional styles and variations",
            "mathematical_aspects": "Mathematical principles in Kolam designs",
            "modern_applications": "Contemporary uses and adaptations"
        }
        
        content = {}
        for topic, description in topics.items():
            if self.model:
                content[topic] = self.explain_kolam_tradition(description)
            else:
                content[topic] = f"Gemini API not configured for: {description}"
        
        return content

def display_gemini_analysis(analysis: Dict) -> None:
    """Display Gemini analysis results in Streamlit"""
    if "error" in analysis:
        st.error(analysis["error"])
        return
    
    if "structured_analysis" in analysis:
        structured = analysis["structured_analysis"]
        
        # Create tabs for different analysis aspects
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Pattern Analysis", "🎨 Design Elements", "📚 Cultural Context", "💡 Suggestions"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pattern Type", structured.get("pattern_classification", "Unknown"))
                st.metric("Symmetry Type", structured.get("symmetry_type", "Unknown"))
            with col2:
                st.metric("Symmetry Quality", f"{structured.get('symmetry_quality', 5)}/10")
                st.metric("Complexity Level", f"{structured.get('complexity_level', 5)}/10")
        
        with tab2:
            elements = structured.get("design_elements", [])
            if elements:
                st.write("**Design Elements Found:**")
                for element in elements:
                    st.write(f"• {element}")
            else:
                st.write("Design elements analysis available in full text below.")
        
        with tab3:
            significance = structured.get("cultural_significance", "Standard Kolam")
            st.write(f"**Cultural Significance:** {significance}")
        
        with tab4:
            suggestions = structured.get("suggestions", [])
            if suggestions:
                st.write("**Improvement Suggestions:**")
                for suggestion in suggestions:
                    st.write(f"• {suggestion}")
    
    # Display full analysis
    st.subheader("📝 Detailed Analysis")
    if "comprehensive_analysis" in analysis:
        st.text_area("Full Gemini Analysis", analysis["comprehensive_analysis"], height=400)
    elif "analysis" in analysis:
        st.text_area("Full Analysis", analysis["analysis"], height=400)

def create_learning_interface(analyzer: GeminiKolamAnalyzer) -> None:
    """Create an educational interface using Gemini"""
    st.subheader("📚 Learn About Kolam Tradition")
    
    if not analyzer.model:
        st.warning("Gemini API not configured for learning content.")
        return
    
    # Topic selector
    topic = st.selectbox(
        "Choose a topic to learn about:",
        [
            "History & Origins",
            "Traditional Techniques", 
            "Cultural Significance",
            "Regional Variations",
            "Mathematical Aspects",
            "Modern Applications"
        ]
    )
    
    if st.button("📖 Get Educational Content"):
        with st.spinner("Generating educational content..."):
            content = analyzer.explain_kolam_tradition(topic)
            st.markdown(content)
