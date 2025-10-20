from .curved_weight_node import NODE_CLASS_MAPPINGS as curved_mappings, NODE_DISPLAY_NAME_MAPPINGS as curved_display
from .multi_mask_combiner import NODE_CLASS_MAPPINGS as combiner_mappings, NODE_DISPLAY_NAME_MAPPINGS as combiner_display
from .regional_prompting import NODE_CLASS_MAPPINGS as regional_mappings, NODE_DISPLAY_NAME_MAPPINGS as regional_display
from .mask_symmetry_tool import NODE_CLASS_MAPPINGS as symmetry_mappings, NODE_DISPLAY_NAME_MAPPINGS as symmetry_display
from .regional_prompt_interpolation import NODE_CLASS_MAPPINGS as interpolation_mappings, NODE_DISPLAY_NAME_MAPPINGS as interpolation_display

NODE_CLASS_MAPPINGS = {**curved_mappings, **combiner_mappings, **regional_mappings, **symmetry_mappings, **interpolation_mappings}
NODE_DISPLAY_NAME_MAPPINGS = {**curved_display, **combiner_display, **regional_display, **symmetry_display, **interpolation_display}