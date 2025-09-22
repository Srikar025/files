import streamlit as st
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import math
from scipy import ndimage
from skimage import feature, measure
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import plotly.graph_objects as go
import plotly.express as px

# Remove top-level page config and CSS; they will be applied inside functions to avoid import-time Streamlit calls

def _inject_css():
    """Inject component-specific CSS. Safe to call inside a render function."""
    st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E4057;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .tool-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .pattern-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .export-section {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #228B22;
    }
    .edge-component-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

class KolamEditor:
    def __init__(self):
        self.canvas_size = (800, 600)
        self.grid_size = 20
        self.dots = []
        self.lines = []
        self.curves = []
        
    def create_grid_dots(self, width, height, spacing):
        """Create a grid of dots for the kolam base"""
        dots = []
        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                dots.append((x, y))
        return dots
    
    def convert_edges_to_components(self, edge_image, canvas_width=800, canvas_height=600):
        """Convert edge detection image to editable drawing components"""
        components = []
        
        # Resize edge image to match canvas
        edge_resized = cv2.resize(edge_image, (canvas_width, canvas_height))
        
        # Find contours in the edge image
        contours, _ = cv2.findContours(edge_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            # Filter out very small contours
            if cv2.contourArea(contour) < 50:
                continue
                
            # Convert contour to points
            points = contour.reshape(-1, 2)
            
            # Flip Y coordinates to match Plotly coordinate system
            points[:, 1] = canvas_height - points[:, 1]
            
            # Simplify contour to reduce points
            epsilon = 0.02 * cv2.arcLength(contour, True)
            simplified = cv2.approxPolyDP(contour, epsilon, True)
            simplified_points = simplified.reshape(-1, 2)
            simplified_points[:, 1] = canvas_height - simplified_points[:, 1]
            
            # Determine if it's more line-like or curve-like
            is_curved = len(simplified_points) > 4
            
            component = {
                'id': f'edge_component_{i}',
                'type': 'curve' if is_curved else 'line',
                'x': simplified_points[:, 0].tolist(),
                'y': simplified_points[:, 1].tolist(),
                'color': '#000000',
                'width': 2,
                'editable': True,
                'source': 'edge_detection',
                'original_points': points.tolist()  # Keep original for reference
            }
            
            components.append(component)
        
        return components
    
    def extract_line_segments(self, edge_image, canvas_width=800, canvas_height=600):
        """Extract line segments using Hough Line Transform"""
        components = []
        
        # Resize edge image to match canvas
        edge_resized = cv2.resize(edge_image, (canvas_width, canvas_height))
        
        # Use HoughLinesP for line segment detection
        lines = cv2.HoughLinesP(edge_resized, 1, np.pi/180, threshold=50, 
                               minLineLength=30, maxLineGap=10)
        
        if lines is not None:
            for i, line in enumerate(lines):
                x1, y1, x2, y2 = line[0]
                
                # Flip Y coordinates to match Plotly coordinate system
                y1 = canvas_height - y1
                y2 = canvas_height - y2
                
                component = {
                    'id': f'line_segment_{i}',
                    'type': 'line',
                    'x': [x1, x2],
                    'y': [y1, y2],
                    'color': '#000000',
                    'width': 2,
                    'editable': True,
                    'source': 'hough_lines'
                }
                
                components.append(component)
        
        return components
    
    def analyze_symmetry(self, image_array):
        """Analyze rotational and reflective symmetry"""
        center = (image_array.shape[1]//2, image_array.shape[0]//2)
        
        # Test for rotational symmetry
        rotational_orders = []
        for order in [2, 3, 4, 6, 8]:
            angle = 360 / order
            rotated = ndimage.rotate(image_array, angle, reshape=False, order=0)
            correlation = cv2.matchTemplate(image_array.astype(np.uint8), 
                                          rotated.astype(np.uint8), 
                                          cv2.TM_CCOEFF_NORMED)[0][0]
            if correlation > 0.8:  # Threshold for similarity
                rotational_orders.append(order)
        
        # Test for reflective symmetry
        reflective_axes = []
        # Horizontal reflection
        h_flipped = np.flipud(image_array)
        h_corr = cv2.matchTemplate(image_array.astype(np.uint8), 
                                  h_flipped.astype(np.uint8), 
                                  cv2.TM_CCOEFF_NORMED)[0][0]
        if h_corr > 0.8:
            reflective_axes.append("horizontal")
            
        # Vertical reflection
        v_flipped = np.fliplr(image_array)
        v_corr = cv2.matchTemplate(image_array.astype(np.uint8), 
                                  v_flipped.astype(np.uint8), 
                                  cv2.TM_CCOEFF_NORMED)[0][0]
        if v_corr > 0.8:
            reflective_axes.append("vertical")
        
        return {
            "rotational_orders": rotational_orders,
            "reflective_axes": reflective_axes
        }
    
    def detect_patterns(self, image_array):
        """Detect curves, lines, and repetitive patterns"""
        # Edge detection
        edges = cv2.Canny(image_array.astype(np.uint8), 50, 150)
        
        # Line detection using Hough Transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        line_count = len(lines) if lines is not None else 0
        
        # Contour detection for curves
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contour properties
        curve_patterns = []
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if area > 100:  # Filter small contours
                # Approximate contour to polygon
                epsilon = 0.02 * perimeter
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) < 8:  # More angular
                    curve_patterns.append("angular")
                else:  # More curved
                    curve_patterns.append("curved")
        
        return {
            "line_count": line_count,
            "curve_count": len(contours),
            "curve_patterns": curve_patterns
        }
    
    def extract_design_principles(self, image_array):
        """Extract comprehensive design principles"""
        symmetry = self.analyze_symmetry(image_array)
        patterns = self.detect_patterns(image_array)
        
        # Calculate complexity score
        complexity = (patterns["line_count"] + patterns["curve_count"]) / 100
        
        return {
            "symmetry": symmetry,
            "patterns": patterns,
            "complexity_score": min(complexity, 1.0),
            "dominant_patterns": self.identify_dominant_patterns(image_array)
        }
    
    def identify_dominant_patterns(self, image_array):
        """Identify dominant visual patterns"""
        # Simple pattern analysis based on image properties
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY) if len(image_array.shape) == 3 else image_array
        
        # Texture analysis
        glcm = feature.graycomatrix(gray, [1], [0], symmetric=True, normed=True)
        contrast = feature.graycoprops(glcm, 'contrast')[0, 0]
        homogeneity = feature.graycoprops(glcm, 'homogeneity')[0, 0]
        
        patterns = []
        if contrast > 0.5:
            patterns.append("high_contrast")
        if homogeneity > 0.8:
            patterns.append("uniform_texture")
        
        return patterns

