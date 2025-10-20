import torch

class RegionalPrompting:
    """
    All-in-one regional prompting node.
    Takes multiple masks and prompts, combines them into regional conditioning.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "base_positive": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Base positive prompt applied everywhere"
                }),
            },
            "optional": {
                "region_1_mask": ("MASK",),
                "region_1_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Positive prompt for region 1"
                }),
                "region_1_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Conditioning strength for region 1"
                }),
                
                "region_2_mask": ("MASK",),
                "region_2_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Positive prompt for region 2"
                }),
                "region_2_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Conditioning strength for region 2"
                }),
                
                "region_3_mask": ("MASK",),
                "region_3_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Positive prompt for region 3"
                }),
                "region_3_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Conditioning strength for region 3"
                }),
                
                "region_4_mask": ("MASK",),
                "region_4_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Positive prompt for region 4"
                }),
                "region_4_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Conditioning strength for region 4"
                }),
                
                "region_5_mask": ("MASK",),
                "region_5_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Positive prompt for region 5"
                }),
                "region_5_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "tooltip": "Conditioning strength for region 5"
                }),
                
                "show_debug": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Print debug information"
                }),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    FUNCTION = "create_regional_conditioning"
    CATEGORY = "conditioning"
    
    def create_regional_conditioning(self, clip, base_positive,
                                     region_1_mask=None, region_1_prompt="", region_1_strength=1.0,
                                     region_2_mask=None, region_2_prompt="", region_2_strength=1.0,
                                     region_3_mask=None, region_3_prompt="", region_3_strength=1.0,
                                     region_4_mask=None, region_4_prompt="", region_4_strength=1.0,
                                     region_5_mask=None, region_5_prompt="", region_5_strength=1.0,
                                     show_debug=False):
        """Create regional conditioning from multiple masked prompts"""
        
        # Collect all regions
        regions = [
            (region_1_mask, region_1_prompt, region_1_strength),
            (region_2_mask, region_2_prompt, region_2_strength),
            (region_3_mask, region_3_prompt, region_3_strength),
            (region_4_mask, region_4_prompt, region_4_strength),
            (region_5_mask, region_5_prompt, region_5_strength),
        ]
        
        # Filter out empty regions (no mask or no prompt)
        active_regions = [(m, p, s) for m, p, s in regions if m is not None and p.strip() != ""]
        
        if show_debug:
            print(f"[Regional Prompting] Base prompt: '{base_positive}'")
            print(f"[Regional Prompting] Active regions: {len(active_regions)}")
        
        # Start with base conditioning
        if base_positive.strip():
            tokens = clip.tokenize(base_positive)
            base_cond, base_pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            conditioning = [[base_cond, {"pooled_output": base_pooled}]]
        else:
            # Empty base conditioning
            conditioning = []
        
        # Add each regional conditioning
        for i, (mask, prompt, strength) in enumerate(active_regions):
            if show_debug:
                print(f"[Regional Prompting] Region {i+1}: '{prompt[:50]}...' strength={strength}")
            
            # Encode the prompt
            tokens = clip.tokenize(prompt)
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            
            # Prepare mask for conditioning
            if len(mask.shape) == 2:
                mask = mask.unsqueeze(0)
            
            # Create conditioning entry with mask
            region_cond = [cond, {
                "pooled_output": pooled,
                "mask": mask,
                "set_area_to_bounds": False,
                "mask_strength": strength
            }]
            
            # Add to conditioning list
            if len(conditioning) == 0:
                conditioning = [region_cond]
            else:
                # Combine with existing conditioning
                conditioning = self.combine_conditioning(conditioning, [region_cond])
            
            if show_debug:
                mask_pixels = (mask > 0.01).sum().item()
                print(f"[Regional Prompting] Region {i+1} mask: {mask_pixels} pixels")
        
        if len(conditioning) == 0:
            # No regions and no base prompt - return empty conditioning
            print("[Regional Prompting] Warning: No prompts provided, returning empty conditioning")
            tokens = clip.tokenize("")
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            conditioning = [[cond, {"pooled_output": pooled}]]
        
        return (conditioning,)
    
    
    def combine_conditioning(self, cond1, cond2):
        """Combine two conditioning lists"""
        # Simple concatenation - ComfyUI's sampler will handle the rest
        return cond1 + cond2


# Node registration
NODE_CLASS_MAPPINGS = {
    "RegionalPrompting": RegionalPrompting
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegionalPrompting": "Regional Prompting"
}