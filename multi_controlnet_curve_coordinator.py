import numpy as np
import matplotlib
matplotlib.use('Agg')
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
except Exception:
    try:
        import sys
        import os
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

# Preset configurations
CURVE_PRESETS = {
    "Custom": None,
    "Fade Out": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "ease_out", "curve_param": 2.0},
    "Fade In": {"start_strength": 0.0, "end_strength": 1.0, "curve_type": "ease_in", "curve_param": 2.0},
    "Peak Control": {"start_strength": 0.0, "end_strength": 1.0, "curve_type": "bell_curve", "curve_param": 2.0},
    "Valley Control": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "reverse_bell", "curve_param": 2.0},
    "Strong Start+End": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "reverse_bell", "curve_param": 3.0},
    "Oscillating": {"start_strength": 0.0, "end_strength": 1.0, "curve_type": "sine_wave", "curve_param": 3.0},
    "Exponential Decay": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "exponential", "curve_param": 4.0},
    "Smooth Transition": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "ease_in_out", "curve_param": 2.0},
}

EASING_FUNCTIONS = {
    "ease_in_quad": lambda t: t ** 2,
    "ease_out_quad": lambda t: 1 - (1 - t) ** 2,
    "ease_in_out_quad": lambda t: 2 * t ** 2 if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2,
    "ease_in_cubic": lambda t: t ** 3,
    "ease_out_cubic": lambda t: 1 - (1 - t) ** 3,
    "ease_in_out_cubic": lambda t: 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2,
    "ease_in_quart": lambda t: t ** 4,
    "ease_out_quart": lambda t: 1 - (1 - t) ** 4,
    "ease_in_out_quart": lambda t: 8 * t ** 4 if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2,
}

