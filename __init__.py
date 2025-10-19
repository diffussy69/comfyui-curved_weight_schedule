from .curved_weight_node import NODE_CLASS_MAPPINGS as curved_mappings, NODE_DISPLAY_NAME_MAPPINGS as curved_display
from .multi_mask_combiner import NODE_CLASS_MAPPINGS as mask_mappings, NODE_DISPLAY_NAME_MAPPINGS as mask_display

NODE_CLASS_MAPPINGS = {**curved_mappings, **mask_mappings}
NODE_DISPLAY_NAME_MAPPINGS = {**curved_display, **mask_display}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']