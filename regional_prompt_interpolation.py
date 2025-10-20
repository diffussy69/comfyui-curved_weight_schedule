import torch
import numpy as np

class RegionalPromptInterpolation:
    """
    Smoothly interpolate between different prompts across regions.
    Creates gradient transitions between regional prompts.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "base_positive": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Base prompt applied everywhere"
                }),
                "interpolation_steps": ("INT", {
                    "default": 5,
                    "min": 2,
                    "max": 20,
                    "step": 1,
                    "tooltip": "Number of gradient steps between regions"
                }),
            },
            "optional": {
                "region_1_mask": ("MASK",),
                "region_1_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "region_1_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                }),
                
                "region_2_mask": ("MASK",),
                "region_2_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "region_2_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                }),
                
                "region_3_mask": ("MASK",),
                "region_3_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                }),
                "region_3_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                }),
                
                "transition_mode": (["linear", "smooth", "ease_in_out"],),
                "gradient_direction": (["auto", "left_to_right", "right_to_left", 
                                       "top_to_bottom", "bottom_to_top", "radial"],),
                "show_debug": ("BOOLEAN", {
                    "default": False,
                }),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING", "MASK",)
    RETURN_NAMES = ("conditioning", "interpolation_viz",)
    FUNCTION = "interpolate_prompts"
    CATEGORY = "conditioning"
    
    def interpolate_prompts(self, clip, base_positive, interpolation_steps,
                          region_1_mask=None, region_1_prompt="", region_1_strength=1.0,
                          region_2_mask=None, region_2_prompt="", region_2_strength=1.0,
                          region_3_mask=None, region_3_prompt="", region_3_strength=1.0,
                          transition_mode="smooth", gradient_direction="auto",
                          show_debug=False):
        """Create smoothly interpolated regional conditioning"""
        
        # Collect active regions
        regions = []
        if region_1_mask is not None and region_1_prompt.strip():
            regions.append((region_1_mask, region_1_prompt, region_1_strength, "Region 1"))
        if region_2_mask is not None and region_2_prompt.strip():
            regions.append((region_2_mask, region_2_prompt, region_2_strength, "Region 2"))
        if region_3_mask is not None and region_3_prompt.strip():
            regions.append((region_3_mask, region_3_prompt, region_3_strength, "Region 3"))
        
        if len(regions) < 2:
            if show_debug:
                print("[Prompt Interpolation] Need at least 2 regions for interpolation")
            # Fall back to simple regional conditioning
            return self.simple_regional_conditioning(clip, base_positive, regions, show_debug)
        
        if show_debug:
            print(f"[Prompt Interpolation] Interpolating between {len(regions)} regions")
            print(f"[Prompt Interpolation] Steps: {interpolation_steps}")
            print(f"[Prompt Interpolation] Transition: {transition_mode}")
        
        # Get reference dimensions from first mask
        first_mask = regions[0][0]
        if len(first_mask.shape) == 2:
            first_mask = first_mask.unsqueeze(0)
        batch_size, height, width = first_mask.shape
        
        # Create distance map for each region
        distance_maps = []
        for mask, prompt, strength, name in regions:
            if len(mask.shape) == 2:
                mask = mask.unsqueeze(0)
            
            # Resize if needed
            if mask.shape != first_mask.shape:
                mask = torch.nn.functional.interpolate(
                    mask.unsqueeze(1), size=(height, width), mode='bilinear'
                ).squeeze(1)
            
            distance_maps.append((mask, prompt, strength, name))
        
        # Generate interpolated regions
        conditioning_list = []
        
        # Start with base conditioning
        if base_positive.strip():
            tokens = clip.tokenize(base_positive)
            base_cond, base_pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            conditioning_list.append([base_cond, {"pooled_output": base_pooled}])
        
        # Create interpolation between each pair of regions
        for i in range(len(regions) - 1):
            mask1, prompt1, strength1, name1 = distance_maps[i]
            mask2, prompt2, strength2, name2 = distance_maps[i + 1]
            
            if show_debug:
                print(f"[Prompt Interpolation] Interpolating {name1} → {name2}")
            
            # Create interpolation steps
            for step in range(interpolation_steps):
                # Calculate interpolation factor
                t = step / (interpolation_steps - 1) if interpolation_steps > 1 else 0.5
                
                # Apply transition curve
                if transition_mode == "smooth":
                    # Smoothstep function
                    t = t * t * (3.0 - 2.0 * t)
                elif transition_mode == "ease_in_out":
                    # Ease in-out cubic
                    t = t * t * t * (t * (t * 6 - 15) + 10) if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
                # linear uses raw t
                
                # Interpolate prompts by blending embeddings
                tokens1 = clip.tokenize(prompt1)
                cond1, pooled1 = clip.encode_from_tokens(tokens1, return_pooled=True)
                
                tokens2 = clip.tokenize(prompt2)
                cond2, pooled2 = clip.encode_from_tokens(tokens2, return_pooled=True)
                
                # Blend embeddings
                blended_cond = cond1 * (1 - t) + cond2 * t
                blended_pooled = pooled1 * (1 - t) + pooled2 * t
                
                # Blend strengths
                blended_strength = strength1 * (1 - t) + strength2 * t
                
                # Create transition mask (where this interpolation applies)
                # This is the region between mask1 and mask2
                transition_mask = self.create_transition_mask(
                    mask1, mask2, t, gradient_direction, height, width
                )
                
                # Add to conditioning
                region_cond = [blended_cond, {
                    "pooled_output": blended_pooled,
                    "mask": transition_mask,
                    "set_area_to_bounds": False,
                    "mask_strength": blended_strength
                }]
                conditioning_list.append(region_cond)
        
        # Add the endpoint regions with full strength
        for mask, prompt, strength, name in regions:
            tokens = clip.tokenize(prompt)
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            
            region_cond = [cond, {
                "pooled_output": pooled,
                "mask": mask,
                "set_area_to_bounds": False,
                "mask_strength": strength
            }]
            conditioning_list.append(region_cond)
        
        # Create visualization of interpolation
        viz_mask = self.create_interpolation_visualization(distance_maps, height, width)
        
        if show_debug:
            print(f"[Prompt Interpolation] Generated {len(conditioning_list)} conditioning regions")
        
        return (conditioning_list, viz_mask,)
    
    
    def create_transition_mask(self, mask1, mask2, t, gradient_direction, height, width):
        """Create a mask for the transition zone between two regions"""
        
        if gradient_direction == "auto":
            # Auto-detect based on mask positions
            # Find center of mass for each mask
            mask1_np = mask1.cpu().numpy()[0]
            mask2_np = mask2.cpu().numpy()[0]
            
            y1, x1 = np.where(mask1_np > 0.5)
            y2, x2 = np.where(mask2_np > 0.5)
            
            if len(x1) > 0 and len(x2) > 0:
                center1 = (np.mean(x1), np.mean(y1))
                center2 = (np.mean(x2), np.mean(y2))
                
                # Determine predominant direction
                dx = center2[0] - center1[0]
                dy = center2[1] - center1[1]
                
                if abs(dx) > abs(dy):
                    gradient_direction = "left_to_right" if dx > 0 else "right_to_left"
                else:
                    gradient_direction = "top_to_bottom" if dy > 0 else "bottom_to_top"
        
        # Create gradient mask based on direction
        device = mask1.device
        
        if gradient_direction == "left_to_right":
            gradient = torch.linspace(0, 1, width, device=device).unsqueeze(0).unsqueeze(0)
            gradient = gradient.expand(1, height, width)
        
        elif gradient_direction == "right_to_left":
            gradient = torch.linspace(1, 0, width, device=device).unsqueeze(0).unsqueeze(0)
            gradient = gradient.expand(1, height, width)
        
        elif gradient_direction == "top_to_bottom":
            gradient = torch.linspace(0, 1, height, device=device).unsqueeze(0).unsqueeze(2)
            gradient = gradient.expand(1, height, width)
        
        elif gradient_direction == "bottom_to_top":
            gradient = torch.linspace(1, 0, height, device=device).unsqueeze(0).unsqueeze(2)
            gradient = gradient.expand(1, height, width)
        
        elif gradient_direction == "radial":
            # Create radial gradient from center
            y = torch.linspace(-1, 1, height, device=device).unsqueeze(1)
            x = torch.linspace(-1, 1, width, device=device).unsqueeze(0)
            gradient = torch.sqrt(x**2 + y**2).unsqueeze(0)
            gradient = gradient / gradient.max()  # Normalize to 0-1
        
        # Create transition mask - active in transition zone
        # Mask is strong where gradient matches current t value
        transition_mask = 1.0 - torch.abs(gradient - t)
        transition_mask = torch.clamp(transition_mask * 3, 0, 1)  # Sharpen
        
        # Combine with region masks to constrain to transition area
        region_mask = torch.maximum(mask1, mask2)
        transition_mask = transition_mask * region_mask
        
        return transition_mask
    
    
    def create_interpolation_visualization(self, regions, height, width):
        """Create a visualization showing interpolation zones"""
        
        viz = torch.zeros((1, height, width))
        
        for i, (mask, _, _, _) in enumerate(regions):
            # Color code each region differently
            color_value = (i + 1) / len(regions)
            viz = torch.maximum(viz, mask * color_value)
        
        return viz
    
    
    def simple_regional_conditioning(self, clip, base_positive, regions, show_debug):
        """Fallback for when interpolation isn't possible"""
        
        conditioning_list = []
        
        if base_positive.strip():
            tokens = clip.tokenize(base_positive)
            base_cond, base_pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            conditioning_list.append([base_cond, {"pooled_output": base_pooled}])
        
        for mask, prompt, strength, name in regions:
            tokens = clip.tokenize(prompt)
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            
            region_cond = [cond, {
                "pooled_output": pooled,
                "mask": mask,
                "set_area_to_bounds": False,
                "mask_strength": strength
            }]
            conditioning_list.append(region_cond)
        
        # Create simple viz
        if len(regions) > 0:
            first_mask = regions[0][0]
            if len(first_mask.shape) == 2:
                first_mask = first_mask.unsqueeze(0)
            viz = torch.zeros_like(first_mask)
        else:
            viz = torch.zeros((1, 64, 64))
        
        return (conditioning_list, viz,)


# Node registration
NODE_CLASS_MAPPINGS = {
    "RegionalPromptInterpolation": RegionalPromptInterpolation
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegionalPromptInterpolation": "Regional Prompt Interpolation"
}