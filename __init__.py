from .curved_controlnet_scheduler import NODE_CLASS_MAPPINGS as controlnet_scheduler_mappings, NODE_DISPLAY_NAME_MAPPINGS as controlnet_scheduler_display
from .multi_mask_combiner import NODE_CLASS_MAPPINGS as combiner_mappings, NODE_DISPLAY_NAME_MAPPINGS as combiner_display
from .regional_prompting import NODE_CLASS_MAPPINGS as regional_mappings, NODE_DISPLAY_NAME_MAPPINGS as regional_display
from .mask_symmetry_tool import NODE_CLASS_MAPPINGS as symmetry_mappings, NODE_DISPLAY_NAME_MAPPINGS as symmetry_display
from .regional_prompt_interpolation import NODE_CLASS_MAPPINGS as interpolation_mappings, NODE_DISPLAY_NAME_MAPPINGS as interpolation_display
from .auto_mask import NODE_CLASS_MAPPINGS as auto_mask_mappings, NODE_DISPLAY_NAME_MAPPINGS as auto_mask_display

NODE_CLASS_MAPPINGS = {
    **controlnet_scheduler_mappings, 
    **combiner_mappings, 
    **regional_mappings, 
    **symmetry_mappings, 
    **interpolation_mappings,
    **auto_mask_mappings
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **controlnet_scheduler_display, 
    **combiner_display, 
    **regional_display, 
    **symmetry_display, 
    **interpolation_display,
    **auto_mask_display
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']