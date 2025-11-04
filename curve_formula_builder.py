import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import io
from PIL import Image

class CurveFormulaBuilder:
    """
    Beginner-friendly curve formula builder.
    No math knowledge required - just select patterns and adjust sliders!
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pattern": ([
                    "Straight Line",
                    "Ease In (Slow Start)", 
                    "Ease Out (Slow End)",
                    "S-Curve (Smooth)",
                    "Wave (Repeating)",
                    "Peak (Up Then Down)",
                    "Valley (Down Then Up)",
                    "Exponential Growth",
                    "Exponential Decay"
                ], {
                    "default": "S-Curve (Smooth)",
                    "tooltip": "Choose the basic shape of your curve"
                }),
                "strength": ("FLOAT", {
                    "default": 50.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 1.0,
                    "tooltip": "How dramatic the effect (0=gentle, 100=extreme)"
                }),
                "speed": ("FLOAT", {
                    "default": 50.0,
                    "min": 10.0,
                    "max": 100.0,
                    "step": 1.0,
                    "tooltip": "How fast the change happens"
                }),
                "num_points": ("INT", {
                    "default": 100,
                    "min": 10,
                    "max": 500,
                    "step": 10,
                    "tooltip": "Resolution of the curve preview"
                }),
            },
            "optional": {
                "flip_vertical": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Flip the curve upside down"
                }),
                "flip_horizontal": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reverse the curve direction"
                }),
                "repeat_times": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Repeat the pattern multiple times"
                }),
                "show_formula": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Show the generated math formula"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("formula", "preview_graph", "description")
    FUNCTION = "build_formula"
    CATEGORY = "conditioning/controlnet"
    
    def build_formula(self, pattern, strength, speed, num_points,
                     flip_vertical=False, flip_horizontal=False, 
                     repeat_times=1, show_formula=False):
        """Build a formula from simple visual parameters"""
        
        # Generate t values
        t = np.linspace(0, 1, num_points)
        
        # Apply horizontal flip (reverse direction)
        if flip_horizontal:
            t = 1 - t
        
        # Apply repeat
        if repeat_times > 1:
            t = (t * repeat_times) % 1.0
        
        # Normalize strength and speed to usable ranges
        strength_factor = strength / 50.0  # 1.0 at 50%
        speed_factor = speed / 50.0  # 1.0 at 50%
        
        # Generate curve based on pattern
        formula_str, curve, description = self.generate_pattern(
            pattern, t, strength_factor, speed_factor
        )
        
        # Apply vertical flip
        if flip_vertical:
            curve = 1 - curve
            formula_str = f"1 - ({formula_str})"
        
        # Ensure curve is in 0-1 range
        curve = np.clip(curve, 0, 1)
        
        # Generate preview graph
        preview_image = self.generate_preview(t, curve, pattern, strength, speed)
        
        # Build description text
        full_description = self.build_description(
            pattern, strength, speed, flip_vertical, flip_horizontal, 
            repeat_times, show_formula, formula_str, description
        )
        
        return (formula_str, preview_image, full_description)
    
    def generate_pattern(self, pattern, t, strength_factor, speed_factor):
        """Generate curve values for each pattern type"""
        
        if pattern == "Straight Line":
            curve = t
            formula = "t"
            description = "Linear progression from start to end"
            
        elif pattern == "Ease In (Slow Start)":
            # Slow start, fast end
            power = 1.0 + strength_factor
            curve = t ** power
            formula = f"t**{power:.2f}"
            description = "Starts gentle, accelerates toward the end"
            
        elif pattern == "Ease Out (Slow End)":
            # Fast start, slow end
            power = 1.0 + strength_factor
            curve = 1 - (1 - t) ** power
            formula = f"1-(1-t)**{power:.2f}"
            description = "Starts strong, slows down toward the end"
            
        elif pattern == "S-Curve (Smooth)":
            # Smooth S-curve (ease in-out)
            curve = 3 * t**2 - 2 * t**3
            # Apply strength by adjusting the curve
            if strength_factor != 1.0:
                curve = curve ** (1.0 / strength_factor)
                curve = np.clip(curve, 0, 1)
            formula = "3*t**2 - 2*t**3"
            description = "Smooth transition - gentle at both ends, faster in middle"
            
        elif pattern == "Wave (Repeating)":
            # Sine wave
            cycles = speed_factor * 2  # More speed = more cycles
            amplitude = strength_factor * 0.5
            curve = 0.5 + amplitude * np.sin(t * np.pi * 2 * cycles)
            formula = f"0.5 + {amplitude:.2f}*sin(t*6.28*{cycles:.1f})"
            description = f"Oscillating wave with {cycles:.1f} cycles"
            
        elif pattern == "Peak (Up Then Down)":
            # Bell curve
            center = 0.5
            width = 0.3 / speed_factor
            curve = strength_factor * np.exp(-((t - center)**2) / (2 * width**2))
            formula = f"{strength_factor:.2f}*exp(-((t-0.5)**2)/(2*{width:.3f}**2))"
            description = "Peaks in the middle, low at edges"
            
        elif pattern == "Valley (Down Then Up)":
            # Inverted bell curve
            center = 0.5
            width = 0.3 / speed_factor
            curve = 1 - strength_factor * np.exp(-((t - center)**2) / (2 * width**2))
            formula = f"1 - {strength_factor:.2f}*exp(-((t-0.5)**2)/(2*{width:.3f}**2))"
            description = "Dips in the middle, high at edges"
            
        elif pattern == "Exponential Growth":
            # Exponential increase
            rate = speed_factor * 5
            curve = (np.exp(rate * t) - 1) / (np.exp(rate) - 1)
            curve = curve * strength_factor
            curve = np.clip(curve, 0, 1)
            formula = f"(exp({rate:.1f}*t)-1)/(exp({rate:.1f})-1)"
            description = "Gradual at first, then rapid growth"
            
        elif pattern == "Exponential Decay":
            # Exponential decrease
            rate = speed_factor * 5
            curve = 1 - (np.exp(rate * t) - 1) / (np.exp(rate) - 1)
            curve = curve * strength_factor
            curve = np.clip(curve, 0, 1)
            formula = f"1 - (exp({rate:.1f}*t)-1)/(exp({rate:.1f})-1)"
            description = "Rapid drop at first, then levels off"
            
        else:
            # Fallback to linear
            curve = t
            formula = "t"
            description = "Linear"
        
        return formula, curve, description
    
    def generate_preview(self, t, curve, pattern, strength, speed):
        """Generate a preview graph of the curve"""
        try:
            fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
            
            # Plot the curve
            ax.plot(t * 100, curve, 'b-', linewidth=2.5, label='Your Curve')
            ax.scatter(t[::len(t)//10] * 100, curve[::len(t)//10], 
                      c='red', s=40, zorder=5, alpha=0.6)
            
            # Styling
            ax.set_xlabel('Progress (%)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Strength', fontsize=11, fontweight='bold')
            ax.set_title(f'{pattern}\nStrength: {strength:.0f}% | Speed: {speed:.0f}%', 
                        fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlim(-5, 105)
            ax.set_ylim(-0.1, 1.1)
            
            # Add reference lines
            ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            ax.axvline(x=50, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            
            plt.tight_layout()
            
            # Convert to image tensor
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            plt.close(fig)
            
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            
            return img_tensor
            
        except Exception as e:
            print(f"[Curve Formula Builder] Graph error: {e}")
            # Return dummy image on error
            dummy = np.zeros((100, 100, 3), dtype=np.float32)
            return torch.from_numpy(dummy)[None,]
        finally:
            plt.close('all')
    
    def build_description(self, pattern, strength, speed, flip_vertical, 
                         flip_horizontal, repeat_times, show_formula, 
                         formula_str, pattern_description):
        """Build a human-readable description of the curve"""
        
        description = f"""
============================
CURVE FORMULA BUILDER
============================
Pattern: {pattern}
{pattern_description}

Settings:
• Strength: {strength:.0f}%
• Speed: {speed:.0f}%
• Flip Vertical: {'Yes' if flip_vertical else 'No'}
• Flip Horizontal: {'Yes' if flip_horizontal else 'No'}
• Repeat: {repeat_times}x

"""
        
        if show_formula:
            description += f"""Mathematical Formula:
{formula_str}

"""
        
        description += """Usage:
1. Copy the formula output
2. Paste into Advanced Curved ControlNet Scheduler
3. Set curve_type to "custom_formula"
4. Paste formula into custom_formula field

Or just use the visual preview to understand
the curve shape before applying!
============================
"""
        
        return description


# Node registration
NODE_CLASS_MAPPINGS = {
    "CurveFormulaBuilder": CurveFormulaBuilder
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CurveFormulaBuilder": "Curve Formula Builder"
}