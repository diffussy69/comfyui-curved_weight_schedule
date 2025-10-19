import numpy as np

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

class CurvedTimestepKeyframes:
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
                "curve_type": (["strong_to_weak", "weak_to_strong", "linear", "ease_in", 
                               "ease_out", "ease_in_out", "sine_wave", "bell_curve", 
                               "reverse_bell", "exponential_up", "exponential_down", 
                               "bounce", "custom_bezier"],),
                "curve_param": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve steepness: higher = faster transition, lower = slower transition"
                }),
            },
            "optional": {
                "prev_timestep_kf": ("TIMESTEP_KEYFRAME",),
                "invert_curve": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert the curve"
                }),
                "print_keyframes": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print generated keyframes for debugging"
                }),
            }
        }
    
    RETURN_TYPES = ("TIMESTEP_KEYFRAME",)
    RETURN_NAMES = ("TIMESTEP_KF",)
    FUNCTION = "generate_keyframes"
    CATEGORY = "conditioning/controlnet"
    
    def generate_keyframes(self, num_keyframes, start_percent, end_percent, 
                          start_strength, end_strength, curve_type, curve_param,
                          prev_timestep_kf=None, invert_curve=False, print_keyframes=False):
        """Generate curved timestep keyframes for ControlNet strength scheduling"""
        
        if not ACN_AVAILABLE:
            raise Exception("Advanced ControlNet is not installed or could not be imported. "
                          "Please install ComfyUI-Advanced-ControlNet from: "
                          "https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet")
        
        print(f"[Curved Timestep] Generating {num_keyframes} keyframes from {start_percent} to {end_percent}")
        print(f"[Curved Timestep] Strength range: {start_strength} to {end_strength}")
        print(f"[Curved Timestep] Curve type: {curve_type}, param: {curve_param}")
        
        # Ensure start_percent < end_percent
        if start_percent >= end_percent:
            raise ValueError(f"start_percent ({start_percent}) must be less than end_percent ({end_percent})")
        
        # Create normalized array from 0 to 1
        t = np.linspace(0, 1, num_keyframes)
        
        # Generate curve based on type
        # Curves output values from 0 to 1, which get mapped to start_strength → end_strength
        if curve_type == "strong_to_weak":
            # We want to go from start_strength (high) to end_strength (low)
            # So curve should go from 1 to 0
            curve = 1 - (t ** (1 / curve_param))
        elif curve_type == "weak_to_strong":
            # We want to go from start_strength (low) to end_strength (high)  
            # So curve should go from 0 to 1
            curve = t ** (1 / curve_param)
        elif curve_type == "linear":
            curve = t
        elif curve_type == "ease_in":
            curve = t ** curve_param
        elif curve_type == "ease_out":
            curve = 1 - (1 - t) ** curve_param
        elif curve_type == "ease_in_out":
            curve = np.where(t < 0.5, 
                           2 ** (curve_param - 1) * t ** curve_param,
                           1 - (-2 * t + 2) ** curve_param / 2)
        elif curve_type == "sine_wave":
            curve = (np.sin(t * curve_param * 2 * np.pi) + 1) / 2
        elif curve_type == "bell_curve":
            curve = np.exp(-((t - 0.5) ** 2) / (2 * (0.15 / curve_param) ** 2))
        elif curve_type == "reverse_bell":
            bell = np.exp(-((t - 0.5) ** 2) / (2 * (0.15 / curve_param) ** 2))
            curve = 1 - bell
        elif curve_type == "exponential_up":
            curve = (np.exp(curve_param * t) - 1) / (np.exp(curve_param) - 1)
        elif curve_type == "exponential_down":
            curve = (np.exp(curve_param * (1 - t)) - 1) / (np.exp(curve_param) - 1)
        elif curve_type == "bounce":
            curve = np.abs(np.sin(t * curve_param * np.pi))
        elif curve_type == "custom_bezier":
            curve = 3 * (1 - t) ** 2 * t * curve_param / 10 + 3 * (1 - t) * t ** 2 * (1 - curve_param / 10) + t ** 3
        else:
            curve = t
        
        # Map curve values to strength range
        # For most curves: curve goes 0→1, so we map start_strength → end_strength
        # For strong_to_weak/weak_to_strong: curve already handles the direction
        strengths = start_strength * curve + end_strength * (1 - curve)
        
        # Map to percent range
        percents = np.linspace(start_percent, end_percent, num_keyframes)
        
        # Create timestep keyframe group
        if prev_timestep_kf is not None:
            keyframe_group = prev_timestep_kf
        else:
            keyframe_group = TimestepKeyframeGroup()
        
        # Add keyframes
        for i, (percent, strength) in enumerate(zip(percents, strengths)):
            # First keyframe gets guarantee_steps=1, rest get 0
            guarantee_steps = 1 if i == 0 else 0
            
            keyframe = TimestepKeyframe(
                start_percent=float(percent),
                strength=float(strength),
                guarantee_steps=guarantee_steps
            )
            keyframe_group.add(keyframe)
            
            if print_keyframes or True:  # Always print for debugging
                print(f"[Curved Timestep] Keyframe {i}: percent={percent:.4f}, strength={strength:.4f}")
        
        print(f"[Curved Timestep] Total keyframes in group: {len(keyframe_group.keyframes)}")
        return (keyframe_group,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "CurvedTimestepKeyframes": CurvedTimestepKeyframes
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CurvedTimestepKeyframes": "Curved Timestep Keyframes"
}