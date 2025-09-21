import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from typing import List, Tuple, Dict
import random
import math

class KolamGenerator:
    """Generates traditional Kolam patterns based on mathematical rules and symmetry"""
    
    def __init__(self):
        self.patterns = {
            'basic_symmetric': self._generate_basic_symmetric,
            'rotational': self._generate_rotational,
            'spiral': self._generate_spiral,
            'floral': self._generate_floral,
            'geometric': self._generate_geometric
        }
    
    def generate_pattern(self, grid_size: int, pattern_type: str = 'basic_symmetric') -> np.ndarray:
        """Generate a Kolam pattern based on grid size and pattern type"""
        if pattern_type in self.patterns:
            return self.patterns[pattern_type](grid_size)
        else:
            return self._generate_basic_symmetric(grid_size)
    
    def _generate_basic_symmetric(self, grid_size: int) -> np.ndarray:
        """Generate a basic symmetric pattern"""
        grid = np.zeros((grid_size, grid_size))
        
        # Create dots (1) and empty spaces (0)
        for i in range(grid_size):
            for j in range(grid_size):
                # Create a symmetric pattern
                if (i + j) % 2 == 0:
                    grid[i][j] = 1
        
        return grid
    
    def _generate_rotational(self, grid_size: int) -> np.ndarray:
        """Generate a rotational symmetric pattern"""
        grid = np.zeros((grid_size, grid_size))
        center = grid_size // 2
        
        # Create rotational symmetry
        for i in range(grid_size):
            for j in range(grid_size):
                # Distance from center
                dx = i - center
                dy = j - center
                distance = math.sqrt(dx*dx + dy*dy)
                angle = math.atan2(dy, dx)
                
                # Create rotational pattern
                if int(distance * 2) % 2 == 0 and int(angle * 4 / math.pi) % 2 == 0:
                    grid[i][j] = 1
        
        return grid
    
    def _generate_spiral(self, grid_size: int) -> np.ndarray:
        """Generate a spiral pattern"""
        grid = np.zeros((grid_size, grid_size))
        center = grid_size // 2
        
        # Create spiral pattern
        for i in range(grid_size):
            for j in range(grid_size):
                dx = i - center
                dy = j - center
                angle = math.atan2(dy, dx)
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Spiral condition
                if abs(distance - angle * 0.5) < 1:
                    grid[i][j] = 1
        
        return grid
    
    def _generate_floral(self, grid_size: int) -> np.ndarray:
        """Generate a floral pattern"""
        grid = np.zeros((grid_size, grid_size))
        center = grid_size // 2
        
        # Create floral pattern with petals
        num_petals = 8
        for petal in range(num_petals):
            angle = 2 * math.pi * petal / num_petals
            for r in range(1, center):
                x = int(center + r * math.cos(angle))
                y = int(center + r * math.sin(angle))
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    grid[x][y] = 1
        
        # Center dot
        if center < grid_size:
            grid[center][center] = 1
        
        return grid
    
    def _generate_geometric(self, grid_size: int) -> np.ndarray:
        """Generate a geometric pattern"""
        grid = np.zeros((grid_size, grid_size))
        
        # Create geometric shapes
        for i in range(grid_size):
            for j in range(grid_size):
                # Create diamond/square pattern
                if abs(i - grid_size//2) + abs(j - grid_size//2) <= grid_size//2:
                    if (i + j) % 3 == 0:
                        grid[i][j] = 1
        
        return grid
    
    def draw_kolam(self, grid: np.ndarray, title: str = "Kolam Pattern") -> plt.Figure:
        """Draw the Kolam pattern"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Create dots
        dot_positions = np.where(grid == 1)
        ax.scatter(dot_positions[1], dot_positions[0], c='black', s=100, marker='o')
        
        # Create connections (simplified)
        for i in range(len(dot_positions[0])):
            for j in range(i+1, len(dot_positions[0])):
                x1, y1 = dot_positions[1][i], dot_positions[0][i]
                x2, y2 = dot_positions[1][j], dot_positions[0][j]
                
                # Connect nearby dots
                distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
                if distance <= 2:  # Connect dots that are close
                    ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.7, linewidth=2)
        
        ax.set_xlim(-0.5, grid.shape[1] - 0.5)
        ax.set_ylim(-0.5, grid.shape[0] - 0.5)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Invert y-axis to match typical grid layout
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        return fig

def get_available_patterns() -> List[str]:
    """Get list of available pattern types"""
    generator = KolamGenerator()
    return list(generator.patterns.keys())
