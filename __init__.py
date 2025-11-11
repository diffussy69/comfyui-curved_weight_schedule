# __init__.py — robust optional imports for ComfyUI custom nodes

import os
import sys
from importlib import import_module
import importlib.util

def _safe_import(module_name: str, pretty_name: str):
    """
    Try to import a sibling module and get its NODE_* mappings.
    1) Attempt as a package-relative import.
    2) Fallback: load by file path next to this __init__.py.
    """
    # 1) Try package-style relative import
    try:
        mod = import_module(f".{module_name}", package=__name__)
        return getattr(mod, "NODE_CLASS_MAPPINGS", {}), getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
    except Exception as e_pkg:
        # 2) Fallback: direct path import
        try:
            base_dir = os.path.dirname(__file__)
            py_path = os.path.join(base_dir, f"{module_name}.py")
            if not os.path.exists(py_path):
                raise FileNotFoundError(f"Missing file: {py_path}")

            spec = importlib.util.spec_from_file_location(f"{__name__}.{module_name}", py_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create spec for {py_path}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)

            return getattr(mod, "NODE_CLASS_MAPPINGS", {}), getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
        except Exception as e_path:
            print(f"[curved_weight_schedule] Optional node '{pretty_name}' not loaded: {e_pkg} | fallback: {e_path}")
            return {}, {}

# ---- Optional modules (won’t break if missing) ----
controlnet_scheduler_mappings, controlnet_scheduler_display = _safe_import(
    "curved_controlnet_scheduler", "curved_controlnet_scheduler"
)
advanced_controlnet_scheduler_mappings, advanced_controlnet_scheduler_display = _safe_import(
    "advanced_curved_controlnet_scheduler", "advanced_curved_controlnet_scheduler"
)
combiner_mappings, combiner_display = _safe_import(
    "multi_mask_combiner", "multi_mask_combiner"
)
regional_mappings, regional_display = _safe_import(
    "regional_prompting", "regional_prompting"
)
symmetry_mappings, symmetry_display = _safe_import(
    "mask_symmetry_tool", "mask_symmetry_tool"
)
interpolation_mappings, interpolation_display = _safe_import(
    "regional_prompt_interpolation", "regional_prompt_interpolation"
)
auto_mask_mappings, auto_mask_display = _safe_import(
    "auto_mask", "auto_mask"
)
formula_builder_mappings, formula_builder_display = _safe_import(
    "curve_formula_builder", "curve_formula_builder"
)
interactive_designer_mappings, interactive_designer_display = _safe_import(
    "interactive_curve_designer", "interactive_curve_designer"
)
dynamic_tile_mappings, dynamic_tile_display = _safe_import(
    "dynamic_tile_preprocessor", "dynamic_tile_preprocessor"
)
batch_to_timestep_mappings, batch_to_timestep_display = _safe_import(
    "batch_to_timestep_keyframes", "batch_to_timestep_keyframes"
)
# New curved tile blur node
curved_tile_mappings, curved_tile_display = _safe_import(
    "curved_tile_preprocessor", "curved_tile_preprocessor"
)

# ---- Merge whatever loaded ----
NODE_CLASS_MAPPINGS = {
    **controlnet_scheduler_mappings,
    **advanced_controlnet_scheduler_mappings,
    **combiner_mappings,
    **regional_mappings,
    **symmetry_mappings,
    **interpolation_mappings,
    **auto_mask_mappings,
    **formula_builder_mappings,
    **interactive_designer_mappings,
    **dynamic_tile_mappings,
    **batch_to_timestep_mappings,
    **curved_tile_mappings,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **controlnet_scheduler_display,
    **advanced_controlnet_scheduler_display,
    **combiner_display,
    **regional_display,
    **symmetry_display,
    **interpolation_display,
    **auto_mask_display,
    **formula_builder_display,
    **interactive_designer_display,
    **dynamic_tile_display,
    **batch_to_timestep_display,
    **curved_tile_display,
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
WEB_DIRECTORY = "./web"
