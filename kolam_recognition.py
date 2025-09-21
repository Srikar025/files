import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import numpy as np
from typing import Dict, List, Tuple
import cv2
from config import GEMINI_API_KEY

class KolamRecognizer:
    """Recognizes and analyzes Kolam patterns using Gemini API and computer vision"""
    
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            st.warning("Gemini API key not configured. Please set GEMINI_API_KEY in your environment.")
    
    def analyze_kolam_image(self, image: Image.Image) -> Dict:
        """Analyze uploaded Kolam image using Gemini API"""
        if not self.model:
            return {"error": "Gemini API not configured"}
        
        try:
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Analyze with Gemini
            prompt = """
            Analyze this Kolam (traditional Indian art form) image and provide detailed information about:
            
            1. Pattern Type: Is this a dot-grid based Kolam, freehand drawing, or symmetric pattern?
            2. Symmetry: What type of symmetry does this pattern exhibit? (rotational, reflectional, translational)
            3. Design Elements: What geometric shapes, curves, or motifs are present?
            4. Complexity: Rate the complexity from 1-10
            5. Cultural Significance: Any traditional motifs or symbolic elements?
            6. Grid Structure: If it's grid-based, estimate the grid size
            7. Mathematical Properties: Any mathematical patterns or rules visible?
            
            Please provide a detailed analysis in JSON format.
            """
            
            response = self.model.generate_content([prompt, {"mime_type": "image/png", "data": img_byte_arr}])
            
            # Parse response
            analysis = self._parse_gemini_response(response.text)
            
            # Add computer vision analysis
            cv_analysis = self._analyze_with_opencv(image)
            analysis.update(cv_analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse Gemini API response"""
        analysis = {
            "pattern_type": "Unknown",
            "symmetry": "Unknown", 
            "design_elements": [],
            "complexity": 5,
            "cultural_significance": "Standard Kolam pattern",
            "grid_structure": "Unknown",
            "mathematical_properties": "Standard geometric patterns"
        }
        
        # Simple parsing (in a real app, you'd want more robust JSON parsing)
        if "dot" in response_text.lower() and "grid" in response_text.lower():
            analysis["pattern_type"] = "Dot-grid based"
        elif "freehand" in response_text.lower():
            analysis["pattern_type"] = "Freehand"
        elif "symmetric" in response_text.lower():
            analysis["pattern_type"] = "Symmetric"
        
        if "rotational" in response_text.lower():
            analysis["symmetry"] = "Rotational symmetry"
        elif "reflectional" in response_text.lower():
            analysis["symmetry"] = "Reflectional symmetry"
        
        # Extract complexity if mentioned
        import re
        complexity_match = re.search(r'complexity[:\s]*(\d+)', response_text.lower())
        if complexity_match:
            analysis["complexity"] = int(complexity_match.group(1))
        
        return analysis
    
    def _analyze_with_opencv(self, image: Image.Image) -> Dict:
        """Perform computer vision analysis using OpenCV"""
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
        
        # Detect circles (dots)
        circles = cv2.HoughCircles(
            img_gray, cv2.HOUGH_GRADIENT, 1, 20,
            param1=50, param2=30, minRadius=5, maxRadius=50
        )
        
        # Detect lines
        edges = cv2.Canny(img_gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
        
        # Analyze symmetry
        symmetry_score = self._calculate_symmetry_score(img_gray)
        
        cv_analysis = {
            "detected_circles": len(circles[0]) if circles is not None else 0,
            "detected_lines": len(lines) if lines is not None else 0,
            "symmetry_score": symmetry_score,
            "image_edges": edges,
            "is_grid_based": circles is not None and len(circles[0]) > 4
        }
        
        return cv_analysis
    
    def _calculate_symmetry_score(self, img_gray: np.ndarray) -> float:
        """Calculate symmetry score of the image"""
        h, w = img_gray.shape
        center_x = w // 2
        
        # Check vertical symmetry
        left_half = img_gray[:, :center_x]
        right_half = img_gray[:, center_x:]
        
        # Flip right half
        right_half_flipped = cv2.flip(right_half, 1)
        
        # Resize to match
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = right_half_flipped[:, :min_width]
        
        # Calculate similarity
        diff = cv2.absdiff(left_half, right_half_flipped)
        symmetry_score = 1.0 - (np.mean(diff) / 255.0)
        
        return max(0, min(1, symmetry_score))
    
    def classify_pattern_type(self, analysis: Dict) -> str:
        """Classify the pattern type based on analysis"""
        if analysis.get("is_grid_based", False):
            return "Dot-Grid Based Kolam"
        elif analysis.get("symmetry_score", 0) > 0.8:
            return "Symmetric Freehand Kolam"
        else:
            return "Freehand Kolam"
    
    def extract_design_principles(self, analysis: Dict) -> List[str]:
        """Extract design principles from the analysis"""
        principles = []
        
        if analysis.get("symmetry_score", 0) > 0.7:
            principles.append("High Rotational Symmetry")
        
        if analysis.get("detected_circles", 0) > 4:
            principles.append("Dot-Grid Structure")
        
        if analysis.get("detected_lines", 0) > 10:
            principles.append("Complex Line Patterns")
        
        if analysis.get("complexity", 5) > 7:
            principles.append("High Complexity Design")
        elif analysis.get("complexity", 5) < 4:
            principles.append("Simple Elegant Design")
        
        # Add more principles based on analysis
        if "floral" in str(analysis.get("design_elements", [])).lower():
            principles.append("Floral Motifs")
        
        if "geometric" in str(analysis.get("design_elements", [])).lower():
            principles.append("Geometric Patterns")
        
        return principles

def create_analysis_visualization(analysis: Dict) -> None:
    """Create visualizations for the analysis results"""
    if "error" in analysis:
        st.error(analysis["error"])
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Pattern Analysis")
        
        # Pattern type
        pattern_type = analysis.get("pattern_type", "Unknown")
        st.metric("Pattern Type", pattern_type)
        
        # Symmetry
        symmetry = analysis.get("symmetry", "Unknown")
        st.metric("Symmetry Type", symmetry)
        
        # Complexity
        complexity = analysis.get("complexity", 5)
        st.metric("Complexity", f"{complexity}/10")
        
        # Symmetry score
        symmetry_score = analysis.get("symmetry_score", 0)
        st.metric("Symmetry Score", f"{symmetry_score:.2f}")
    
    with col2:
        st.subheader("🔍 Technical Analysis")
        
        # Detected elements
        circles = analysis.get("detected_circles", 0)
        lines = analysis.get("detected_lines", 0)
        
        st.metric("Detected Dots", circles)
        st.metric("Detected Lines", lines)
        
        # Design principles
        principles = analysis.get("design_principles", [])
        if principles:
            st.subheader("🎨 Design Principles")
            for principle in principles:
                st.write(f"• {principle}")
    
    # Show edge detection if available
    if "image_edges" in analysis:
        st.subheader("🔍 Edge Detection Analysis")
        edges = analysis["image_edges"]
        if edges is not None:
            st.image(edges, caption="Detected Edges", use_column_width=True)
