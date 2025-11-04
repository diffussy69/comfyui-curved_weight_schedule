import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import io
import json
from PIL import Image

class InteractiveCurveDesigner:
    """
    Interactive curve designer with visual canvas interface.
    Draw curves by clicking and dragging points on a canvas!
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "points_data": ("STRING", {
                    "default": '[{"x":0,"y":1},{"x":0.25,"y":0.75},{"x":0.5,"y":0.5},{"x":0.75,"y":0.25},{"x":1,"y":0}]',
                    "multiline": True,
                    "tooltip": "JSON data from canvas (auto-updated)"
                }),
                "interpolation_method": (["linear", "cubic_spline", "polynomial", "hermite"], {
                    "default": "cubic_spline",
                    "tooltip": "Curve interpolation method"
                }),
                "resolution": ("INT", {
                    "default": 100,
                    "min": 10,
                    "max": 500,
                    "step": 10,
                    "tooltip": "Curve resolution"
                }),
                "normalize": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Normalize output to 0-1 range"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("formula", "preview", "description")
    FUNCTION = "generate_curve"
    CATEGORY = "conditioning/controlnet"
    
    def generate_curve(self, points_data, interpolation_method, resolution, normalize):
        """Generate curve from canvas points"""
        
        try:
            # Parse points from JSON
            points = json.loads(points_data)
            
            if not points or len(points) < 2:
                return ("t", self.create_error_image("Need at least 2 points"), "Error: Not enough points")
            
            # Extract x and y coordinates
            points_x = np.array([p["x"] for p in points])
            points_y = np.array([p["y"] for p in points])
            
            # DEBUG: Print received points
            print(f"[Interactive Curve Designer] Received points:")
            for i, (x, y) in enumerate(zip(points_x, points_y)):
                print(f"  P{i+1}: x={x:.3f}, y={y:.3f}")
            
            # Sort by x
            sorted_idx = np.argsort(points_x)
            points_x = points_x[sorted_idx]
            points_y = points_y[sorted_idx]
            
            # Generate curve
            t = np.linspace(0, 1, resolution)
            curve, formula = self.interpolate_curve(t, points_x, points_y, interpolation_method)
            
            # DEBUG: Check curve direction
            print(f"[DEBUG] First curve value: {curve[0]:.3f}, Last curve value: {curve[-1]:.3f}")
            print(f"[DEBUG] First point Y: {points_y[0]:.3f}, Last point Y: {points_y[-1]:.3f}")
            
            # Store original points for preview
            original_points_y = points_y.copy()
            
            # Normalize if requested
            if normalize:
                curve_min = np.min(curve)
                curve_max = np.max(curve)
                if curve_max > curve_min:
                    curve = (curve - curve_min) / (curve_max - curve_min)
                    # Also normalize the display points for preview
                    display_points_y = (original_points_y - curve_min) / (curve_max - curve_min)
                else:
                    display_points_y = original_points_y
            else:
                display_points_y = original_points_y
            
            print(f"[DEBUG] After normalize - First curve: {curve[0]:.3f}, Last curve: {curve[-1]:.3f}")
            print(f"[DEBUG] Display points: {display_points_y}")
            
            # Clamp
            curve = np.clip(curve, 0, 2.0)
            
            # Generate preview with normalized display points
            preview = self.generate_preview(t, curve, points_x, display_points_y, interpolation_method)
            
            # Generate description
            description = self.generate_description(points, formula, interpolation_method, normalize)
            
            return (formula, preview, description)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[Interactive Curve Designer] {error_msg}")
            return ("t", self.create_error_image(error_msg), error_msg)
    
    def interpolate_curve(self, t, points_x, points_y, method):
        """Interpolate curve through points"""
        
        if method == "linear":
            curve = np.interp(t, points_x, points_y)
            x_str = "[" + ",".join([f"{x:.3f}" for x in points_x]) + "]"
            y_str = "[" + ",".join([f"{y:.3f}" for y in points_y]) + "]"
            formula = f"np.interp(t, {x_str}, {y_str})"
            
        elif method == "cubic_spline":
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(points_x, points_y, bc_type='natural')
            curve = cs(t)
            formula = f"# Cubic spline through {len(points_x)} points\nnp.interp(t, {list(points_x)}, {list(points_y)})"
            
        elif method == "polynomial":
            degree = min(len(points_x) - 1, 6)
            coeffs = np.polyfit(points_x, points_y, degree)
            curve = np.polyval(coeffs, t)
            formula = self.format_polynomial(coeffs)
            
        elif method == "hermite":
            # Hermite interpolation (smooth with automatic tangents)
            curve = self.hermite_interpolate(t, points_x, points_y)
            formula = f"# Hermite interpolation\nnp.interp(t, {list(points_x)}, {list(points_y)})"
            
        else:
            curve = np.interp(t, points_x, points_y)
            formula = f"np.interp(t, {list(points_x)}, {list(points_y)})"
        
        return curve, formula
    
    def hermite_interpolate(self, t, points_x, points_y):
        """Hermite spline interpolation with automatic tangents"""
        # Calculate tangents at each point
        tangents = np.zeros_like(points_y)
        
        for i in range(len(points_y)):
            if i == 0:
                tangents[i] = (points_y[1] - points_y[0]) / (points_x[1] - points_x[0])
            elif i == len(points_y) - 1:
                tangents[i] = (points_y[i] - points_y[i-1]) / (points_x[i] - points_x[i-1])
            else:
                tangents[i] = ((points_y[i+1] - points_y[i-1]) / 
                              (points_x[i+1] - points_x[i-1]))
        
        # Interpolate
        result = np.zeros_like(t)
        for i in range(len(t)):
            t_val = t[i]
            
            # Find segment
            segment = 0
            for j in range(len(points_x) - 1):
                if points_x[j] <= t_val <= points_x[j + 1]:
                    segment = j
                    break
            
            # Hermite basis functions
            x0, x1 = points_x[segment], points_x[segment + 1]
            y0, y1 = points_y[segment], points_y[segment + 1]
            t0, t1 = tangents[segment], tangents[segment + 1]
            
            s = (t_val - x0) / (x1 - x0) if x1 > x0 else 0
            
            h00 = 2*s**3 - 3*s**2 + 1
            h10 = s**3 - 2*s**2 + s
            h01 = -2*s**3 + 3*s**2
            h11 = s**3 - s**2
            
            result[i] = h00*y0 + h10*(x1-x0)*t0 + h01*y1 + h11*(x1-x0)*t1
        
        return result
    
    def format_polynomial(self, coeffs):
        """Format polynomial formula"""
        terms = []
        degree = len(coeffs) - 1
        
        for i, coeff in enumerate(coeffs):
            power = degree - i
            if abs(coeff) < 0.0001:
                continue
            
            if power == 0:
                terms.append(f"{coeff:.4f}")
            elif power == 1:
                terms.append(f"{coeff:.4f}*t")
            else:
                terms.append(f"{coeff:.4f}*t**{power}")
        
        if not terms:
            return "0"
        
        formula = " + ".join(terms)
        return formula.replace("+ -", "- ")
    
    def generate_preview(self, t, curve, points_x, points_y, method):
        """Generate preview graph"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            
            # Plot curve
            ax.plot(t * 100, curve, 'b-', linewidth=3, label='Interpolated Curve', alpha=0.9)
            
            # Plot control points
            ax.scatter(points_x * 100, points_y, c='red', s=150, zorder=10, 
                      label='Control Points', edgecolors='darkred', linewidth=2.5)
            
            # Connect points with thin lines
            ax.plot(points_x * 100, points_y, 'r--', linewidth=1, alpha=0.3)
            
            # Point labels
            for i, (x, y) in enumerate(zip(points_x, points_y), 1):
                ax.annotate(f'P{i}\n({x:.2f},{y:.2f})', 
                           (x * 100, y), 
                           xytext=(0, 15), 
                           textcoords='offset points',
                           ha='center',
                           fontsize=9,
                           bbox=dict(boxstyle='round,pad=0.5', 
                                   facecolor='yellow', 
                                   alpha=0.8,
                                   edgecolor='orange'))
            
            # Styling
            ax.set_xlabel('Progress (%)', fontsize=13, fontweight='bold')
            ax.set_ylabel('Strength', fontsize=13, fontweight='bold')
            ax.set_title(f'Interactive Curve Designer - {method.replace("_", " ").title()}\n'
                        f'{len(points_x)} Control Points',
                        fontsize=14, fontweight='bold', pad=15)
            
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            ax.legend(loc='best', fontsize=11, framealpha=0.9)
            
            ax.set_xlim(-5, 105)
            y_min = min(0, np.min(curve), np.min(points_y)) - 0.15
            y_max = max(1, np.max(curve), np.max(points_y)) + 0.15
            ax.set_ylim(y_min, y_max)
            
            # Background
            ax.set_facecolor('#f8f8f8')
            fig.patch.set_facecolor('white')
            
            plt.tight_layout()
            
            # Convert to tensor
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='white', dpi=100)
            buf.seek(0)
            img = Image.open(buf)
            plt.close(fig)
            
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            
            return img_tensor
            
        except Exception as e:
            print(f"[Interactive Curve Designer] Preview error: {e}")
            return self.create_error_image(str(e))
        finally:
            plt.close('all')
    
    def create_error_image(self, message):
        """Create error image"""
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        ax.text(0.5, 0.5, f'Error:\n{message}', 
               ha='center', va='center',
               fontsize=14, color='red',
               bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.8))
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        img_array = np.array(img).astype(np.float32) / 255.0
        return torch.from_numpy(img_array)[None,]
    
    def generate_description(self, points, formula, method, normalized):
        """Generate description"""
        
        description = f"""
========================================
INTERACTIVE CURVE DESIGNER
========================================

Method: {method.replace('_', ' ').title()}
Points: {len(points)}
Normalized: {'Yes' if normalized else 'No'}

Control Points:
"""
        for i, p in enumerate(points, 1):
            description += f"  P{i}: ({p['x']:.3f}, {p['y']:.3f})\n"
        
        description += f"""
Generated Formula:
{formula}

Canvas Controls:
• Click: Add new point
• Drag: Move existing point
• Double-click: Delete point
• Buttons: Quick transformations

How to Use Formula:
1. Copy the formula above
2. In Advanced Curved ControlNet Scheduler:
   - Set curve_type to "custom_formula"
   - Paste into custom_formula field
3. Generate!

Tips:
• Draw the curve shape you want visually
• Formula is auto-generated from your drawing
• Use symmetry for balanced curves
• Invert Y to flip the curve

========================================
"""
        
        return description


# Node registration
NODE_CLASS_MAPPINGS = {
    "InteractiveCurveDesigner": InteractiveCurveDesigner
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InteractiveCurveDesigner": "Interactive Curve Designer 🎨"
}