def create_drawing_interface():
    """Create the main drawing interface"""
    _inject_css()
    st.markdown('<div class="main-header">🎨 Kolam Editor - Draw Online</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'editor' not in st.session_state:
        st.session_state.editor = KolamEditor()
    if 'canvas_image' not in st.session_state:
        st.session_state.canvas_image = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'add_parsed_to_canvas' not in st.session_state:
        st.session_state.add_parsed_to_canvas = False
    if 'selected_color' not in st.session_state:
        st.session_state.selected_color = "#000000"
    if 'drawing_elements' not in st.session_state:
        st.session_state.drawing_elements = []
    if 'current_drawing_mode' not in st.session_state:
        st.session_state.current_drawing_mode = "Free Draw"
    if 'tools_settings' not in st.session_state:
        st.session_state.tools_settings = {}
    if 'edge_components' not in st.session_state:
        st.session_state.edge_components = []
    if 'selected_component_ids' not in st.session_state:
        st.session_state.selected_component_ids = []

def create_sidebar_tools():
    """Create sidebar with drawing tools and options"""
    st.sidebar.header("🛠️ Drawing Tools")
    
    # Drawing mode selection
    drawing_mode = st.sidebar.selectbox(
        "Select Drawing Mode",
        ["Free Draw", "Grid Dots", "Lines", "Curves", "Patterns", "Edit Components"],
        index=["Free Draw", "Grid Dots", "Lines", "Curves", "Patterns", "Edit Components"].index(st.session_state.current_drawing_mode) if st.session_state.current_drawing_mode in ["Free Draw", "Grid Dots", "Lines", "Curves", "Patterns", "Edit Components"] else 0,
        key="sidebar_drawing_mode_selectbox"
    )
    
    # Update session state when mode changes
    if drawing_mode != st.session_state.current_drawing_mode:
        st.session_state.current_drawing_mode = drawing_mode
        st.rerun()
    
    # Color selection
    stroke_color = st.sidebar.color_picker("Stroke Color", st.session_state.selected_color, key="sidebar_color_picker")
    
    # Quick color buttons
    st.sidebar.write("Quick Colors:")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button("Black", key="sidebar_black_color"):
            st.session_state.selected_color = "#000000"
            st.rerun()
    with col2:
        if st.button("White", key="sidebar_white_color"):
            st.session_state.selected_color = "#FFFFFF"
            st.rerun()
    with col3:
        if st.button("Red", key="sidebar_red_color"):
            st.session_state.selected_color = "#FF0000"
            st.rerun()
    
    # Update stroke color from session state
    if st.session_state.selected_color != stroke_color:
        stroke_color = st.session_state.selected_color
    
    # Show current selected color
    st.sidebar.write(f"**Current Color:** {st.session_state.selected_color}")
    st.sidebar.color_picker("", st.session_state.selected_color, disabled=True, key="sidebar_color_display")
    
    # Brush settings
    brush_size = st.sidebar.slider("Brush Size", 1, 20, 3, key="sidebar_brush_size_slider")
    
    # Edge component controls
    if st.session_state.edge_components:
        st.sidebar.markdown("---")
        st.sidebar.header("🔧 Edge Components")
        st.sidebar.write(f"**Total Components:** {len(st.session_state.edge_components)}")
        
        # Component selection
        component_options = [f"{comp['id']} ({comp['type']})" for comp in st.session_state.edge_components]
        selected_components = st.sidebar.multiselect(
            "Select Components to Edit:",
            component_options,
            key="sidebar_component_multiselect"
        )
        
        # Update selected component IDs
        st.session_state.selected_component_ids = [
            comp['id'] for comp in st.session_state.edge_components 
            if f"{comp['id']} ({comp['type']})" in selected_components
        ]
        
        if st.session_state.selected_component_ids:
            st.sidebar.write(f"**Selected:** {len(st.session_state.selected_component_ids)} components")
            
            # Bulk edit controls
            if st.sidebar.button("Change Color of Selected", key="sidebar_change_color"):
                for comp in st.session_state.edge_components:
                    if comp['id'] in st.session_state.selected_component_ids:
                        comp['color'] = st.session_state.selected_color
                st.success("Color updated!")
                st.rerun()
            
            if st.sidebar.button("Delete Selected", key="sidebar_delete_selected"):
                st.session_state.edge_components = [
                    comp for comp in st.session_state.edge_components 
                    if comp['id'] not in st.session_state.selected_component_ids
                ]
                st.session_state.selected_component_ids = []
                st.success("Selected components deleted!")
                st.rerun()
        
        # Clear all edge components
        if st.sidebar.button("Clear All Edge Components", key="sidebar_clear_edges"):
            st.session_state.edge_components = []
            st.session_state.selected_component_ids = []
            st.success("All edge components cleared!")
            st.rerun()
    
    # Mode-specific settings
    if drawing_mode == "Grid Dots":
        grid_spacing = st.sidebar.slider("Grid Spacing", 10, 50, 20, key="sidebar_grid_spacing_slider")
        show_grid = st.sidebar.checkbox("Show Grid", True, key="sidebar_show_grid_checkbox")
        st.sidebar.info("Click on grid points to create patterns")
    elif drawing_mode == "Lines":
        line_style = st.sidebar.selectbox("Line Style", ["Solid", "Dashed", "Dotted"], key="sidebar_line_style_selectbox")
        st.sidebar.info("Click two points to draw a line")
    elif drawing_mode == "Curves":
        curve_smoothness = st.sidebar.slider("Curve Smoothness", 1, 10, 5, key="sidebar_curve_smoothness_slider")
        st.sidebar.info("Click multiple points to create smooth curves")
    elif drawing_mode == "Patterns":
        pattern_type = st.sidebar.selectbox("Pattern Type", ["Flower", "Spiral", "Geometric", "Mandala"], key="sidebar_pattern_type_selectbox")
        pattern_size = st.sidebar.slider("Pattern Size", 50, 200, 100, key="sidebar_pattern_size_slider")
        st.sidebar.info("Click to place pattern at that location")
    elif drawing_mode == "Edit Components":
        st.sidebar.info("Select and edit edge components from parsed images")
        if not st.session_state.edge_components:
            st.sidebar.warning("No edge components available. Parse an image first!")
    else:  # Free Draw
        st.sidebar.info("Draw freely with your mouse/touch")
        grid_spacing = 20
        show_grid = False
        line_style = "Solid"
        curve_smoothness = 5
        pattern_type = "Flower"
        pattern_size = 100
    
    tools_settings = {
        "mode": drawing_mode,
        "color": stroke_color,
        "brush_size": brush_size,
        "grid_spacing": grid_spacing if drawing_mode == "Grid Dots" else 20,
        "show_grid": show_grid if drawing_mode == "Grid Dots" else False,
        "line_style": line_style if drawing_mode == "Lines" else "Solid",
        "curve_smoothness": curve_smoothness if drawing_mode == "Curves" else 5,
        "pattern_type": pattern_type if drawing_mode == "Patterns" else "Flower",
        "pattern_size": pattern_size if drawing_mode == "Patterns" else 100
    }
    
    # Store in session state
    st.session_state.tools_settings = tools_settings
    
    return tools_settings

def create_simple_canvas(tools=None):
    """Create an interactive drawing canvas using Plotly"""
    fig = go.Figure()
    
    # Get current settings
    current_color = st.session_state.get('selected_color', '#000000')
    drawing_mode = st.session_state.get('current_drawing_mode', 'Free Draw')
    
    # Use provided tools or get from session state
    if tools is None:
        tools = st.session_state.get('tools_settings', {
            'brush_size': 3,
            'grid_spacing': 20,
            'show_grid': False
        })
    
    # Set up the canvas
    fig.update_layout(
        title=f"Kolam Drawing Canvas - {drawing_mode} Mode",
        xaxis=dict(range=[0, 800], showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(range=[0, 600], showgrid=True, gridwidth=1, gridcolor='lightgray'),
        width=800,
        height=600,
        showlegend=False,
        dragmode='drawline',
        newshape=dict(line_color=current_color, line_width=tools.get('brush_size', 3)),
    )
    
    # Add edge components first (so they appear below other elements)
    for component in st.session_state.edge_components:
        # Highlight selected components
        line_color = component['color']
        line_width = component['width']
        opacity = 1.0
        
        if component['id'] in st.session_state.selected_component_ids:
            line_color = '#ff6b6b'  # Red highlight for selected
            line_width = max(line_width + 2, 4)
            opacity = 0.8
        
        if component['type'] == 'line':
            fig.add_trace(go.Scatter(
                x=component['x'], y=component['y'],
                mode='lines',
                line=dict(color=line_color, width=line_width),
                opacity=opacity,
                name=f"Edge: {component['id']}",
                showlegend=False,
                hoverinfo='text',
                hovertext=f"Edge Component: {component['id']}<br>Type: {component['type']}<br>Click to select"
            ))
        elif component['type'] == 'curve':
            fig.add_trace(go.Scatter(
                x=component['x'], y=component['y'],
                mode='lines',
                line=dict(color=line_color, width=line_width, shape='spline'),
                opacity=opacity,
                name=f"Edge: {component['id']}",
                showlegend=False,
                hoverinfo='text',
                hovertext=f"Edge Component: {component['id']}<br>Type: {component['type']}<br>Points: {len(component['x'])}"
            ))
    
    # Add existing drawing elements
    for element in st.session_state.drawing_elements:
        if element['type'] == 'line':
            fig.add_trace(go.Scatter(
                x=element['x'], y=element['y'],
                mode='lines',
                line=dict(color=element['color'], width=element['width']),
                showlegend=False,
                hoverinfo='none'
            ))
        elif element['type'] == 'curve':
            fig.add_trace(go.Scatter(
                x=element['x'], y=element['y'],
                mode='lines',
                line=dict(color=element['color'], width=element['width'], shape='spline'),
                showlegend=False,
                hoverinfo='none'
            ))
        elif element['type'] == 'pattern':
            fig.add_trace(go.Scatter(
                x=element['x'], y=element['y'],
                mode='markers+lines',
                marker=dict(color=element['color'], size=element['size']),
                line=dict(color=element['color'], width=element['width']),
                showlegend=False,
                hoverinfo='none'
            ))
        elif element['type'] == 'grid_point':
            fig.add_trace(go.Scatter(
                x=element['x'], y=element['y'],
                mode='markers',
                marker=dict(color=element['color'], size=element['size']),
                showlegend=False,
                hoverinfo='none'
            ))
    
    # Add grid dots based on mode
    if drawing_mode == "Grid Dots" or tools.get('show_grid', False):
        grid_spacing = tools.get('grid_spacing', 20)
        grid_x, grid_y = np.meshgrid(np.arange(0, 801, grid_spacing), np.arange(0, 601, grid_spacing))
        fig.add_trace(go.Scatter(
            x=grid_x.flatten(),
            y=grid_y.flatten(),
            mode='markers',
            marker=dict(size=4, color='black', opacity=0.7),
            name='Grid Dots',
            hoverinfo='none'
        ))
    
    return fig

def image_upload_section():
    """Handle image upload and processing"""
    st.markdown('<div class="tool-section">', unsafe_allow_html=True)
    st.header("📤 Upload & Parse Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image file (PNG, JPG, JPEG)",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a kolam image to parse and recreate on the drawing board",
        key="main_file_uploader"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Convert to numpy array for processing
        image_array = np.array(image)
        
        # Process and analyze the image
        if st.button("Parse & Analyze Image", type="primary", key="main_parse_analyze_btn"):
            editor = st.session_state.editor
            
            with st.spinner("Analyzing image patterns..."):
                analysis = editor.extract_design_principles(image_array)
                st.session_state.analysis_results = analysis
                st.session_state.canvas_image = image_array
            
            st.success("Image analyzed successfully! Check the Pattern Analysis section below.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def pattern_analysis_section():
    """Display pattern analysis results"""
    if st.session_state.analysis_results:
        st.markdown('<div class="pattern-info">', unsafe_allow_html=True)
        st.header("🔍 Pattern Analysis")
        
        analysis = st.session_state.analysis_results
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Symmetry Properties")
            symmetry = analysis["symmetry"]
            
            if symmetry["rotational_orders"]:
                st.write(f"**Rotational Symmetry:** {symmetry['rotational_orders']}-fold")
            else:
                st.write("**Rotational Symmetry:** None detected")
            
            if symmetry["reflective_axes"]:
                st.write(f"**Reflective Symmetry:** {', '.join(symmetry['reflective_axes'])}")
            else:
                st.write("**Reflective Symmetry:** None detected")
        
        with col2:
            st.subheader("Pattern Details")
            patterns = analysis["patterns"]
            
            st.metric("Lines Detected", patterns["line_count"])
            st.metric("Curves Detected", patterns["curve_count"])
            st.metric("Complexity Score", f"{analysis['complexity_score']:.2f}")
        
        # Pattern visualization
        if st.session_state.canvas_image is not None:
            st.subheader("Pattern Visualization")
            
            # Create edge detection visualization
            gray = cv2.cvtColor(st.session_state.canvas_image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Store edge detection image in session state
            if 'edge_detection_image' not in st.session_state:
                st.session_state.edge_detection_image = edges
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(st.session_state.canvas_image, caption="Original", use_column_width=True)
            with col2:
                st.image(st.session_state.edge_detection_image, caption="Edge Detection", use_column_width=True)
            
            # Edge detection controls
            st.subheader("🎛️ Edge Detection Controls")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Canny threshold controls
                low_threshold = st.slider("Low Threshold", 10, 200, 50, key="analysis_low_threshold")
                high_threshold = st.slider("High Threshold", 50, 300, 150, key="analysis_high_threshold")
                
                if st.button("Update Edge Detection", key="analysis_update_edges"):
                    new_edges = cv2.Canny(gray, low_threshold, high_threshold)
                    st.session_state.edge_detection_image = new_edges
                    st.success("Edge detection updated!")
                    st.rerun()
            
            with col2:
                # Morphological operations
                if st.button("Dilate Edges", key="analysis_dilate"):
                    kernel = np.ones((3,3), np.uint8)
                    dilated = cv2.dilate(st.session_state.edge_detection_image, kernel, iterations=1)
                    st.session_state.edge_detection_image = dilated
                    st.success("Edges dilated!")
                    st.rerun()
                
                if st.button("Erode Edges", key="analysis_erode"):
                    kernel = np.ones((3,3), np.uint8)
                    eroded = cv2.erode(st.session_state.edge_detection_image, kernel, iterations=1)
                    st.session_state.edge_detection_image = eroded
                    st.success("Edges eroded!")
                    st.rerun()
            
            with col3:
                # Component conversion controls
                st.write("**Convert to Editable Components:**")
                
                # Component conversion method selection
                conversion_method = st.selectbox(
                    "Conversion Method:",
                    ["Contour Tracing", "Line Segments", "Both"],
                    key="analysis_conversion_method"
                )
                
                if st.button("Convert to Components", type="primary", key="analysis_convert_components"):
                    editor = st.session_state.editor
                    
                    with st.spinner("Converting edges to editable components..."):
                        if conversion_method in ["Contour Tracing", "Both"]:
                            contour_components = editor.convert_edges_to_components(
                                st.session_state.edge_detection_image
                            )
                            st.session_state.edge_components.extend(contour_components)
                        
                        if conversion_method in ["Line Segments", "Both"]:
                            line_components = editor.extract_line_segments(
                                st.session_state.edge_detection_image
                            )
                            st.session_state.edge_components.extend(line_components)
                    
                    st.success(f"✅ {len(st.session_state.edge_components)} components created and ready for editing!")
                    
                    # Switch to edit mode
                    st.session_state.current_drawing_mode = "Edit Components"
                    st.rerun()
                
                if st.button("Reset Conversion", key="analysis_reset_conversion"):
                    st.session_state.edge_components = []
                    st.session_state.selected_component_ids = []
                    st.success("Component conversion reset!")
                    st.rerun()
                
                if st.button("Reset Edge Detection", key="analysis_reset_edges"):
                    # Reset to original edge detection
                    original_edges = cv2.Canny(gray, 50, 150)
                    st.session_state.edge_detection_image = original_edges
                    st.success("Edge detection reset!")
                    st.rerun()
        
        # Edge Components Information
        if st.session_state.edge_components:
            st.markdown('<div class="edge-component-info">', unsafe_allow_html=True)
            st.subheader("🔧 Editable Components Created")
            
            component_stats = {}
            for comp in st.session_state.edge_components:
                comp_type = comp['type']
                component_stats[comp_type] = component_stats.get(comp_type, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Components", len(st.session_state.edge_components))
            with col2:
                st.metric("Lines", component_stats.get('line', 0))
            with col3:
                st.metric("Curves", component_stats.get('curve', 0))
            
            st.info("💡 **Components are now editable!** Switch to 'Edit Components' mode in the sidebar to select, modify colors, or delete individual components.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def export_section():
    """Handle pattern export functionality"""
    st.markdown('<div class="export-section">', unsafe_allow_html=True)
    st.header("💾 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export as PNG", type="secondary", key="export_png_btn"):
            if st.session_state.canvas_image is not None or st.session_state.drawing_elements or st.session_state.edge_components:
                st.success("PNG export feature - Implementation needed for canvas rendering")
            else:
                st.warning("No pattern to export. Please draw or upload an image first.")
    
    with col2:
        if st.button("Export Analysis", type="secondary", key="export_analysis_btn"):
            if st.session_state.analysis_results:
                analysis_json = json.dumps(st.session_state.analysis_results, indent=2, default=str)
                st.download_button(
                    label="Download Analysis (JSON)",
                    data=analysis_json,
                    file_name="kolam_analysis.json",
                    mime="application/json",
                    key="download_analysis_btn"
                )
            else:
                st.warning("No analysis to export. Please analyze a pattern first.")
    
    with col3:
        if st.button("Export Components", type="secondary", key="export_components_btn"):
            if st.session_state.edge_components or st.session_state.drawing_elements:
                all_components = {
                    "edge_components": st.session_state.edge_components,
                    "drawing_elements": st.session_state.drawing_elements
                }
                components_json = json.dumps(all_components, indent=2, default=str)
                st.download_button(
                    label="Download Components (JSON)",
                    data=components_json,
                    file_name="kolam_components.json",
                    mime="application/json",
                    key="download_components_btn"
                )
            else:
                st.warning("No components to export. Please create some components first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def drawing_canvas_section():
    """Main drawing canvas section"""
    st.header("🎨 Drawing Canvas")
    
    # Get tool settings once at the beginning
    tools = create_sidebar_tools()
    
    # Create tabs for different drawing modes
    tab1, tab2, tab3 = st.tabs(["Canvas", "Templates", "Tutorial"])
    
    with tab1:
        st.markdown("""
        **Instructions:**
        - Use the drawing tools in the sidebar to customize your drawing
        - Switch to "Edit Components" mode to modify parsed edge components
        - Click on edge components to select them (they'll turn red)
        - Use bulk operations to modify multiple components at once
        """)
        
        # Edge components status
        if st.session_state.edge_components:
            st.markdown('<div class="edge-component-info">', unsafe_allow_html=True)
            st.subheader("🔧 Edge Components Status")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Components", len(st.session_state.edge_components))
            with col2:
                st.metric("Selected", len(st.session_state.selected_component_ids))
            with col3:
                lines = sum(1 for comp in st.session_state.edge_components if comp['type'] == 'line')
                st.metric("Lines", lines)
            with col4:
                curves = sum(1 for comp in st.session_state.edge_components if comp['type'] == 'curve')
                st.metric("Curves", curves)
            
            # Quick component operations
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Select All", key="canvas_select_all"):
                    st.session_state.selected_component_ids = [comp['id'] for comp in st.session_state.edge_components]
                    st.success("All components selected!")
                    st.rerun()
            with col2:
                if st.button("Deselect All", key="canvas_deselect_all"):
                    st.session_state.selected_component_ids = []
                    st.success("All components deselected!")
                    st.rerun()
            with col3:
                if st.button("Hide Selected", key="canvas_hide_selected"):
                    for comp in st.session_state.edge_components:
                        if comp['id'] in st.session_state.selected_component_ids:
                            comp['hidden'] = True
                    st.success("Selected components hidden!")
                    st.rerun()
            with col4:
                if st.button("Show All", key="canvas_show_all"):
                    for comp in st.session_state.edge_components:
                        comp.pop('hidden', None)
                    st.success("All components shown!")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Simple drawing interface
        canvas_fig = create_simple_canvas(tools)
        st.plotly_chart(canvas_fig, use_container_width=True)
        
        # Drawing mode specific controls
        drawing_mode = tools['mode']
        
        if drawing_mode == "Edit Components":
            if st.session_state.edge_components:
                st.subheader("🎯 Component Editor")
                
                # Component details for selected items
                if st.session_state.selected_component_ids:
                    selected_comps = [comp for comp in st.session_state.edge_components 
                                    if comp['id'] in st.session_state.selected_component_ids]
                    
                    st.write(f"**Editing {len(selected_comps)} selected components:**")
                    
                    # Color modification
                    col1, col2 = st.columns(2)
                    with col1:
                        new_color = st.color_picker("New Color for Selected", value="#000000", key="component_color_picker")
                        if st.button("Apply Color", key="component_apply_color"):
                            for comp in st.session_state.edge_components:
                                if comp['id'] in st.session_state.selected_component_ids:
                                    comp['color'] = new_color
                            st.success(f"Color applied to {len(selected_comps)} components!")
                            st.rerun()
                    
                    with col2:
                        new_width = st.slider("Line Width", 1, 10, 2, key="component_width_slider")
                        if st.button("Apply Width", key="component_apply_width"):
                            for comp in st.session_state.edge_components:
                                if comp['id'] in st.session_state.selected_component_ids:
                                    comp['width'] = new_width
                            st.success(f"Width applied to {len(selected_comps)} components!")
                            st.rerun()
                    
                    # Advanced operations
                    st.subheader("🔧 Advanced Operations")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Smooth Selected Curves", key="component_smooth_curves"):
                            smoothed_count = 0
                            for comp in st.session_state.edge_components:
                                if comp['id'] in st.session_state.selected_component_ids and comp['type'] == 'curve':
                                    # Simple smoothing by reducing points
                                    if len(comp['x']) > 10:
                                        step = len(comp['x']) // 8
                                        comp['x'] = comp['x'][::step]
                                        comp['y'] = comp['y'][::step]
                                        smoothed_count += 1
                            st.success(f"Smoothed {smoothed_count} curves!")
                            st.rerun()
                    
                    with col2:
                        if st.button("Convert to Lines", key="component_convert_lines"):
                            converted_count = 0
                            for comp in st.session_state.edge_components:
                                if comp['id'] in st.session_state.selected_component_ids and comp['type'] == 'curve':
                                    comp['type'] = 'line'
                                    converted_count += 1
                            st.success(f"Converted {converted_count} curves to lines!")
                            st.rerun()
                    
                    with col3:
                        if st.button("Duplicate Selected", key="component_duplicate"):
                            new_components = []
                            for comp in st.session_state.edge_components:
                                if comp['id'] in st.session_state.selected_component_ids:
                                    new_comp = comp.copy()
                                    new_comp['id'] = f"{comp['id']}_copy"
                                    # Offset the duplicate slightly
                                    new_comp['x'] = [x + 20 for x in comp['x']]
                                    new_comp['y'] = [y + 20 for y in comp['y']]
                                    new_components.append(new_comp)
                            st.session_state.edge_components.extend(new_components)
                            st.success(f"Duplicated {len(new_components)} components!")
                            st.rerun()
                else:
                    st.info("Select components using the sidebar controls to edit them here.")
            else:
                st.warning("No edge components available. Parse an image first to create editable components.")
        
        elif drawing_mode == "Grid Dots":
            st.subheader("🎯 Grid Dots Mode")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add Grid Point", key="canvas_add_grid_point"):
                    # Simulate adding a grid point
                    new_element = {
                        'type': 'grid_point',
                        'x': [400], 'y': [300],
                        'color': st.session_state.selected_color,
                        'size': 8
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Grid point added!")
                    st.rerun()
            with col2:
                if st.button("Connect Points", key="canvas_connect_points"):
                    st.info("Click on two grid points to connect them")
        
        elif drawing_mode == "Lines":
            st.subheader("📏 Lines Mode")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Draw Line", key="canvas_draw_line"):
                    # Simulate drawing a line
                    new_element = {
                        'type': 'line',
                        'x': [100, 700], 'y': [300, 300],
                        'color': st.session_state.selected_color,
                        'width': 3
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Line drawn!")
                    st.rerun()
            with col2:
                if st.button("Draw Diagonal", key="canvas_draw_diagonal"):
                    new_element = {
                        'type': 'line',
                        'x': [100, 700], 'y': [100, 500],
                        'color': st.session_state.selected_color,
                        'width': 3
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Diagonal line drawn!")
                    st.rerun()
        
        elif drawing_mode == "Curves":
            st.subheader("🌊 Curves Mode")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Draw Curve", key="canvas_draw_curve"):
                    # Simulate drawing a curve
                    x_points = np.linspace(100, 700, 20)
                    y_points = 300 + 100 * np.sin((x_points - 100) * np.pi / 600)
                    new_element = {
                        'type': 'curve',
                        'x': x_points.tolist(), 'y': y_points.tolist(),
                        'color': st.session_state.selected_color,
                        'width': 3
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Curve drawn!")
                    st.rerun()
            with col2:
                if st.button("Draw Spiral", key="canvas_draw_spiral"):
                    t = np.linspace(0, 4*np.pi, 50)
                    x_points = 400 + 50 * t * np.cos(t)
                    y_points = 300 + 50 * t * np.sin(t)
                    new_element = {
                        'type': 'curve',
                        'x': x_points.tolist(), 'y': y_points.tolist(),
                        'color': st.session_state.selected_color,
                        'width': 3
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Spiral drawn!")
                    st.rerun()
        
        elif drawing_mode == "Patterns":
            st.subheader("🌸 Patterns Mode")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Flower Pattern", key="canvas_flower_pattern"):
                    # Create flower pattern
                    center_x, center_y = 400, 300
                    petals = 8
                    radius = 100
                    x_points, y_points = [], []
                    for i in range(petals):
                        angle = 2 * np.pi * i / petals
                        x_points.extend([center_x, center_x + radius * np.cos(angle)])
                        y_points.extend([center_y, center_y + radius * np.sin(angle)])
                    new_element = {
                        'type': 'pattern',
                        'x': x_points, 'y': y_points,
                        'color': st.session_state.selected_color,
                        'width': 3,
                        'size': 6
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Flower pattern added!")
                    st.rerun()
            with col2:
                if st.button("Geometric", key="canvas_geometric_pattern"):
                    # Create geometric pattern
                    center_x, center_y = 400, 300
                    sides = 6
                    radius = 100
                    x_points, y_points = [], []
                    for i in range(sides + 1):
                        angle = 2 * np.pi * i / sides
                        x_points.append(center_x + radius * np.cos(angle))
                        y_points.append(center_y + radius * np.sin(angle))
                    new_element = {
                        'type': 'pattern',
                        'x': x_points, 'y': y_points,
                        'color': st.session_state.selected_color,
                        'width': 3,
                        'size': 6
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Geometric pattern added!")
                    st.rerun()
            with col3:
                if st.button("Mandala", key="canvas_mandala_pattern"):
                    # Create mandala pattern
                    center_x, center_y = 400, 300
                    x_points, y_points = [], []
                    for r in [50, 100, 150]:
                        for i in range(12):
                            angle = 2 * np.pi * i / 12
                            x_points.append(center_x + r * np.cos(angle))
                            y_points.append(center_y + r * np.sin(angle))
                    new_element = {
                        'type': 'pattern',
                        'x': x_points, 'y': y_points,
                        'color': st.session_state.selected_color,
                        'width': 2,
                        'size': 4
                    }
                    st.session_state.drawing_elements.append(new_element)
                    st.success("Mandala pattern added!")
                    st.rerun()
        
        # Action buttons
        st.subheader("🛠️ Canvas Controls")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Clear Drawing", key="canvas_clear_drawing"):
                st.session_state.drawing_elements = []
                st.success("Drawing elements cleared!")
                st.rerun()
        with col2:
            if st.button("Clear Components", key="canvas_clear_components"):
                st.session_state.edge_components = []
                st.session_state.selected_component_ids = []
                st.success("Edge components cleared!")
                st.rerun()
        with col3:
            if st.button("Clear All", key="canvas_clear_all"):
                st.session_state.drawing_elements = []
                st.session_state.edge_components = []
                st.session_state.selected_component_ids = []
                st.success("Canvas completely cleared!")
                st.rerun()
        with col4:
            if st.button("Undo Last Drawing", key="canvas_undo_last"):
                if st.session_state.drawing_elements:
                    st.session_state.drawing_elements.pop()
                    st.success("Last drawing element removed!")
                    st.rerun()
                else:
                    st.info("No drawing elements to undo")
    
    with tab2:
        st.subheader("Kolam Templates")
        
        # Template gallery
        template_options = [
            "Basic Dot Grid",
            "Flower Pattern",
            "Geometric Design",
            "Traditional Rangoli",
            "Spiral Pattern"
        ]
        
        selected_template = st.selectbox("Choose a template to start with:", template_options, key="templates_selectbox")
        
        if st.button("Load Template", key="templates_load_btn"):
            st.success(f"Loading {selected_template} template...")
            # Template loading logic would go here
    
    with tab3:
        st.subheader("How to Draw Kolam Patterns")
        
        st.markdown("""
        ### Basic Principles:
        1. **Start with dots**: Traditional kolams begin with a grid of dots
        2. **Connect the dots**: Draw curves and lines connecting the dots
        3. **Maintain symmetry**: Most kolams have rotational or reflective symmetry
        4. **No loose ends**: Traditional kolams form continuous loops
        5. **Use repetition**: Repeat patterns to create larger designs
        
        ### Using Edge Components:
        1. **Upload an image** and use "Parse & Analyze Image"
        2. **Adjust edge detection** parameters for better results
        3. **Convert to components** using contour tracing or line segments
        4. **Switch to Edit Components mode** to modify the detected edges
        5. **Select components** to change colors, widths, or delete them
        6. **Use advanced operations** to smooth, duplicate, or convert components
        
        ### Drawing Tips:
        - Use smooth, flowing curves
        - Maintain consistent spacing
        - Start from the center and work outward
        - Practice basic motifs before complex designs
        - Use edge detection to trace existing patterns and modify them
        """)

def render_advanced_editor():
    """Render the advanced editor UI from this module inside a parent Streamlit app."""
    create_drawing_interface()
    col1, col2 = st.columns([2, 1])
    with col1:
        drawing_canvas_section()
    with col2:
        image_upload_section()
        pattern_analysis_section()
    export_section()
    # Footer to match standalone
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🎨 Kolam Editor - Preserving traditional art through digital innovation</p>
        <p>✨ Now with editable edge components for enhanced pattern editing!</p>
        <p>Created with ❤️ using Streamlit</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

def main():
    """Standalone runner for this module."""
    # Only when running this file directly should we set page config
    st.set_page_config(
        page_title="Kolam Editor - Draw Online",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    render_advanced_editor()

if __name__ == "__main__":
    # Run as standalone page
    main()