class MultiControlNetCurveCoordinator:
    """
    Coordinate multiple ControlNet curves simultaneously with independent timing.
    Define up to 4 separate ControlNet curves, each with its own start/end timing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        curve_types = [
            "linear", "ease_in", "ease_out", "ease_in_out",
            "ease_in_quad", "ease_out_quad", "ease_in_out_quad",
            "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
            "ease_in_quart", "ease_out_quart", "ease_in_out_quart",
            "sine_wave", "bell_curve", "reverse_bell",
            "exponential", "bounce", "custom_bezier"
        ]
        
        return {
            "required": {
                # Global settings
                "num_keyframes": ("INT", {
                    "default": 10,
                    "min": 2,
                    "max": 100,
                    "step": 1,
                    "tooltip": "Number of keyframes (applies to all slots)"
                }),
                
                # === SLOT A ===
                "divider_a": ("STRING", {
                    "default": "━━━━━━━ SLOT A ━━━━━━━",
                    "multiline": False,
                }),
                "enable_slot_a": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable ControlNet Slot A"
                }),
                "start_percent_a": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "Start point for Slot A"
                }),
                "end_percent_a": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "End point for Slot A"
                }),
                "preset_a": (list(CURVE_PRESETS.keys()), {
                    "default": "Fade Out",
                    "tooltip": "Preset for Slot A (overrides settings below)"
                }),
                "curve_type_a": (curve_types, {
                    "default": "ease_out",
                    "tooltip": "Curve type for Slot A"
                }),
                "start_strength_a": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Start strength for Slot A"
                }),
                "end_strength_a": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "End strength for Slot A"
                }),
                "curve_param_a": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve parameter for Slot A"
                }),
                
                # === SLOT B ===
                "divider_b": ("STRING", {
                    "default": "━━━━━━━ SLOT B ━━━━━━━",
                    "multiline": False,
                }),
                "enable_slot_b": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Enable ControlNet Slot B"
                }),
                "start_percent_b": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "Start point for Slot B"
                }),
                "end_percent_b": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "End point for Slot B"
                }),
                "preset_b": (list(CURVE_PRESETS.keys()), {
                    "default": "Fade In",
                    "tooltip": "Preset for Slot B"
                }),
                "curve_type_b": (curve_types, {
                    "default": "ease_in",
                    "tooltip": "Curve type for Slot B"
                }),
                "start_strength_b": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Start strength for Slot B"
                }),
                "end_strength_b": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "End strength for Slot B"
                }),
                "curve_param_b": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve parameter for Slot B"
                }),
                
                # === SLOT C ===
                "divider_c": ("STRING", {
                    "default": "━━━━━━━ SLOT C ━━━━━━━",
                    "multiline": False,
                }),
                "enable_slot_c": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable ControlNet Slot C"
                }),
                "start_percent_c": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "Start point for Slot C"
                }),
                "end_percent_c": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "End point for Slot C"
                }),
                "preset_c": (list(CURVE_PRESETS.keys()), {
                    "default": "Peak Control",
                    "tooltip": "Preset for Slot C"
                }),
                "curve_type_c": (curve_types, {
                    "default": "bell_curve",
                    "tooltip": "Curve type for Slot C"
                }),
                "start_strength_c": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Start strength for Slot C"
                }),
                "end_strength_c": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "End strength for Slot C"
                }),
                "curve_param_c": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve parameter for Slot C"
                }),
                
                # === SLOT D ===
                "divider_d": ("STRING", {
                    "default": "━━━━━━━ SLOT D ━━━━━━━",
                    "multiline": False,
                }),
                "enable_slot_d": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Enable ControlNet Slot D"
                }),
                "start_percent_d": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "Start point for Slot D"
                }),
                "end_percent_d": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.001,
                    "tooltip": "End point for Slot D"
                }),
                "preset_d": (list(CURVE_PRESETS.keys()), {
                    "default": "Custom",
                    "tooltip": "Preset for Slot D"
                }),
                "curve_type_d": (curve_types, {
                    "default": "linear",
                    "tooltip": "Curve type for Slot D"
                }),
                "start_strength_d": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Start strength for Slot D"
                }),
                "end_strength_d": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "End strength for Slot D"
                }),
                "curve_param_d": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve parameter for Slot D"
                }),
            }
        }

    RETURN_TYPES = ("TIMESTEP_KEYFRAME", "TIMESTEP_KEYFRAME", "TIMESTEP_KEYFRAME", "TIMESTEP_KEYFRAME", "IMAGE", "STRING")
    RETURN_NAMES = ("SLOT_A", "SLOT_B", "SLOT_C", "SLOT_D", "combined_graph", "info")
    FUNCTION = "coordinate_curves"
    CATEGORY = "conditioning/controlnet"

    def calculate_curve(self, t, curve_type, curve_param):
        """Calculate curve values (reused from your existing node)"""
        t = np.clip(t, 0, 1)
        
        if curve_type == "linear":
            return t
        elif curve_type in ["ease_in", "ease_out", "ease_in_out"]:
            if curve_type == "ease_in":
                return t ** curve_param
            elif curve_type == "ease_out":
                return 1 - (1 - t) ** curve_param
            else:  # ease_in_out
                return np.where(t < 0.5, 
                    2**(curve_param-1) * t**curve_param,
                    1 - (-2*t + 2)**curve_param / (2**(curve_param-1)))
        elif curve_type in EASING_FUNCTIONS:
            return np.array([EASING_FUNCTIONS[curve_type](ti) for ti in t])
        elif curve_type == "sine_wave":
            return (np.sin(t * np.pi * curve_param * 2 - np.pi/2) + 1) / 2
        elif curve_type == "bell_curve":
            center = 0.5
            return np.exp(-curve_param * (t - center)**2)
        elif curve_type == "reverse_bell":
            center = 0.5
            return 1 - np.exp(-curve_param * (t - center)**2)
        elif curve_type == "exponential":
            return (np.exp(curve_param * t) - 1) / (np.exp(curve_param) - 1)
        elif curve_type == "bounce":
            n = int(curve_param)
            decay = 0.5
            result = np.zeros_like(t)
            for i in range(n):
                phase = t * n - i
                bounce = np.maximum(0, 1 - np.abs(phase))
                result += bounce * (decay ** i)
            return result / np.max(result) if np.max(result) > 0 else result
        elif curve_type == "custom_bezier":
            p0, p1, p2, p3 = 0, curve_param/10, 1-curve_param/10, 1
            return 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3
        else:
            return t

    def create_keyframe_group(self, num_keyframes, start_percent, end_percent, 
                            start_strength, end_strength, curve_type, curve_param):
        """Create a TimestepKeyframeGroup for a single slot"""
        try:
            keyframe_group = TimestepKeyframeGroup()
            
            t = np.linspace(0, 1, num_keyframes)
            percents = start_percent + (end_percent - start_percent) * t
            
            curve = self.calculate_curve(t, curve_type, curve_param)
            strengths = start_strength + (end_strength - start_strength) * curve
            
            for i, (percent, strength) in enumerate(zip(percents, strengths)):
                keyframe = TimestepKeyframe(
                    start_percent=float(percent),
                    strength=float(strength)
                )
                keyframe_group.add(keyframe)
            
            return keyframe_group, percents, strengths
            
        except Exception as e:
            print(f"[Multi-CN Coordinator] Error creating keyframe group: {e}")
            return TimestepKeyframeGroup(), np.array([]), np.array([])

    def apply_preset(self, preset_name, curve_type, start_strength, end_strength, curve_param):
        """Apply preset if not Custom"""
        if preset_name != "Custom" and preset_name in CURVE_PRESETS:
            preset = CURVE_PRESETS[preset_name]
            if preset:
                return (
                    preset.get("curve_type", curve_type),
                    preset.get("start_strength", start_strength),
                    preset.get("end_strength", end_strength),
                    preset.get("curve_param", curve_param)
                )
        return curve_type, start_strength, end_strength, curve_param

    def generate_combined_graph(self, slot_data):
        """Generate graph showing all active curves with timing windows"""
        try:
            fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
            
            colors = ['#2E86DE', '#EE5A6F', '#10AC84', '#F79F1F']
            slot_names = ['Slot A', 'Slot B', 'Slot C', 'Slot D']
            
            active_count = 0
            for i, (enabled, percents, strengths, curve_type, label, start_pct, end_pct) in enumerate(slot_data):
                if enabled and len(percents) > 0:
                    # Draw shaded region for active window
                    ax.axvspan(start_pct * 100, end_pct * 100, 
                             alpha=0.1, color=colors[i], zorder=0)
                    
                    # Draw the curve
                    ax.plot(percents * 100, strengths, 
                           color=colors[i], linewidth=2.5, 
                           label=f'{slot_names[i]}: {curve_type} [{start_pct:.2f}-{end_pct:.2f}]', 
                           alpha=0.85)
                    ax.scatter(percents * 100, strengths, 
                             c=colors[i], s=40, zorder=5, alpha=0.6)
                    active_count += 1
            
            if active_count == 0:
                ax.text(0.5, 0.5, 'No active slots', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=16, color='gray')
            
            ax.set_xlabel('Generation Progress (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('ControlNet Strength', fontsize=12, fontweight='bold')
            ax.set_title('Multi-ControlNet Curve Coordination (Shaded = Active Window)', 
                        fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='best', fontsize=9, framealpha=0.9)
            
            ax.set_xlim(-5, 105)
            
            all_strengths = []
            for enabled, percents, strengths, _, _, _, _ in slot_data:
                if enabled and len(strengths) > 0:
                    all_strengths.extend(strengths)
            
            if all_strengths:
                y_min = min(0, min(all_strengths) - 0.1)
                y_max = max(all_strengths) + 0.1
                ax.set_ylim(y_min, y_max)
            else:
                ax.set_ylim(-0.1, 1.1)
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            plt.close(fig)
            
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            
            return img_tensor
            
        except Exception as e:
            print(f"[Multi-CN Coordinator] Graph failed: {e}")
            return self.create_dummy_image()
        finally:
            plt.close('all')

    def create_dummy_image(self):
        """Create dummy image when graph fails"""
        try:
            img_array = np.zeros((64, 64, 3), dtype=np.float32)
            return torch.from_numpy(img_array)[None,]
        except Exception:
            return torch.zeros((1, 64, 64, 3), dtype=torch.float32)

    def coordinate_curves(self, num_keyframes,
                         divider_a, enable_slot_a, start_percent_a, end_percent_a, preset_a, curve_type_a, start_strength_a, end_strength_a, curve_param_a,
                         divider_b, enable_slot_b, start_percent_b, end_percent_b, preset_b, curve_type_b, start_strength_b, end_strength_b, curve_param_b,
                         divider_c, enable_slot_c, start_percent_c, end_percent_c, preset_c, curve_type_c, start_strength_c, end_strength_c, curve_param_c,
                         divider_d, enable_slot_d, start_percent_d, end_percent_d, preset_d, curve_type_d, start_strength_d, end_strength_d, curve_param_d):
        """Main execution function"""
        
        try:
            # Apply presets
            curve_type_a, start_strength_a, end_strength_a, curve_param_a = \
                self.apply_preset(preset_a, curve_type_a, start_strength_a, end_strength_a, curve_param_a)
            curve_type_b, start_strength_b, end_strength_b, curve_param_b = \
                self.apply_preset(preset_b, curve_type_b, start_strength_b, end_strength_b, curve_param_b)
            curve_type_c, start_strength_c, end_strength_c, curve_param_c = \
                self.apply_preset(preset_c, curve_type_c, start_strength_c, end_strength_c, curve_param_c)
            curve_type_d, start_strength_d, end_strength_d, curve_param_d = \
                self.apply_preset(preset_d, curve_type_d, start_strength_d, end_strength_d, curve_param_d)
            
            # Create keyframe groups for each slot with individual timing
            kf_a, percents_a, strengths_a = self.create_keyframe_group(
                num_keyframes, start_percent_a, end_percent_a, 
                start_strength_a, end_strength_a, curve_type_a, curve_param_a
            ) if enable_slot_a else (TimestepKeyframeGroup(), np.array([]), np.array([]))
            
            kf_b, percents_b, strengths_b = self.create_keyframe_group(
                num_keyframes, start_percent_b, end_percent_b,
                start_strength_b, end_strength_b, curve_type_b, curve_param_b
            ) if enable_slot_b else (TimestepKeyframeGroup(), np.array([]), np.array([]))
            
            kf_c, percents_c, strengths_c = self.create_keyframe_group(
                num_keyframes, start_percent_c, end_percent_c,
                start_strength_c, end_strength_c, curve_type_c, curve_param_c
            ) if enable_slot_c else (TimestepKeyframeGroup(), np.array([]), np.array([]))
            
            kf_d, percents_d, strengths_d = self.create_keyframe_group(
                num_keyframes, start_percent_d, end_percent_d,
                start_strength_d, end_strength_d, curve_type_d, curve_param_d
            ) if enable_slot_d else (TimestepKeyframeGroup(), np.array([]), np.array([]))
            
            # Generate combined graph with timing windows
            slot_data = [
                (enable_slot_a, percents_a, strengths_a, curve_type_a, "Slot A", start_percent_a, end_percent_a),
                (enable_slot_b, percents_b, strengths_b, curve_type_b, "Slot B", start_percent_b, end_percent_b),
                (enable_slot_c, percents_c, strengths_c, curve_type_c, "Slot C", start_percent_c, end_percent_c),
                (enable_slot_d, percents_d, strengths_d, curve_type_d, "Slot D", start_percent_d, end_percent_d),
            ]
            
            graph = self.generate_combined_graph(slot_data)
            
            # Generate info text
            info_lines = [
                f"Multi-ControlNet Curve Coordinator",
                f"Keyframes: {num_keyframes}",
                ""
            ]
            
            if enable_slot_a:
                info_lines.append(f"Slot A: {curve_type_a} | {start_strength_a:.2f}→{end_strength_a:.2f} | [{start_percent_a:.2f}-{end_percent_a:.2f}]")
            if enable_slot_b:
                info_lines.append(f"Slot B: {curve_type_b} | {start_strength_b:.2f}→{end_strength_b:.2f} | [{start_percent_b:.2f}-{end_percent_b:.2f}]")
            if enable_slot_c:
                info_lines.append(f"Slot C: {curve_type_c} | {start_strength_c:.2f}→{end_strength_c:.2f} | [{start_percent_c:.2f}-{end_percent_c:.2f}]")
            if enable_slot_d:
                info_lines.append(f"Slot D: {curve_type_d} | {start_strength_d:.2f}→{end_strength_d:.2f} | [{start_percent_d:.2f}-{end_percent_d:.2f}]")
            
            info = "\n".join(info_lines)
            
            return (kf_a, kf_b, kf_c, kf_d, graph, info)
            
        except Exception as e:
            print(f"[Multi-CN Coordinator] ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            dummy_kf = TimestepKeyframeGroup()
            dummy_graph = self.create_dummy_image()
            error_info = f"Error: {str(e)}"
            
            return (dummy_kf, dummy_kf, dummy_kf, dummy_kf, dummy_graph, error_info)


NODE_CLASS_MAPPINGS = {
    "Multi-ControlNet Curve Coordinator": MultiControlNetCurveCoordinator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Multi-ControlNet Curve Coordinator": "Multi-ControlNet Curve Coordinator"
}