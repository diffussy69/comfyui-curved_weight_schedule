import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
from PIL import Image
import torch
import json
import os
import csv
import re

# Import Advanced ControlNet classes
try:
    from .control import ControlWeights
    from .nodes import TimestepKeyframeNode
    from .utils import TimestepKeyframeGroup, TimestepKeyframe
    ACN_AVAILABLE = True
except Exception:
    try:
        import sys
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

# Preset configurations
CURVE_PRESETS = {
    "Custom": None,
    "Fade Out": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "ease_out", "curve_param": 2.0},
    "Fade In": {"start_strength": 0.0, "end_strength": 1.0, "curve_type": "ease_in", "curve_param": 2.0},
    "Peak Control": {"start_strength": 0.5, "end_strength": 0.5, "curve_type": "bell_curve", "curve_param": 2.0},
    "Valley Control": {"start_strength": 0.5, "end_strength": 0.5, "curve_type": "reverse_bell", "curve_param": 2.0},
    "Strong Start+End": {"start_strength": 0.5, "end_strength": 0.5, "curve_type": "reverse_bell", "curve_param": 3.0},
    "Oscillating": {"start_strength": 0.5, "end_strength": 0.5, "curve_type": "sine_wave", "curve_param": 3.0},
    "Exponential Decay": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "exponential", "curve_param": 4.0},
    "Smooth Transition": {"start_strength": 1.0, "end_strength": 0.0, "curve_type": "ease_in_out", "curve_param": 2.0},
}

# Animation easing functions
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

