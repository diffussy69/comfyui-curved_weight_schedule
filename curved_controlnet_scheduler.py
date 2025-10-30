import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
from PIL import Image
import torch

# Import Advanced ControlNet classes
try:
    from .control import ControlWeights
    from .nodes import TimestepKeyframeNode
    from .utils import TimestepKeyframeGroup, TimestepKeyframe
    ACN_AVAILABLE = True
except:
    try:
        import sys
        import os
        # Try to import from the Advanced ControlNet custom node
        comfy_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        acn_path = os.path.join(comfy_path, "custom_nodes", "ComfyUI-Advanced-ControlNet")
        if os.path.exists(acn_path):
            sys.path.insert(0, acn_path)
            from adv_control.control import ControlWeights
            from adv_control.nodes import TimestepKeyframeNode
            from adv_control.utils import TimestepKeyframeGroup, TimestepKeyframe
            ACN_AVAILABLE = True
        else:
            ACN_AVAILABLE = False
    except Exception as e:
        print(f"Failed to import Advanced ControlNet: {e}")
        ACN_AVAILABLE = False

class CurvedControlNetScheduler:
    """
    Generates curved timestep keyframes for Advanced ControlNet.
    Controls ControlNet strength across generation steps (timesteps).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "num_keyframes": ("INT", {
                    "default": 10,
                    "min": 2,
                    "max": 100,
                    "step": 1,
                    "tooltip": "Number of keyframes to generate across the timestep range"
                }),
                "start_percent": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "Starting point in generation (0.0 = beginning)"
                }),
                "end_percent": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "Ending point in generation (1.0 = end)"
                }),
                "start_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "ControlNet strength at start_percent"
                }),
                "end_strength": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "ControlNet strength at end_percent"
                }),
                "curve_type": (["linear", "ease_in", "ease_out", "ease_in_out", 
                               "sine_wave", "bell_curve", "reverse_bell", 
                               "exponential", "bounce", "custom_bezier"],),
                "curve_param": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve steepness: higher = more extreme curve"
                }),
            },
            "optional": {
                "prev_timestep_kf": ("TIMESTEP_KEYFRAME",),
                "invert_curve": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert the curve shape"
                }),
                "print_keyframes": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print generated keyframes for debugging"
                }),
                "show_graph": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Generate visual graph of the curve"
                }),
            }
        }
    
    RETURN_TYPES = ("TIMESTEP_KEYFRAME", "IMAGE",)
    RETURN_NAMES = ("TIMESTEP_KF", "curve_graph",)
    FUNCTION = "generate_keyframes"
    CATEGORY = "conditioning/controlnet"
    
    def generate_keyframes(self, num_keyframes, start_percent, end_percent, 
                          start_strength, end_strength, curve_type, curve_param,
                          prev_timestep_kf=None, invert_curve=False, print_keyframes=False,
                          show_graph=True):
        """Generate curved timestep keyframes for ControlNet strength scheduling"""
        
        try:
            if not ACN_AVAILABLE:
                raise Exception("Advanced ControlNet is not installed or could not be imported.")
            
            # Ensure start_percent < end_percent
            if start_percent >= end_percent:
                raise ValueError(f"start_percent must be less than end_percent")
            
            # Create normalized array from 0 to 1
            t = np.linspace(0, 1, num_keyframes)
            
            # Generate NORMALIZED curve (always 0 to 1, representing progress)
            # The curve shape determines HOW we interpolate, not the direction
            if curve_type == "linear":
                curve = t
            elif curve_type == "ease_in":
                # Slow start, fast end
                curve = t ** curve_param
            elif curve_type == "ease_out":
                # Fast start, slow end
                curve = 1 - (1 - t) ** curve_param
            elif curve_type == "ease_in_out":
                # Slow start and end, fast middle
                curve = np.where(t < 0.5, 
                               2 ** (curve_param - 1) * t ** curve_param,
                               1 - (-2 * t + 2) ** curve_param / 2)
            elif curve_type == "sine_wave":
                # Oscillating wave
                curve = (np.sin(t * curve_param * 2 * np.pi) + 1) / 2
            elif curve_type == "bell_curve":
                # Peak in the middle
                center = 0.5
                width = 0.15 / curve_param
                curve = np.exp(-((t - center) ** 2) / (2 * width ** 2))
            elif curve_type == "reverse_bell":
                # Valley in the middle (inverted bell)
                center = 0.5
                width = 0.15 / curve_param
                bell = np.exp(-((t - center) ** 2) / (2 * width ** 2))
                curve = 1 - bell
            elif curve_type == "exponential":
                # Exponential growth
                curve = (np.exp(curve_param * t) - 1) / (np.exp(curve_param) - 1)
            elif curve_type == "bounce":
                # Bouncing abs sine wave
                curve = np.abs(np.sin(t * curve_param * np.pi))
            elif curve_type == "custom_bezier":
                # Custom cubic bezier curve
                p1 = curve_param / 10
                p2 = 1 - curve_param / 10
                curve = 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3
            else:
                curve = t
            
            # Invert curve if requested (flips the shape)
            if invert_curve:
                curve = 1 - curve
            
            # Now apply the curve to interpolate between start_strength and end_strength
            # curve goes from 0 to 1, so this correctly interpolates
            strengths = start_strength + (end_strength - start_strength) * curve
            
            # Map to percent range
            percents = np.linspace(start_percent, end_percent, num_keyframes)
            
            # Create timestep keyframe group
            if prev_timestep_kf is not None:
                keyframe_group = prev_timestep_kf
            else:
                keyframe_group = TimestepKeyframeGroup()
            
            # Add keyframes
            for i, (percent, strength) in enumerate(zip(percents, strengths)):
                guarantee_steps = 1 if i == 0 else 0
                
                keyframe = TimestepKeyframe(
                    start_percent=float(percent),
                    strength=float(strength),
                    guarantee_steps=guarantee_steps
                )
                keyframe_group.add(keyframe)
                
                if print_keyframes:
                    print(f"[Curved Timestep] Keyframe {i}: percent={percent:.4f}, strength={strength:.4f}")
            
            if print_keyframes:
                print(f"[Curved Timestep] Total keyframes: {len(keyframe_group.keyframes)}")
            
            # Generate graph if requested
            graph_image = None
            if show_graph:
                try:
                    graph_image = self.generate_graph(percents, strengths, curve_type, curve_param, 
                                                      start_percent, end_percent, start_strength, end_strength)
                except Exception as e:
                    print(f"[Curved Timestep] Graph generation failed: {e}")
                    graph_image = None
            
            # Ensure we always return a valid image
            if graph_image is None:
                graph_image = self.create_dummy_image()
            
            return (keyframe_group, graph_image)
            
        except Exception as e:
            print(f"[Curved Timestep] ERROR: {e}")
            import traceback
            traceback.print_exc()
            # Return safe defaults
            keyframe_group = TimestepKeyframeGroup() if prev_timestep_kf is None else prev_timestep_kf
            dummy_image = self.create_dummy_image()
            return (keyframe_group, dummy_image)


    def generate_graph(self, percents, strengths, curve_type, curve_param, 
                      start_percent, end_percent, start_strength, end_strength):
        """Generate a matplotlib graph showing the curve"""
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        # Plot the curve
        ax.plot(percents * 100, strengths, 'b-', linewidth=2.5, label='Strength Curve')
        ax.scatter(percents * 100, strengths, c='red', s=50, zorder=5, label='Keyframes')
        
        # Styling
        ax.set_xlabel('Generation Progress (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('ControlNet Strength', fontsize=12, fontweight='bold')
        ax.set_title(f'Curve: {curve_type} (param={curve_param:.2f})', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best')
        
        # Set axis limits with some padding
        ax.set_xlim(start_percent * 100 - 5, end_percent * 100 + 5)
        y_min = min(0, min(strengths) - 0.1)
        y_max = max(strengths) + 0.1
        ax.set_ylim(y_min, y_max)
        
        # Add info text
        info_text = f'Range: {start_percent:.2f} → {end_percent:.2f}\n'
        info_text += f'Strength: {start_strength:.2f} → {end_strength:.2f}\n'
        info_text += f'Keyframes: {len(percents)}'
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
               fontsize=10)
        
        plt.tight_layout()
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        # Convert to ComfyUI image format (tensor)
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array)[None,]
        
        return img_tensor
    
    
    def create_dummy_image(self):
        """Create a small dummy image when graph generation is disabled or fails"""
        # Create a simple 64x64 black image
        img_array = np.zeros((64, 64, 3), dtype=np.float32)
        img_tensor = torch.from_numpy(img_array)[None,]
        return img_tensor


# Node registration
NODE_CLASS_MAPPINGS = {
    "Curved ControlNet Scheduler": CurvedControlNetScheduler
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Curved ControlNet Scheduler": "Curved ControlNet Scheduler"
}