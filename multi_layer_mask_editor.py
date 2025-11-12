import torch
import numpy as np
from PIL import Image
import folder_paths
import os
import json

class MultiLayerMaskEditor:
    """
    A node that allows editing multiple mask layers on a single image.
    Each layer outputs as a separate mask that can be connected to different inputs.
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "output"
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "image": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "num_layers": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "display": "number"
                }),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "masks_data": "STRING",
            }
        }
    
    RETURN_TYPES = tuple(["MASK"] * 10)  # Maximum 10 mask outputs
    RETURN_NAMES = tuple([f"mask_{i+1}" for i in range(10)])
    FUNCTION = "process_masks"
    CATEGORY = "mask/edit"
    OUTPUT_NODE = True

    def process_masks(self, num_layers=5, image=None, unique_id=None, extra_pnginfo=None, masks_data=None):
        """
        Process the mask data from the frontend and return separate mask tensors
        """
        # Get image dimensions from the loaded image in the widget
        # The image parameter contains the filename
        if image and image.strip():
            # Load the image to get dimensions
            import os
            from PIL import Image as PILImage
            
            # Try to load from input directory
            input_dir = folder_paths.get_input_directory()
            image_path = os.path.join(input_dir, image)
            
            if os.path.exists(image_path):
                img = PILImage.open(image_path)
                width, height = img.size
            else:
                # Default dimensions if image not found
                print(f"[MultiLayerMaskEditor] Image not found: {image_path}, using default 512x512")
                width, height = 512, 512
        else:
            # No image specified, use default dimensions
            width, height = 512, 512
        
        # Initialize empty masks
        masks = []
        
        if masks_data:
            try:
                # Parse the JSON data from the frontend
                # Check if masks_data is a filename or JSON data
                if masks_data.endswith(".json"):
                    # Load from temp file
                    temp_dir = folder_paths.get_temp_directory()
                    mask_file = os.path.join(temp_dir, "masks", masks_data)
                    
                    if os.path.exists(mask_file):
                        with open(mask_file, "r") as f:
                            layers_info = json.load(f)
                        print(f"[MultiLayerMaskEditor] Loaded masks from: {mask_file}")
                    else:
                        print(f"[MultiLayerMaskEditor] File not found: {mask_file}")
                        layers_info = {}
                else:
                    layers_info = json.loads(masks_data)
                
                for layer_idx in range(num_layers):
                    layer_key = f"layer_{layer_idx}"
                    
                    if layer_key in layers_info and layers_info[layer_key]:
                        mask_data = layers_info[layer_key]
                        
                        # Check if it's the new base64 format (dict with 'data', 'width', 'height')
                        if isinstance(mask_data, dict) and 'data' in mask_data:
                            import base64
                            
                            # Decode base64 string
                            base64_data = mask_data['data']
                            mask_width = mask_data['width']
                            mask_height = mask_data['height']
                            
                            # Decode base64 to bytes
                            decoded_bytes = base64.b64decode(base64_data)
                            
                            # Convert to numpy array
                            mask_array = np.frombuffer(decoded_bytes, dtype=np.uint8).reshape(mask_height, mask_width).copy()
                            
                            # Verify dimensions match (they should always match since we load the same image)
                            if mask_height != height or mask_width != width:
                                print(f"[MultiLayerMaskEditor] WARNING: Mask dimensions ({mask_width}x{mask_height}) don't match image ({width}x{height})")
                                print(f"[MultiLayerMaskEditor] This shouldn't happen - masks are created at full resolution")
                                # Create empty mask instead of resizing
                                mask_tensor = torch.zeros((height, width), dtype=torch.float32)
                            else:
                                # Normalize to 0-1 range
                                mask_tensor = torch.from_numpy(mask_array).float() / 255.0
                        
                        # Legacy format: list of values
                        elif isinstance(mask_data, list):
                            mask_array = np.array(mask_data, dtype=np.uint8).reshape(height, width)
                            mask_tensor = torch.from_numpy(mask_array).float() / 255.0
                        else:
                            # Empty mask
                            mask_tensor = torch.zeros((height, width), dtype=torch.float32)
                    else:
                        # Empty mask for this layer
                        mask_tensor = torch.zeros((height, width), dtype=torch.float32)
                    
                    masks.append(mask_tensor)
                    
            except json.JSONDecodeError as e:
                print(f"[MultiLayerMaskEditor] JSON decode error: {e}")
                # If parsing fails, create empty masks
                masks = [torch.zeros((height, width), dtype=torch.float32) for _ in range(num_layers)]
            except Exception as e:
                print(f"[MultiLayerMaskEditor] Error processing masks: {e}")
                import traceback
                traceback.print_exc()
                masks = [torch.zeros((height, width), dtype=torch.float32) for _ in range(num_layers)]
        else:
            # No mask data provided, return empty masks
            masks = [torch.zeros((height, width), dtype=torch.float32) for _ in range(num_layers)]
        
        # Pad the output to 10 masks (fill with empty masks if fewer layers)
        while len(masks) < 10:
            masks.append(torch.zeros((height, width), dtype=torch.float32))
        
        # Return as tuple (only first 10 even if more were created)
        return tuple(masks[:10])

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always re-execute when masks_data changes
        return float("nan")


class MultiLayerMaskEditorSimple:
    """
    Simplified version that outputs a specific number of masks based on num_layers
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "image": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "num_layers": ([3, 5, 10], {"default": 5}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "masks_data": "STRING",
            }
        }
    
    RETURN_TYPES = ("MASK", "MASK", "MASK", "MASK", "MASK")
    RETURN_NAMES = ("mask_1", "mask_2", "mask_3", "mask_4", "mask_5")
    FUNCTION = "process_masks"
    CATEGORY = "mask/edit"
    OUTPUT_NODE = True

    def process_masks(self, num_layers=5, image=None, unique_id=None, masks_data=None):
        """
        Process masks and return only the requested number
        """
        # Get image dimensions
        if image and image.strip():
            import os
            from PIL import Image as PILImage
            
            input_dir = folder_paths.get_input_directory()
            image_path = os.path.join(input_dir, image)
            
            if os.path.exists(image_path):
                img = PILImage.open(image_path)
                width, height = img.size
            else:
                print(f"[MultiLayerMaskEditorSimple] Image not found: {image_path}, using default 512x512")
                width, height = 512, 512
        else:
            width, height = 512, 512
        
        masks = []
        
        if masks_data:
            try:
                # Check if masks_data is a filename or JSON data
                if masks_data.endswith(".json"):
                    # Load from temp file
                    temp_dir = folder_paths.get_temp_directory()
                    mask_file = os.path.join(temp_dir, "masks", masks_data)
                    
                    if os.path.exists(mask_file):
                        with open(mask_file, "r") as f:
                            layers_info = json.load(f)
                        print(f"[MultiLayerMaskEditorSimple] Loaded masks from: {mask_file}")
                    else:
                        print(f"[MultiLayerMaskEditorSimple] File not found: {mask_file}")
                        layers_info = {}
                else:
                    layers_info = json.loads(masks_data)
                
                for layer_idx in range(5):  # Always process up to 5
                    layer_key = f"layer_{layer_idx}"
                    
                    if layer_key in layers_info and layers_info[layer_key]:
                        mask_data = layers_info[layer_key]
                        
                        # Check if it's the new base64 format
                        if isinstance(mask_data, dict) and 'data' in mask_data:
                            import base64
                            
                            base64_data = mask_data['data']
                            mask_width = mask_data['width']
                            mask_height = mask_data['height']
                            
                            decoded_bytes = base64.b64decode(base64_data)
                            mask_array = np.frombuffer(decoded_bytes, dtype=np.uint8).reshape(mask_height, mask_width).copy()
                            
                            # Verify dimensions match
                            if mask_height != height or mask_width != width:
                                print(f"[MultiLayerMaskEditorSimple] WARNING: Mask dimensions ({mask_width}x{mask_height}) don't match image ({width}x{height})")
                                mask_tensor = torch.zeros((height, width), dtype=torch.float32)
                            else:
                                mask_tensor = torch.from_numpy(mask_array).float() / 255.0
                        
                        # Legacy format
                        elif isinstance(mask_data, list):
                            mask_array = np.array(mask_data, dtype=np.uint8).reshape(height, width)
                            mask_tensor = torch.from_numpy(mask_array).float() / 255.0
                        else:
                            mask_tensor = torch.zeros((height, width), dtype=torch.float32)
                    else:
                        mask_tensor = torch.zeros((height, width), dtype=torch.float32)
                    
                    masks.append(mask_tensor)
                    
            except Exception as e:
                print(f"[MultiLayerMaskEditorSimple] Error processing masks: {e}")
                import traceback
                traceback.print_exc()
                masks = [torch.zeros((height, width), dtype=torch.float32) for _ in range(5)]
        else:
            masks = [torch.zeros((height, width), dtype=torch.float32) for _ in range(5)]
        
        return tuple(masks)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")


# Node registration
NODE_CLASS_MAPPINGS = {
    "MultiLayerMaskEditor": MultiLayerMaskEditor,
    "MultiLayerMaskEditorSimple": MultiLayerMaskEditorSimple,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiLayerMaskEditor": "Multi-Layer Mask Editor (10 outputs)",
    "MultiLayerMaskEditorSimple": "Multi-Layer Mask Editor (5 outputs)",
}