class AdvancedCurvedControlNetScheduler:
    """
    Advanced version with presets, formulas, blending, and more features.
    Generates curved timestep keyframes for Advanced ControlNet.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(CURVE_PRESETS.keys()), {
                    "default": "Custom",
                    "tooltip": "Pre-configured curves (OVERRIDES strength/curve settings below when selected)"
                }),
                "mode": (["percent", "steps"], {
                    "default": "percent",
                    "tooltip": "Use percentage (0-1) or absolute steps"
                }),
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
                    "tooltip": "ControlNet strength at start (ignored if preset selected)"
                }),
                "end_strength": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "ControlNet strength at end (ignored if preset selected)"
                }),
                "curve_type": ([
                    "linear",
                    "ease_in", "ease_out", "ease_in_out",
                    "ease_in_quad", "ease_out_quad", "ease_in_out_quad",
                    "ease_in_cubic", "ease_out_cubic", "ease_in_out_cubic",
                    "ease_in_quart", "ease_out_quart", "ease_in_out_quart",
                    "sine_wave", "bell_curve", "reverse_bell",
                    "exponential", "bounce", "custom_bezier",
                    "custom_formula"
                ], {
                    "tooltip": "Curve shape (ignored if preset selected)"
                }),
                "curve_param": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Curve steepness (ignored if preset selected)"
                }),
            },
            "optional": {
                "total_steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Total number of sampling steps (only used in 'steps' mode)"
                }),
                "custom_formula": ("STRING", {
                    "default": "t",
                    "multiline": True,
                    "tooltip": "Custom math formula using 't' (0 to 1). Examples: 'sin(t*3.14)', 't**2', '1-exp(-5*t)'"
                }),
                "prev_timestep_kf": ("TIMESTEP_KEYFRAME",),
                "batch_images": ("IMAGE", {
                    "tooltip": "Optional: Batch of preprocessed images. Keyframe i will use image i."
                }),
                "invert_curve": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert the curve shape"
                }),
                "mirror_curve": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Create symmetrical curve around midpoint"
                }),
                "repeat_curve": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "tooltip": "Repeat the curve pattern N times"
                }),
                "adaptive_keyframes": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Automatically place more keyframes where curve changes rapidly"
                }),
                "blend_curve_type": (["none"] + [
                    "linear", "ease_in", "ease_out", "ease_in_out",
                    "sine_wave", "bell_curve", "exponential"
                ], {
                    "default": "none",
                    "tooltip": "Second curve to blend with primary curve"
                }),
                "blend_amount": ("FLOAT", {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "How much to blend with second curve (0=primary only, 1=blend only)"
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
                "comparison_curve": (["none"] + [
                    "linear", "ease_in", "ease_out", "ease_in_out",
                    "sine_wave", "bell_curve", "exponential"
                ], {
                    "default": "none",
                    "tooltip": "Show comparison with another curve type"
                }),
                "save_curve": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Save curve data to CSV file"
                }),
                "curve_filename": ("STRING", {
                    "default": "curve_export",
                    "tooltip": "Filename for curve export (without extension)"
                }),
            }
        }

    RETURN_TYPES = ("TIMESTEP_KEYFRAME", "IMAGE", "STRING",)
    RETURN_NAMES = ("TIMESTEP_KF", "curve_graph", "curve_stats",)
    FUNCTION = "generate_keyframes"
    CATEGORY = "conditioning/controlnet"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def apply_preset(self, preset, start_strength, end_strength, curve_type, curve_param):
        """Apply preset values if preset is not Custom"""
        if preset != "Custom" and preset in CURVE_PRESETS:
            preset_values = CURVE_PRESETS[preset]
            if preset_values:
                new_start = preset_values.get("start_strength", start_strength)
                new_end = preset_values.get("end_strength", end_strength)
                new_curve = preset_values.get("curve_type", curve_type)
                new_param = preset_values.get("curve_param", curve_param)

                print(f"\n[Preset Applied: {preset}]")
                print(f"  Start Strength: {start_strength} → {new_start}")
                print(f"  End Strength: {end_strength} → {new_end}")
                print(f"  Curve Type: {curve_type} → {new_curve}")
                print(f"  Curve Param: {curve_param} → {new_param}")
                print(f"  (Note: UI values don't auto-update, but these values ARE being used)\n")

                return (new_start, new_end, new_curve, new_param)
        return start_strength, end_strength, curve_type, curve_param

    def validate_inputs(self, start_percent, end_percent, num_keyframes, start_strength, end_strength):
        """Validate inputs before processing"""
        errors = []
        warnings = []

        if start_percent >= end_percent:
            errors.append(f"start_percent ({start_percent}) must be < end_percent ({end_percent})")

        if num_keyframes < 2:
            errors.append(f"num_keyframes ({num_keyframes}) must be at least 2")

        if end_percent - start_percent < 0.01 and num_keyframes > 100:
            warnings.append("Too many keyframes for such a small range")

        if start_strength < 0 or end_strength < 0:
            warnings.append("Negative strength values detected")

        if start_strength == end_strength:
            warnings.append("Start and end strength are identical - curve will be flat")

        return errors, warnings

    def safe_eval_formula(self, formula, t):
        """Safely evaluate a mathematical formula"""
        try:
            safe_dict = {
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "exp": np.exp, "log": np.log, "log10": np.log10,
                "sqrt": np.sqrt, "abs": np.abs,
                "pi": np.pi, "e": np.e,
                "t": t, "np": np,
            }

            if any(word in formula.lower() for word in ["import", "exec", "eval", "compile", "__"]):
                raise ValueError("Formula contains forbidden operations")

            result = eval(formula, {"__builtins__": {}}, safe_dict)

            if not isinstance(result, np.ndarray):
                result = np.full_like(t, float(result))

            result_min, result_max = np.min(result), np.max(result)
            if result_max > result_min:
                result = (result - result_min) / (result_max - result_min)

            return result
        except Exception as e:
            print(f"[Error] Custom formula evaluation failed: {e}")
            return t

    def calculate_curve(self, t, curve_type, curve_param, custom_formula="t"):
        """Calculate curve values based on type"""
        try:
            if curve_type in EASING_FUNCTIONS:
                curve = EASING_FUNCTIONS[curve_type](t)
            elif curve_type == "linear":
                curve = t
            elif curve_type == "ease_in":
                curve = t ** curve_param
            elif curve_type == "ease_out":
                curve = 1 - (1 - t) ** curve_param
            elif curve_type == "ease_in_out":
                curve = np.where(
                    t < 0.5,
                    2 ** (curve_param - 1) * t ** curve_param,
                    1 - (-2 * t + 2) ** curve_param / 2
                )
            elif curve_type == "sine_wave":
                curve = (np.sin(t * curve_param * 2 * np.pi) + 1) / 2
            elif curve_type == "bell_curve":
                center = 0.5
                width = 0.15 / max(curve_param, 0.1)
                curve = np.exp(-((t - center) ** 2) / (2 * width ** 2))
            elif curve_type == "reverse_bell":
                center = 0.5
                width = 0.15 / max(curve_param, 0.1)
                bell = np.exp(-((t - center) ** 2) / (2 * width ** 2))
                curve = 1 - bell
            elif curve_type == "exponential":
                safe_param = min(curve_param, 10.0)
                denom = np.exp(safe_param) - 1
                if denom < 1e-10:
                    print("[Warning] Exponential parameter too small, using linear")
                    curve = t
                else:
                    curve = (np.exp(safe_param * t) - 1) / denom
            elif curve_type == "bounce":
                curve = np.abs(np.sin(t * curve_param * np.pi))
            elif curve_type == "custom_bezier":
                p1 = curve_param / 10
                p2 = 1 - curve_param / 10
                curve = 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3
            elif curve_type == "custom_formula":
                curve = self.safe_eval_formula(custom_formula, t)
            else:
                print(f"[Warning] Unknown curve type '{curve_type}', using linear")
                curve = t

            return curve
        except Exception as e:
            print(f"[Error] Curve calculation failed: {e}")
            return t

    def apply_adaptive_keyframes(self, percents, strengths, num_keyframes):
        """Redistribute keyframes based on curve rate of change"""
        try:
            derivatives = np.abs(np.diff(strengths))

            if np.sum(derivatives) > 0:
                derivatives = derivatives / np.sum(derivatives)
            else:
                return percents, strengths

            cum_derivatives = np.concatenate([[0], np.cumsum(derivatives)])

            new_indices = np.linspace(0, len(cum_derivatives) - 1, num_keyframes)
            new_percents = np.interp(new_indices, np.arange(len(percents)), percents)
            new_strengths = np.interp(new_indices, np.arange(len(strengths)), strengths)

            return new_percents, new_strengths
        except Exception as e:
            print(f"[Warning] Adaptive keyframes failed: {e}")
            return percents, strengths

    def calculate_statistics(self, percents, strengths):
        """Calculate curve statistics"""
        try:
            avg_strength = np.mean(strengths)
            max_strength = np.max(strengths)
            min_strength = np.min(strengths)
            max_idx = np.argmax(strengths)
            peak_at = percents[max_idx] * 100

            area = np.trapz(strengths, percents)

            if len(strengths) > 1:
                rate_of_change = np.mean(np.abs(np.diff(strengths)))
            else:
                rate_of_change = 0

            stats = f"""Curve Statistics:
