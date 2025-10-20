import torch
import torch.nn.functional as F

class MaskSymmetryTool:
    """
    Mirror/flip masks across different axes for symmetrical compositions.
    Useful for portraits, architecture, and any symmetrical subjects.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK",),
                "symmetry_mode": ([
                    "none",
                    "horizontal",
                    "vertical", 
                    "both",
                    "diagonal_tl_br",  # top-left to bottom-right
                    "diagonal_tr_bl",  # top-right to bottom-left
                    "radial_4way",     # 4-way radial symmetry
                ],),
                "blend_mode": (["replace", "add", "max", "average"],),
                "blend_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "How strongly to blend mirrored mask with original"
                }),
            },
            "optional": {
                "invert_mirrored": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Invert the mirrored portion"
                }),
                "show_debug": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print debug information"
                }),
            }
        }
    
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("symmetrical_mask",)
    FUNCTION = "apply_symmetry"
    CATEGORY = "mask"
    
    def apply_symmetry(self, mask, symmetry_mode, blend_mode, blend_strength,
                      invert_mirrored=False, show_debug=False):
        """Apply symmetry/mirroring to a mask"""
        
        # Ensure mask has correct dimensions
        if len(mask.shape) == 2:
            mask = mask.unsqueeze(0)
        
        batch_size, height, width = mask.shape
        
        if show_debug:
            print(f"[Mask Symmetry] Input mask shape: {mask.shape}")
            print(f"[Mask Symmetry] Symmetry mode: {symmetry_mode}")
            print(f"[Mask Symmetry] Blend mode: {blend_mode}")
        
        if symmetry_mode == "none":
            return (mask,)
        
        # Create output mask starting with original
        output_mask = mask.clone()
        
        # Apply symmetry transformations
        if symmetry_mode == "horizontal":
            mirrored = torch.flip(mask, dims=[2])  # flip width
            output_mask = self.blend_masks(output_mask, mirrored, blend_mode, blend_strength, invert_mirrored)
        
        elif symmetry_mode == "vertical":
            mirrored = torch.flip(mask, dims=[1])  # flip height
            output_mask = self.blend_masks(output_mask, mirrored, blend_mode, blend_strength, invert_mirrored)
        
        elif symmetry_mode == "both":
            mirrored_h = torch.flip(mask, dims=[2])
            mirrored_v = torch.flip(mask, dims=[1])
            mirrored_both = torch.flip(mask, dims=[1, 2])
            
            # Blend all versions
            output_mask = self.blend_masks(output_mask, mirrored_h, blend_mode, blend_strength, invert_mirrored)
            output_mask = self.blend_masks(output_mask, mirrored_v, blend_mode, blend_strength, invert_mirrored)
            output_mask = self.blend_masks(output_mask, mirrored_both, blend_mode, blend_strength, invert_mirrored)
        
        elif symmetry_mode == "diagonal_tl_br":
            # Transpose (flip along top-left to bottom-right diagonal)
            mirrored = mask.transpose(1, 2)
            # Resize if dimensions don't match
            if mirrored.shape != mask.shape:
                mirrored = F.interpolate(mirrored.unsqueeze(1), size=(height, width), mode='nearest').squeeze(1)
            output_mask = self.blend_masks(output_mask, mirrored, blend_mode, blend_strength, invert_mirrored)
        
        elif symmetry_mode == "diagonal_tr_bl":
            # Flip both axes then transpose (flip along top-right to bottom-left diagonal)
            mirrored = torch.flip(mask, dims=[1, 2]).transpose(1, 2)
            if mirrored.shape != mask.shape:
                mirrored = F.interpolate(mirrored.unsqueeze(1), size=(height, width), mode='nearest').squeeze(1)
            output_mask = self.blend_masks(output_mask, mirrored, blend_mode, blend_strength, invert_mirrored)
        
        elif symmetry_mode == "radial_4way":
            # Create 4-way radial symmetry (like a kaleidoscope)
            mirrored_h = torch.flip(mask, dims=[2])
            mirrored_v = torch.flip(mask, dims=[1])
            mirrored_both = torch.flip(mask, dims=[1, 2])
            
            # Split into quadrants and mirror
            h_mid = height // 2
            w_mid = width // 2
            
            # Top-left is original
            output_mask = mask.clone()
            
            # Top-right mirrors top-left horizontally
            output_mask[:, :h_mid, w_mid:] = torch.flip(mask[:, :h_mid, :w_mid], dims=[2])
            
            # Bottom-left mirrors top-left vertically
            output_mask[:, h_mid:, :w_mid] = torch.flip(mask[:, :h_mid, :w_mid], dims=[1])
            
            # Bottom-right mirrors top-left both ways
            output_mask[:, h_mid:, w_mid:] = torch.flip(mask[:, :h_mid, :w_mid], dims=[1, 2])
        
        # Clamp to valid range
        output_mask = torch.clamp(output_mask, 0.0, 1.0)
        
        if show_debug:
            print(f"[Mask Symmetry] Output mask range: [{output_mask.min():.3f}, {output_mask.max():.3f}]")
            active_pixels = (output_mask > 0.01).sum().item()
            print(f"[Mask Symmetry] Active pixels: {active_pixels}")
        
        return (output_mask,)
    
    
    def blend_masks(self, mask1, mask2, blend_mode, blend_strength, invert_mirrored):
        """Blend two masks together"""
        
        # Optionally invert the mirrored mask
        if invert_mirrored:
            mask2 = 1.0 - mask2
        
        # Apply blend strength to mask2
        mask2 = mask2 * blend_strength
        
        if blend_mode == "replace":
            # Where mask2 has values, use those
            return torch.where(mask2 > 0.01, mask2, mask1)
        
        elif blend_mode == "add":
            return mask1 + mask2
        
        elif blend_mode == "max":
            return torch.maximum(mask1, mask2)
        
        elif blend_mode == "average":
            return (mask1 + mask2) / 2.0
        
        return mask1


# Node registration
NODE_CLASS_MAPPINGS = {
    "MaskSymmetryTool": MaskSymmetryTool
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MaskSymmetryTool": "Mask Symmetry Tool"
}