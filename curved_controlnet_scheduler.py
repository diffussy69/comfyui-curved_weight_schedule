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
                "curve_type": ([
                    "linear",           # Constant rate
                    "ease_in",         # Slow start, fast end
                    "ease_out",        # Fast start, slow end
                    "ease_in_out",     # Slow start and end, fast middle
                    "sine_wave",       # Oscillating wave
                    "bell_curve",      # Peak in the middle
                    "reverse_bell",    # Valley in the middle
                    "exponential",     # Exponential growth
                    "bounce",          # Bouncing effect
                    "custom_bezier"    # Custom cubic bezier
                ], {
                    "tooltip": "Shape of the interpolation curve between start and end strength"
                }),
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
                "clamp_strengths": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Clamp strength values to valid range (0-10)"
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
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution if any parameter changes
        # This ensures the graph updates properly
        return float("nan")
    
    def validate_inputs(self, start_percent, end_percent, num_keyframes, start_strength, end_strength):
        """Validate inputs before processing"""
        errors = []
        warnings = []
        
        if start_percent >= end_percent:
            errors.append(f"start_percent ({start_percent}) must be < end_percent ({end_percent})")
        
        if num_keyframes < 2:
            errors.append(f"num_keyframes ({num_keyframes}) must be at least 2")
        
        if end_percent - start_percent < 0.01 and num_keyframes > 100:
            warnings.append("Too many keyframes for such a small range - may cause performance issues")
        
        if start_strength < 0 or end_strength < 0:
            warnings.append(f"Negative strength values detected (start: {start_strength}, end: {end_strength})")
        
        if start_strength == end_strength:
            warnings.append(f"Start and end strength are identical ({start_strength}) - curve will be flat")
        
        return errors, warnings
    
    def generate_keyframes(self, num_keyframes, start_percent, end_percent, 
                          start_strength, end_strength, curve_type, curve_param,
                          prev_timestep_kf=None, invert_curve=False, clamp_strengths=True,
                          print_keyframes=False, show_graph=True):
        """Generate curved timestep keyframes for ControlNet strength scheduling"""
        
        try:
            if not ACN_AVAILABLE:
                print("[ERROR] Advanced ControlNet is not installed or could not be imported.")
                print("[ERROR] Returning passthrough to prevent workflow crash.")
                if prev_timestep_kf is not None:
                    return (prev_timestep_kf, self.create_dummy_image())
                else:
                    # Create a minimal keyframe group with default behavior
                    keyframe_group = TimestepKeyframeGroup() if 'TimestepKeyframeGroup' in globals() else None
                    if keyframe_group is None:
                        raise Exception("Advanced ControlNet is required but not available")
                    return (keyframe_group, self.create_dummy_image())
            
            # Validate inputs
            errors, warnings = self.validate_inputs(start_percent, end_percent, num_keyframes, 
                                                    start_strength, end_strength)
            
            if errors:
                error_msg = "Input validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
                raise ValueError(error_msg)
            
            if warnings:
                for warning in warnings:
                    print(f"[Warning] {warning}")
            
            # Clamp strength values to prevent issues
            start_strength = max(0, start_strength)
            end_strength = max(0, end_strength)
            
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
                width = 0.15 / max(curve_param, 0.1)  # Prevent division by tiny numbers
                curve = np.exp(-((t - center) ** 2) / (2 * width ** 2))
            elif curve_type == "reverse_bell":
                # Valley in the middle (inverted bell)
                center = 0.5
                width = 0.15 / max(curve_param, 0.1)  # Prevent division by tiny numbers
                bell = np.exp(-((t - center) ** 2) / (2 * width ** 2))
                curve = 1 - bell
            elif curve_type == "exponential":
                # Exponential growth with numerical stability
                safe_param = min(curve_param, 10.0)  # Clamp to prevent overflow
                denom = np.exp(safe_param) - 1
                if denom < 1e-10:  # Prevent division by very small numbers
                    print("[Warning] Exponential curve parameter too small, using linear")
                    curve = t
                else:
                    curve = (np.exp(safe_param * t) - 1) / denom
            elif curve_type == "bounce":
                # Bouncing abs sine wave
                curve = np.abs(np.sin(t * curve_param * np.pi))
            elif curve_type == "custom_bezier":
                # Custom cubic bezier curve
                p1 = curve_param / 10
                p2 = 1 - curve_param / 10
                curve = 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3
            else:
                print(f"[Warning] Unknown curve type '{curve_type}', using linear")
                curve = t
            
            # Invert curve if requested (flips the shape)
            if invert_curve:
                curve = 1 - curve
            
            # Check for NaN values in curve
            if np.any(np.isnan(curve)):
                print("[ERROR] NaN values detected in curve calculation, using linear fallback")
                curve = np.linspace(0, 1, num_keyframes)
            
            # Now apply the curve to interpolate between start_strength and end_strength
            # curve goes from 0 to 1, so this correctly interpolates
            strengths = start_strength + (end_strength - start_strength) * curve
            
            # Clamp strengths if requested
            if clamp_strengths:
                strengths = np.clip(strengths, 0.0, 10.0)
            
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
                    import traceback
                    traceback.print_exc()
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
            if prev_timestep_kf is not None:
                keyframe_group = prev_timestep_kf
            else:
                try:
                    keyframe_group = TimestepKeyframeGroup()
                except:
                    # If we can't even create a basic group, we have bigger problems
                    print("[CRITICAL] Cannot create TimestepKeyframeGroup - Advanced ControlNet may not be installed")
                    keyframe_group = None
            
            dummy_image = self.create_dummy_image()
            return (keyframe_group, dummy_image)


    def generate_graph(self, percents, strengths, curve_type, curve_param, 
                      start_percent, end_percent, start_strength, end_strength):
        """Generate a matplotlib graph showing the curve"""
        
        fig = None
        try:
            # Add validation
            if len(percents) == 0 or len(strengths) == 0:
                print("[Warning] Empty data for graph generation")
                return self.create_dummy_image()
            
            # Ensure arrays are valid
            percents = np.asarray(percents)
            strengths = np.asarray(strengths)
            
            if np.any(np.isnan(percents)) or np.any(np.isnan(strengths)):
                print("[Warning] NaN values detected in curve data")
                return self.create_dummy_image()
            
            if np.any(np.isinf(percents)) or np.any(np.isinf(strengths)):
                print("[Warning] Infinite values detected in curve data")
                return self.create_dummy_image()
            
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
            fig = None  # Mark as closed
            
            # Convert to ComfyUI image format (tensor)
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            
            # Validate tensor shape
            if len(img_tensor.shape) != 4 or img_tensor.shape[0] != 1:
                print(f"[Warning] Unexpected tensor shape: {img_tensor.shape}")
            
            return img_tensor
            
        except Exception as e:
            print(f"[Curved Timestep] Graph generation failed: {e}")
            import traceback
            traceback.print_exc()
            return self.create_dummy_image()
        finally:
            # Ensure matplotlib resources are always cleaned up
            if fig is not None:
                plt.close(fig)
            plt.close('all')
    
    
    def create_dummy_image(self):
        """Create a small dummy image when graph generation is disabled or fails"""
        try:
            img_array = np.zeros((64, 64, 3), dtype=np.float32)
            img_tensor = torch.from_numpy(img_array)[None,]
            
            # Validate tensor shape
            if img_tensor.shape != (1, 64, 64, 3):
                print(f"[Warning] Unexpected dummy image tensor shape: {img_tensor.shape}")
            
            return img_tensor
        except Exception as e:
            print(f"[Error] Failed to create dummy image: {e}")
            # Return minimal valid tensor as absolute fallback
            return torch.zeros((1, 64, 64, 3), dtype=torch.float32)


# Node registration
NODE_CLASS_MAPPINGS = {
    "Curved ControlNet Scheduler": CurvedControlNetScheduler
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Curved ControlNet Scheduler": "Curved ControlNet Scheduler"
}