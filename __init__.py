# __init__.py — comfyui-curved_weight_schedule unified node init

import os
import sys
from importlib import import_module
import importlib.util

def _safe_import(module_name: str, pretty_name: str = None):
    """Try to import sibling node modules safely."""
    pretty_name = pretty_name or module_name
    try:
        mod = import_module(f".{module_name}", package=__name__)
        return getattr(mod, "NODE_CLASS_MAPPINGS", {}), getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", {})
    except Exception as e_pkg:
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

# ---- Load all node modules ----
NODE_MODULES = [
    "curved_controlnet_scheduler",
    "advanced_curved_controlnet_scheduler",
    "multi_mask_combiner",
    "regional_prompting",
    "mask_symmetry_tool",
    "regional_prompt_interpolation",
    "auto_mask",
    "curve_formula_builder",
    "interactive_curve_designer",
    "batch_to_timestep_keyframes",
    "curved_tile_preprocessor",
    "multi_layer_mask_editor",
    "multi_controlnet_curve_coordinator",
]

# Initialize mappings
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Load and merge all modules
for module_name in NODE_MODULES:
    class_mappings, display_mappings = _safe_import(module_name)
    NODE_CLASS_MAPPINGS.update(class_mappings)
    NODE_DISPLAY_NAME_MAPPINGS.update(display_mappings)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# ---- Serve JavaScript files from web directory ----
WEB_DIRECTORY = "./web"

print(f"[curved_weight_schedule] Loaded {len(NODE_CLASS_MAPPINGS)} nodes")