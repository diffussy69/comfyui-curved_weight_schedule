import torch
import numpy as np
from PIL import Image

# Try to import rembg
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("[Auto Mask] Warning: rembg not installed. Install with: pip install rembg")


class AutoPersonMask:
    """
    Automatically detect and mask people/foreground objects using AI.
    Uses rembg (U2-Net) for accurate segmentation.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": (["u2net", "u2netp", "u2net_human_seg", "silueta"],),
            },
            "optional": {
                "alpha_matting": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Better edge quality but slower"
                }),
                "alpha_matting_foreground_threshold": ("INT", {
                    "default": 240,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "alpha_matting_background_threshold": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "alpha_matting_erode_size": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 50,
                    "step": 1
                }),
                "post_process_mask": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Clean up mask with morphological operations"
                }),
                "show_debug": ("BOOLEAN", {
                    "default": False,
                }),
            }
        }
    
    RETURN_TYPES = ("MASK", "IMAGE",)
    RETURN_NAMES = ("person_mask", "masked_image",)
    FUNCTION = "generate_mask"
    CATEGORY = "mask"
    
    def generate_mask(self, image, model, alpha_matting=False,
                     alpha_matting_foreground_threshold=240,
                     alpha_matting_background_threshold=10,
                     alpha_matting_erode_size=10,
                     post_process_mask=False, show_debug=False):
        """Generate person/foreground mask"""
        
        if not REMBG_AVAILABLE:
            raise Exception("rembg is not installed. Install with: pip install rembg")
        
        # Convert tensor to PIL
        if len(image.shape) == 4:
            image = image[0]
        
        i = 255. * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        if show_debug:
            print(f"[Auto Person Mask] Processing image: {img.size}")
            print(f"[Auto Person Mask] Model: {model}")
            print(f"[Auto Person Mask] Alpha matting: {alpha_matting}")
        
        # Remove background using rembg
        try:
            # Create session with model
            from rembg import new_session
            session = new_session(model)
            
            if alpha_matting:
                output = remove(
                    img,
                    session=session,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                    alpha_matting_erode_size=alpha_matting_erode_size
                )
            else:
                output = remove(img, session=session)
            
        except Exception as e:
            if show_debug:
                print(f"[Auto Person Mask] Error: {e}")
            raise Exception(f"Failed to generate mask: {str(e)}")
        
        # Extract alpha channel as mask
        if output.mode == 'RGBA':
            mask = output.split()[-1]
        else:
            # Fallback if no alpha channel
            mask = Image.new('L', output.size, 255)
        
        # Post-process mask if requested
        if post_process_mask:
            mask = self.clean_mask(mask, show_debug)
        
        # Convert mask to tensor
        mask_np = np.array(mask).astype(np.float32) / 255.0
        mask_tensor = torch.from_numpy(mask_np)
        
        # Convert masked image to tensor
        output_rgb = output.convert('RGB')
        output_np = np.array(output_rgb).astype(np.float32) / 255.0
        output_tensor = torch.from_numpy(output_np)[None,]
        
        if show_debug:
            mask_coverage = (mask_np > 0.5).sum() / mask_np.size
            print(f"[Auto Person Mask] Mask coverage: {mask_coverage*100:.1f}%")
        
        return (mask_tensor, output_tensor,)
    
    
    def clean_mask(self, mask, show_debug):
        """Clean up mask with morphological operations"""
        from PIL import ImageFilter, ImageOps
        
        # Convert to numpy for processing
        mask_np = np.array(mask)
        
        # Simple threshold to make binary
        threshold = 128
        mask_np = (mask_np > threshold).astype(np.uint8) * 255
        
        # Convert back to PIL
        mask_pil = Image.fromarray(mask_np)
        
        # Apply slight blur and re-threshold for smoother edges
        mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=1))
        
        if show_debug:
            print(f"[Auto Person Mask] Applied post-processing")
        
        return mask_pil


class AutoBackgroundMask:
    """
    Automatically generate background mask (inverted person mask).
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": (["u2net", "u2netp", "u2net_human_seg", "silueta"],),
            },
            "optional": {
                "alpha_matting": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Better edge quality but slower"
                }),
                "alpha_matting_foreground_threshold": ("INT", {
                    "default": 240,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "alpha_matting_background_threshold": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "alpha_matting_erode_size": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 50,
                    "step": 1
                }),
                "post_process_mask": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Clean up mask with morphological operations"
                }),
                "show_debug": ("BOOLEAN", {
                    "default": False,
                }),
            }
        }
    
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("background_mask",)
    FUNCTION = "generate_mask"
    CATEGORY = "mask"
    
    def generate_mask(self, image, model, alpha_matting=False,
                     alpha_matting_foreground_threshold=240,
                     alpha_matting_background_threshold=10,
                     alpha_matting_erode_size=10,
                     post_process_mask=False, show_debug=False):
        """Generate background mask (inverted person mask)"""
        
        if not REMBG_AVAILABLE:
            raise Exception("rembg is not installed. Install with: pip install rembg")
        
        # Convert tensor to PIL
        if len(image.shape) == 4:
            image = image[0]
        
        i = 255. * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        if show_debug:
            print(f"[Auto Background Mask] Processing image: {img.size}")
            print(f"[Auto Background Mask] Model: {model}")
        
        # Remove background using rembg
        try:
            # Create session with model
            from rembg import new_session
            session = new_session(model)
            
            if alpha_matting:
                output = remove(
                    img,
                    session=session,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                    alpha_matting_background_threshold=alpha_matting_background_threshold,
                    alpha_matting_erode_size=alpha_matting_erode_size
                )
            else:
                output = remove(img, session=session)
            
        except Exception as e:
            if show_debug:
                print(f"[Auto Background Mask] Error: {e}")
            raise Exception(f"Failed to generate mask: {str(e)}")
        
        # Extract alpha channel as mask
        if output.mode == 'RGBA':
            mask = output.split()[-1]
        else:
            mask = Image.new('L', output.size, 255)
        
        # INVERT the mask (person becomes black, background becomes white)
        from PIL import ImageOps
        mask = ImageOps.invert(mask)
        
        # Post-process mask if requested
        if post_process_mask:
            mask = self.clean_mask(mask, show_debug)
        
        # Convert mask to tensor
        mask_np = np.array(mask).astype(np.float32) / 255.0
        mask_tensor = torch.from_numpy(mask_np)
        
        if show_debug:
            mask_coverage = (mask_np > 0.5).sum() / mask_np.size
            print(f"[Auto Background Mask] Background coverage: {mask_coverage*100:.1f}%")
        
        return (mask_tensor,)
    
    
    def clean_mask(self, mask, show_debug):
        """Clean up mask with morphological operations"""
        from PIL import ImageFilter
        
        # Convert to numpy for processing
        mask_np = np.array(mask)
        
        # Simple threshold to make binary
        threshold = 128
        mask_np = (mask_np > threshold).astype(np.uint8) * 255
        
        # Convert back to PIL
        mask_pil = Image.fromarray(mask_np)
        
        # Apply slight blur and re-threshold for smoother edges
        mask_pil = mask_pil.filter(ImageFilter.GaussianBlur(radius=1))
        
        if show_debug:
            print(f"[Auto Background Mask] Applied post-processing")
        
        return mask_pil


# Node registration
NODE_CLASS_MAPPINGS = {
    "AutoPersonMask": AutoPersonMask,
    "AutoBackgroundMask": AutoBackgroundMask
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoPersonMask": "Auto Person Mask",
    "AutoBackgroundMask": "Auto Background Mask"
}