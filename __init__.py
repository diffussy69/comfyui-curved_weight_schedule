from .curved_controlnet_scheduler import NODE_CLASS_MAPPINGS as controlnet_scheduler_mappings, NODE_DISPLAY_NAME_MAPPINGS as controlnet_scheduler_display
from .advanced_curved_controlnet_scheduler import NODE_CLASS_MAPPINGS as advanced_controlnet_scheduler_mappings, NODE_DISPLAY_NAME_MAPPINGS as advanced_controlnet_scheduler_display
from .multi_mask_combiner import NODE_CLASS_MAPPINGS as combiner_mappings, NODE_DISPLAY_NAME_MAPPINGS as combiner_display
from .regional_prompting import NODE_CLASS_MAPPINGS as regional_mappings, NODE_DISPLAY_NAME_MAPPINGS as regional_display
from .mask_symmetry_tool import NODE_CLASS_MAPPINGS as symmetry_mappings, NODE_DISPLAY_NAME_MAPPINGS as symmetry_display
from .regional_prompt_interpolation import NODE_CLASS_MAPPINGS as interpolation_mappings, NODE_DISPLAY_NAME_MAPPINGS as interpolation_display
from .auto_mask import NODE_CLASS_MAPPINGS as auto_mask_mappings, NODE_DISPLAY_NAME_MAPPINGS as auto_mask_display
from .curve_formula_builder import NODE_CLASS_MAPPINGS as formula_builder_mappings, NODE_DISPLAY_NAME_MAPPINGS as formula_builder_display
from .interactive_curve_designer import NODE_CLASS_MAPPINGS as interactive_designer_mappings, NODE_DISPLAY_NAME_MAPPINGS as interactive_designer_display

NODE_CLASS_MAPPINGS = {
    **controlnet_scheduler_mappings, 
    **advanced_controlnet_scheduler_mappings,
    **combiner_mappings, 
    **regional_mappings, 
    **symmetry_mappings, 
    **interpolation_mappings,
    **auto_mask_mappings,
    **formula_builder_mappings,
    **interactive_designer_mappings
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
    **interactive_designer_display
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
WEB_DIRECTORY = "./web"