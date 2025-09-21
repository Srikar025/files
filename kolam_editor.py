import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple, Dict
import json

class KolamEditor:
    """Interactive Kolam editor with canvas functionality"""
    
    def __init__(self):
        self.grid_size = 7
        self.dots = []
        self.connections = []
        self.current_dots = set()
        
    def create_editor_interface(self):
        """Create the main editor interface"""
        st.subheader("🎨 Interactive Kolam Editor")
        
        # Check if pattern was passed from AI generator
        if 'editor_pattern' in st.session_state:
            pattern_data = st.session_state['editor_pattern']
            st.success("🎉 AI-generated pattern loaded! You can now edit it.")
            
            # Load the pattern
            self.dots = pattern_data.get('dots', [])
            self.connections = pattern_data.get('connections', [])
            
            # Clear the session state
            del st.session_state['editor_pattern']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Grid size selector
            self.grid_size = st.selectbox(
                "Select Grid Size",
                options=[3, 5, 7, 9, 11],
                index=2,
                help="Choose the size of the dot grid"
            )
            
            # Create the interactive canvas
            self._create_interactive_canvas()
            
        with col2:
            st.subheader("🎯 Tools")
            
            # Drawing tools
            tool = st.radio(
                "Drawing Tool",
                ["Dot Mode", "Line Mode", "Curve Mode", "Erase Mode"],
                help="Select the drawing tool to use"
            )
            
            # Clear canvas
            if st.button("🗑️ Clear Canvas", type="secondary"):
                self.dots = []
                self.connections = []
                self.current_dots = set()
                st.rerun()
            
            # Save design
            if st.button("💾 Save Design"):
                self._save_design()
            
            # Load design
            uploaded_file = st.file_uploader(
                "📁 Load Design",
                type=['json'],
                help="Load a previously saved Kolam design"
            )
            if uploaded_file:
                self._load_design(uploaded_file)
            
            # Export options
            st.subheader("📤 Export")
            export_format = st.selectbox(
                "Export Format",
                ["PNG", "SVG", "JSON"]
            )
            
            if st.button("📥 Export Design"):
                self._export_design(export_format)
    
    def _create_interactive_canvas(self):
        """Create an interactive canvas using Plotly"""
        # Generate grid points
        grid_points = self._generate_grid_points()
        
        # Create the plot
        fig = go.Figure()
        
        # Add grid dots
        for i, (x, y) in enumerate(grid_points):
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(
                    size=12,
                    color='black',
                    symbol='circle'
                ),
                name=f'Dot {i+1}',
                hovertemplate=f'Dot {i+1}<br>Position: ({x}, {y})<extra></extra>'
            ))
        
        # Add connections if any
        for connection in self.connections:
            x_coords = [connection['start'][0], connection['end'][0]]
            y_coords = [connection['start'][1], connection['end'][1]]
            
            fig.add_trace(go.Scatter(
                x=x_coords, y=y_coords,
                mode='lines',
                line=dict(color='red', width=3),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Configure layout
        fig.update_layout(
            title="Kolam Editor - Click on dots to connect them",
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                showgrid=True,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showticklabels=False
            ),
            plot_bgcolor='white',
            width=600,
            height=600,
            showlegend=False
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Add click functionality
        st.write("💡 **Instructions:**")
        st.write("• Use the drawing tools on the right to create your Kolam")
        st.write("• In Dot Mode: Click on grid points to place dots")
        st.write("• In Line Mode: Click two dots to connect them with a line")
        st.write("• In Curve Mode: Click multiple dots to create curved connections")
        st.write("• In Erase Mode: Click on elements to remove them")
        
        # Simple dot placement interface
        self._create_simple_editor()
    
    def _generate_grid_points(self) -> List[Tuple[float, float]]:
        """Generate grid points for the canvas"""
        points = []
        spacing = 1.0
        start = -(self.grid_size - 1) * spacing / 2
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = start + j * spacing
                y = start + i * spacing
                points.append((x, y))
        
        return points
    
    def _create_simple_editor(self):
        """Create a simplified editor interface"""
        st.subheader("🎮 Simple Editor")
        
        # Dot placement
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Place Dots:**")
            if st.button("Add Random Dot"):
                self._add_random_dot()
        
        with col2:
            st.write("**Connect Dots:**")
            if st.button("Connect Random Dots"):
                self._connect_random_dots()
        
        with col3:
            st.write("**Patterns:**")
            if st.button("Create Symmetric Pattern"):
                self._create_symmetric_pattern()
        
        # Display current design
        if self.dots or self.connections:
            self._display_current_design()
    
    def _add_random_dot(self):
        """Add a random dot to the design"""
        if len(self.dots) < self.grid_size * self.grid_size:
            grid_points = self._generate_grid_points()
            available_points = [p for p in grid_points if p not in self.dots]
            if available_points:
                new_dot = available_points[0]  # Could be random
                self.dots.append(new_dot)
                st.success(f"Added dot at {new_dot}")
    
    def _connect_random_dots(self):
        """Connect two random dots"""
        if len(self.dots) >= 2:
            import random
            start_dot = random.choice(self.dots)
            end_dot = random.choice([d for d in self.dots if d != start_dot])
            
            connection = {
                'start': start_dot,
                'end': end_dot,
                'type': 'line'
            }
            self.connections.append(connection)
            st.success(f"Connected {start_dot} to {end_dot}")
    
    def _create_symmetric_pattern(self):
        """Create a symmetric pattern"""
        if self.grid_size >= 5:
            center = (0, 0)  # Center of grid
            self.dots.append(center)
            
            # Create symmetric dots
            for i in range(1, self.grid_size // 2):
                for angle in [0, 90, 180, 270]:  # 4-fold symmetry
                    import math
                    x = i * math.cos(math.radians(angle))
                    y = i * math.sin(math.radians(angle))
                    self.dots.append((x, y))
            
            st.success("Created symmetric pattern")
    
    def _display_current_design(self):
        """Display the current design using matplotlib"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Draw dots
        if self.dots:
            dot_x = [dot[0] for dot in self.dots]
            dot_y = [dot[1] for dot in self.dots]
            ax.scatter(dot_x, dot_y, c='black', s=100, marker='o', zorder=3)
        
        # Draw connections
        for connection in self.connections:
            start = connection['start']
            end = connection['end']
            ax.plot([start[0], end[0]], [start[1], end[1]], 'r-', linewidth=2, zorder=2)
        
        # Configure plot
        ax.set_xlim(-self.grid_size//2 - 1, self.grid_size//2 + 1)
        ax.set_ylim(-self.grid_size//2 - 1, self.grid_size//2 + 1)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title("Your Kolam Design", fontsize=14, fontweight='bold')
        
        st.pyplot(fig)
    
    def _save_design(self):
        """Save the current design"""
        design_data = {
            'grid_size': self.grid_size,
            'dots': self.dots,
            'connections': self.connections
        }
        
        # Create download link
        json_str = json.dumps(design_data, indent=2)
        st.download_button(
            label="💾 Download Design",
            data=json_str,
            file_name="kolam_design.json",
            mime="application/json"
        )
        st.success("Design saved!")
    
    def _load_design(self, uploaded_file):
        """Load a design from uploaded file"""
        try:
            design_data = json.load(uploaded_file)
            self.grid_size = design_data.get('grid_size', 7)
            self.dots = design_data.get('dots', [])
            self.connections = design_data.get('connections', [])
            st.success("Design loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading design: {str(e)}")
    
    def _export_design(self, format_type: str):
        """Export the design in specified format"""
        if format_type == "JSON":
            self._save_design()
        elif format_type == "PNG":
            # Create matplotlib figure and save
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Draw design
            if self.dots:
                dot_x = [dot[0] for dot in self.dots]
                dot_y = [dot[1] for dot in self.dots]
                ax.scatter(dot_x, dot_y, c='black', s=100, marker='o')
            
            for connection in self.connections:
                start = connection['start']
                end = connection['end']
                ax.plot([start[0], end[0]], [start[1], end[1]], 'r-', linewidth=2)
            
            ax.set_xlim(-self.grid_size//2 - 1, self.grid_size//2 + 1)
            ax.set_ylim(-self.grid_size//2 - 1, self.grid_size//2 + 1)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title("Kolam Design", fontsize=16)
            
            # Save to buffer
            import io
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download PNG",
                data=buffer.getvalue(),
                file_name="kolam_design.png",
                mime="image/png"
            )
            
            plt.close(fig)
    
    def extract_design_principles(self) -> List[str]:
        """Extract design principles from the current design"""
        principles = []
        
        # Check for symmetry
        if len(self.dots) > 1:
            # Simple symmetry check
            center_x = sum(dot[0] for dot in self.dots) / len(self.dots)
            center_y = sum(dot[1] for dot in self.dots) / len(self.dots)
            
            symmetric_dots = 0
            for dot in self.dots:
                # Check if there's a symmetric counterpart
                symmetric_x = 2 * center_x - dot[0]
                symmetric_y = 2 * center_y - dot[1]
                
                for other_dot in self.dots:
                    if abs(other_dot[0] - symmetric_x) < 0.1 and abs(other_dot[1] - symmetric_y) < 0.1:
                        symmetric_dots += 1
                        break
            
            if symmetric_dots > len(self.dots) * 0.7:
                principles.append("High Symmetry")
        
        # Check for grid structure
        if len(self.dots) >= self.grid_size * 0.5:
            principles.append("Grid-Based Structure")
        
        # Check for line patterns
        if len(self.connections) > 3:
            principles.append("Complex Line Patterns")
        
        # Check for geometric shapes
        if len(self.dots) >= 4 and len(self.connections) >= 4:
            principles.append("Geometric Design")
        
        return principles
