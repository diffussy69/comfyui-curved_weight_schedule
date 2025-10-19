import torch
import numpy as np

class MultiMaskStrengthCombiner:
    """
    Combines multiple separate masks with different strength multipliers.
    Each mask can have its own ControlNet strength, making it easy to control
    different regions independently.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Base strength multiplier applied to all masks"
                }),
            },
            "optional": {
                "mask_1": ("MASK",),
                "mask_1_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Strength multiplier for mask 1"
                }),
                "mask_2": ("MASK",),
                "mask_2_strength": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Strength multiplier for mask 2"
                }),
                "mask_3": ("MASK",),
                "mask_3_strength": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Strength multiplier for mask 3"
                }),
                "mask_4": ("MASK",),
                "mask_4_strength": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Strength multiplier for mask 4"
                }),
                "mask_5": ("MASK",),
                "mask_5_strength": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.01,
                    "tooltip": "Strength multiplier for mask 5"
                }),
                "blend_mode": (["max", "add", "multiply", "average"],),
                "normalize_output": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Clamp output to [0,1] range"
                }),
                "show_debug": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print debug information"
                }),
            }
        }
    
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("combined_mask",)
    FUNCTION = "combine_masks"
    CATEGORY = "mask"
    
    def combine_masks(self, base_strength, mask_1=None, mask_1_strength=1.0,
                     mask_2=None, mask_2_strength=0.7, mask_3=None, mask_3_strength=0.5,
                     mask_4=None, mask_4_strength=0.3, mask_5=None, mask_5_strength=0.2,
                     blend_mode="max", normalize_output=True, show_debug=False):
        """Combine multiple masks with different strength multipliers"""
        
        # Collect all provided masks and their strengths
        masks_data = [
            (mask_1, mask_1_strength),
            (mask_2, mask_2_strength),
            (mask_3, mask_3_strength),
            (mask_4, mask_4_strength),
            (mask_5, mask_5_strength),
        ]
        
        # Filter out None masks
        active_masks = [(m, s) for m, s in masks_data if m is not None]
        
        if len(active_masks) == 0:
            raise ValueError("At least one mask must be provided")
        
        if show_debug:
            print(f"[Multi-Mask Combiner] Combining {len(active_masks)} masks")
            print(f"[Multi-Mask Combiner] Base strength: {base_strength}")
            print(f"[Multi-Mask Combiner] Blend mode: {blend_mode}")
        
        # Get the shape from the first mask
        first_mask = active_masks[0][0]
        if len(first_mask.shape) == 2:
            first_mask = first_mask.unsqueeze(0)
        
        batch_size, height, width = first_mask.shape
        
        if show_debug:
            print(f"[Multi-Mask Combiner] Output shape: {first_mask.shape}")
        
        # Initialize output mask
        if blend_mode == "max":
            output_mask = torch.zeros_like(first_mask)
        elif blend_mode == "add":
            output_mask = torch.zeros_like(first_mask)
        elif blend_mode == "multiply":
            output_mask = torch.ones_like(first_mask)
        elif blend_mode == "average":
            output_mask = torch.zeros_like(first_mask)
        
        # Process each mask
        for i, (mask, strength) in enumerate(active_masks):
            # Ensure mask has correct shape
            if len(mask.shape) == 2:
                mask = mask.unsqueeze(0)
            
            # Resize if dimensions don't match
            if mask.shape != first_mask.shape:
                if show_debug:
                    print(f"[Multi-Mask Combiner] Warning: Mask {i+1} shape {mask.shape} doesn't match, resizing")
                # Simple nearest neighbor resize
                mask = torch.nn.functional.interpolate(
                    mask.unsqueeze(1), 
                    size=(height, width), 
                    mode='nearest'
                ).squeeze(1)
            
            # Apply strength multiplier and base strength
            weighted_mask = mask * strength * base_strength
            
            if show_debug:
                mask_pixels = (mask > 0.01).sum().item()
                print(f"[Multi-Mask Combiner] Mask {i+1}: {mask_pixels} pixels, "
                      f"strength={strength:.2f}, range=[{weighted_mask.min():.3f}, {weighted_mask.max():.3f}]")
            
            # Combine based on blend mode
            if blend_mode == "max":
                output_mask = torch.maximum(output_mask, weighted_mask)
            elif blend_mode == "add":
                output_mask = output_mask + weighted_mask
            elif blend_mode == "multiply":
                # For multiply, use the weighted mask as a multiplier
                # Convert to (1 - (1-mask) * strength) to preserve multiplication behavior
                output_mask = output_mask * (1 - (1 - mask) * strength * base_strength)
            elif blend_mode == "average":
                output_mask = output_mask + weighted_mask
        
        # Finalize average mode
        if blend_mode == "average":
            output_mask = output_mask / len(active_masks)
        
        # Normalize/clamp output
        if normalize_output:
            output_mask = torch.clamp(output_mask, 0.0, 1.0)
        
        if show_debug:
            print(f"[Multi-Mask Combiner] Output range: [{output_mask.min():.3f}, {output_mask.max():.3f}]")
            total_pixels = (output_mask > 0.01).sum().item()
            print(f"[Multi-Mask Combiner] Total active pixels: {total_pixels}")
        
        return (output_mask,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "MultiMaskStrengthCombiner": MultiMaskStrengthCombiner
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiMaskStrengthCombiner": "Multi-Mask Strength Combiner"
}