============================
Average Strength: {avg_strength:.3f}
Max Strength: {max_strength:.3f} (at {peak_at:.1f}%)
Min Strength: {min_strength:.3f}
Area Under Curve: {area:.3f}
Avg Rate of Change: {rate_of_change:.4f}
Total Keyframes: {len(strengths)}
============================"""

            return stats
        except Exception as e:
            return f"Statistics calculation failed: {e}"

    def save_curve_to_csv(self, percents, strengths, filename):
        """Save curve data to CSV file"""
        try:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "output", "curves"
            )

            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, f"{filename}.csv")

            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["percent", "strength", "step"])
                for i, (p, s) in enumerate(zip(percents, strengths)):
                    writer.writerow([f"{p:.6f}", f"{s:.6f}", i])

            print(f"[Advanced Curved] Curve saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"[Error] Failed to save curve: {e}")
            return None

    def generate_keyframes(
        self, preset, mode, num_keyframes, start_percent, end_percent,
        start_strength, end_strength, curve_type, curve_param,
        total_steps=20, custom_formula="t",
        prev_timestep_kf=None, invert_curve=False, mirror_curve=False,
        repeat_curve=1, adaptive_keyframes=False,
        blend_curve_type="none", blend_amount=0.0,
        clamp_strengths=True, print_keyframes=False, show_graph=True,
        comparison_curve="none", save_curve=False, curve_filename="curve_export", batch_images=None
    ):
        """Generate curved timestep keyframes for ControlNet strength scheduling"""

        try:
            if not ACN_AVAILABLE:
                print("[ERROR] Advanced ControlNet not available")
                if prev_timestep_kf is not None:
                    return (prev_timestep_kf, self.create_dummy_image(), "ACN not available")
                else:
                    keyframe_group = TimestepKeyframeGroup() if 'TimestepKeyframeGroup' in globals() else None
                    if keyframe_group is None:
                        raise Exception("Advanced ControlNet is required")
                    return (keyframe_group, self.create_dummy_image(), "ACN not available")

            # Apply preset overrides
            start_strength, end_strength, curve_type, curve_param = self.apply_preset(
                preset, start_strength, end_strength, curve_type, curve_param
            )

            # If user chose steps mode, interpret start/end as steps unless already 0-1
            if mode == "steps":
                start_percent = start_percent if start_percent <= 1.0 else start_percent / max(total_steps, 1)
                end_percent = end_percent if end_percent <= 1.0 else end_percent / max(total_steps, 1)

            # Validate inputs
            errors, warnings = self.validate_inputs(start_percent, end_percent, num_keyframes, start_strength, end_strength)
            if errors:
                error_msg = "Validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
                raise ValueError(error_msg)
            for warning in warnings:
                print(f"[Warning] {warning}")

            # Clamp base strengths (we may clamp again at the end too)
            start_strength = max(0, start_strength)
            end_strength = max(0, end_strength)

            # Generate param t across repeats
            actual_keyframes = num_keyframes * repeat_curve
            t = np.linspace(0, 1, actual_keyframes)
            if repeat_curve > 1:
                t = (t * repeat_curve) % 1.0

            # Build primary curve
            curve = self.calculate_curve(t, curve_type, curve_param, custom_formula)

            # Mirror if requested
            if mirror_curve:
                midpoint = len(curve) // 2
                curve[midpoint:] = curve[midpoint - 1::-1][:len(curve[midpoint:])]

            # Blend with a second curve
            if blend_curve_type != "none" and blend_amount > 0:
                blend_curve = self.calculate_curve(t, blend_curve_type, curve_param, custom_formula)
                curve = curve * (1 - blend_amount) + blend_curve * blend_amount

            # Invert if requested
            if invert_curve:
                curve = 1 - curve

            # Safety for NaNs
            if np.any(np.isnan(curve)):
                print("[ERROR] NaN in curve, using linear")
                curve = np.linspace(0, 1, actual_keyframes)

            # Strength sampling
            if curve_type in ["bell_curve", "reverse_bell", "sine_wave"] and abs(start_strength - end_strength) < 0.01:
                # Center around start_strength
                curve_min = np.min(curve)
                curve_max = np.max(curve)
                if curve_max > curve_min:
                    normalized = (curve - curve_min) / (curve_max - curve_min) - 0.5
                    strengths = start_strength + normalized * start_strength * 2
                else:
                    strengths = np.full_like(curve, start_strength)
            else:
                # Simple interpolation
                strengths = start_strength + (end_strength - start_strength) * curve

            if clamp_strengths:
                strengths = np.clip(strengths, 0.0, 10.0)

            # Percent positions
            percents = np.linspace(start_percent, end_percent, actual_keyframes)

            # Adaptive redistribution
            if adaptive_keyframes and actual_keyframes > 2:
                percents, strengths = self.apply_adaptive_keyframes(percents, strengths, actual_keyframes)

            # Prepare output group
            if prev_timestep_kf is not None:
                keyframe_group = prev_timestep_kf
            else:
                keyframe_group = TimestepKeyframeGroup()

            # Build keyframes
            for i, (percent, strength) in enumerate(zip(percents, strengths)):
                guarantee_steps = 1 if i == 0 else 0

                keyframe = TimestepKeyframe(
                    start_percent=float(percent),
                    strength=float(strength),
                    guarantee_steps=guarantee_steps
                )

                # Assign batch image index when provided
                if batch_images is not None:
                    batch_size = getattr(batch_images, "shape", [0])[0] if hasattr(batch_images, "shape") else 0
                    if i < batch_size:
                        index_set = False

                        # Method 1: latent_keyframe attribute
                        try:
                            keyframe.latent_keyframe = i
                            index_set = True
                        except Exception:
                            pass

                        # Method 2: latent_keyframe_index attribute
                        if not index_set:
                            try:
                                keyframe.latent_keyframe_index = i
                                index_set = True
                            except Exception:
                                pass

                        # Method 3: batch_index attribute
                        if not index_set:
                            try:
                                keyframe.batch_index = i
                                index_set = True
                            except Exception:
                                pass

                        # Method 4: via control_weights
                        if not index_set:
                            try:
                                if not hasattr(keyframe, "control_weights") or keyframe.control_weights is None:
                                    keyframe.control_weights = ControlWeights()
                                keyframe.control_weights.latent_keyframe_index = i
                                index_set = True
                            except Exception:
                                pass

                        # Final fallback: setattr attempt
                        if not index_set:
                            try:
                                setattr(keyframe, "latent_keyframe", i)
                            except Exception:
                                pass

                keyframe_group.add(keyframe)

                if print_keyframes:
                    img_idx = getattr(keyframe, "latent_keyframe", getattr(keyframe, "latent_keyframe_index", "N/A"))
                    print(f"[Advanced Curved] KF {i}: {percent:.4f}, {strength:.4f}, img_index={img_idx}")

            # Stats
            stats = self.calculate_statistics(percents, strengths)

            # Add batch info to stats
            if batch_images is not None:
                batch_size = getattr(batch_images, "shape", [0])[0] if hasattr(batch_images, "shape") else 0
                stats += f"\nBatch Images: {batch_size} images indexed to keyframes"
                if batch_size != len(percents):
                    stats += f" ⚠ WARNING: Batch size ({batch_size}) != num_keyframes ({len(percents)})"

            # Optional CSV export
            if save_curve:
                self.save_curve_to_csv(percents, strengths, curve_filename)

            # Graph
            graph_image = None
            if show_graph:
                try:
                    comparison_data = None
                    if comparison_curve != "none":
                        comp_curve = self.calculate_curve(t, comparison_curve, curve_param, custom_formula)
                        comp_strengths = start_strength + (end_strength - start_strength) * comp_curve
                        comparison_data = (percents, comp_strengths, comparison_curve)

                    graph_image = self.generate_graph(
                        percents, strengths, curve_type, curve_param,
                        start_percent, end_percent, start_strength, end_strength,
                        comparison_data
                    )
                except Exception as e:
                    print(f"[Advanced Curved] Graph failed: {e}")
                    graph_image = None

            if graph_image is None:
                graph_image = self.create_dummy_image()

            return (keyframe_group, graph_image, stats)

        except Exception as e:
            print(f"[Advanced Curved] ERROR: {e}")
            import traceback
            traceback.print_exc()

            if prev_timestep_kf is not None:
                keyframe_group = prev_timestep_kf
            else:
                try:
                    keyframe_group = TimestepKeyframeGroup()
                except Exception:
                    keyframe_group = None

            dummy_image = self.create_dummy_image()
            error_stats = f"Error: {str(e)}"
            return (keyframe_group, dummy_image, error_stats)

    def generate_graph(
        self, percents, strengths, curve_type, curve_param,
        start_percent, end_percent, start_strength, end_strength,
        comparison_data=None
    ):
        """Generate a matplotlib graph showing the curve"""

        fig = None
        try:
            if len(percents) == 0 or len(strengths) == 0:
                return self.create_dummy_image()

            percents = np.asarray(percents)
            strengths = np.asarray(strengths)

            if np.any(np.isnan(percents)) or np.any(np.isnan(strengths)):
                return self.create_dummy_image()

            if np.any(np.isinf(percents)) or np.any(np.isinf(strengths)):
                return self.create_dummy_image()

            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

            ax.plot(percents * 100, strengths, 'b-', linewidth=2.5, label='Primary', alpha=0.8)
            ax.scatter(percents * 100, strengths, c='red', s=50, zorder=5, label='Keyframes')

            if comparison_data is not None:
                comp_percents, comp_strengths, comp_name = comparison_data
                ax.plot(comp_percents * 100, comp_strengths, 'g--', linewidth=2, label=f'Compare: {comp_name}', alpha=0.6)

            ax.set_xlabel('Generation Progress (%)', fontsize=12, fontweight='bold')
            ax.set_ylabel('ControlNet Strength', fontsize=12, fontweight='bold')
            ax.set_title(f'{curve_type} (param={curve_param:.2f})', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='best', fontsize=10)

            ax.set_xlim(start_percent * 100 - 5, end_percent * 100 + 5)

            all_strengths = list(strengths)
            if comparison_data:
                all_strengths.extend(comparison_data[1])

            y_min = min(0, min(all_strengths) - 0.1)
            y_max = max(all_strengths) + 0.1
            ax.set_ylim(y_min, y_max)

            info_text = f'Range: {start_percent:.2f}->{end_percent:.2f}\n'
            info_text += f'Strength: {start_strength:.2f}->{end_strength:.2f}\n'
            info_text += f'Keyframes: {len(percents)}'
            ax.text(
                0.02, 0.98, info_text, transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                fontsize=10
            )

            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img = Image.open(buf)
            plt.close(fig)
            fig = None

            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]

            return img_tensor

        except Exception as e:
            print(f"[Advanced Curved] Graph failed: {e}")
            return self.create_dummy_image()
        finally:
            if fig is not None:
                plt.close(fig)
            plt.close('all')

    def create_dummy_image(self):
        """Create dummy image when graph generation fails"""
        try:
            img_array = np.zeros((64, 64, 3), dtype=np.float32)
            img_tensor = torch.from_numpy(img_array)[None,]
            return img_tensor
        except Exception:
            return torch.zeros((1, 64, 64, 3), dtype=torch.float32)


NODE_CLASS_MAPPINGS = {
    "Advanced Curved ControlNet Scheduler": AdvancedCurvedControlNetScheduler
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Advanced Curved ControlNet Scheduler": "Advanced Curved ControlNet Scheduler"
}
