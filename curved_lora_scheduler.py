import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
from PIL import Image
import torch
import math

class CurvedLoRAScheduler:
    """
    Generates curved weight schedules for multiple LoRA models with independent control.
    Each LoRA can have its own curve, strength range, and active steps.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        lora_list = ["None"] + cls.get_lora_list()
        
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "num_steps": ("INT", {
                    "default": 20,
                    "min": 2,
                    "max": 1000,
                    "step": 1,
                    "tooltip": "Total number of sampling steps (should match your sampler)"
                }),
                
                # LoRA 1
                "lora_1_name": (lora_list,),
                "lora_1_start_step": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "lora_1_end_step": ("INT", {"default": 20, "min": 0, "max": 1000, "step": 1}),
                "lora_1_start_strength": ("FLOAT", {"default": 1.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                "lora_1_end_strength": ("FLOAT", {"default": 0.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                "lora_1_curve_type": (["linear", "ease_in", "ease_out", "ease_in_out", 
                                      "strong_to_weak", "weak_to_strong", "sine_wave", 
                                      "bell_curve", "reverse_bell", "exponential_up", 
                                      "exponential_down", "bounce", "custom_bezier"],),
                "lora_1_curve_param": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "lora_1_strength_clip": ("FLOAT", {"default": 1.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                
                # LoRA 2
                "lora_2_name": (lora_list,),
                "lora_2_start_step": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "lora_2_end_step": ("INT", {"default": 20, "min": 0, "max": 1000, "step": 1}),
                "lora_2_start_strength": ("FLOAT", {"default": 1.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                "lora_2_end_strength": ("FLOAT", {"default": 0.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                "lora_2_curve_type": (["linear", "ease_in", "ease_out", "ease_in_out", 
                                      "strong_to_weak", "weak_to_strong", "sine_wave", 
                                      "bell_curve", "reverse_bell", "exponential_up", 
                                      "exponential_down", "bounce", "custom_bezier"],),
                "lora_2_curve_param": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "lora_2_strength_clip": ("FLOAT", {"default": 1.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                
                # LoRA 3
                "lora_3_name": (lora_list,),
                "lora_3_start_step": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "lora_3_end_step": ("INT", {"default": 20, "min": 0, "max": 1000, "step": 1}),
                "lora_3_start_strength": ("FLOAT", {"default": 1.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                "lora_3_end_strength": ("FLOAT", {"default": 0.0, "min": -5.0, "max": 5.0, "step": 0.01}),
                "lora_3_curve_type": (["linear", "ease_in", "ease_out", "ease_in_out", 
                                      "strong_to_weak", "weak_to_strong", "sine_wave", 
                                      "bell_curve", "reverse_bell", "exponential_up", 
                                      "exponential_down", "bounce", "custom_bezier"],),
                "lora_3_curve_param": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "lora_3_strength_clip": ("FLOAT", {"default": 1.0, "min": -5.0, "max": 5.0, "step": 0.01}),
            },
            "optional": {
                "print_schedule": ("BOOLEAN", {"default": False, "tooltip": "Print weight schedules"}),
                "show_graph": ("BOOLEAN", {"default": True, "tooltip": "Generate visual graph"}),
            }
        }
    
    RETURN_TYPES = ("MODEL", "CLIP", "IMAGE",)
    RETURN_NAMES = ("MODEL", "CLIP", "curve_graph",)
    FUNCTION = "apply_lora_schedule"
    CATEGORY = "loaders"
    
    @classmethod
    def get_lora_list(cls):
        """Get list of available LoRA files"""
        import folder_paths
        return folder_paths.get_filename_list("loras")
    
    def generate_curve(self, t, curve_type, curve_param):
        """Generate normalized curve values (0 to 1)"""
        if curve_type == "strong_to_weak":
            return 1 - (t ** (1 / curve_param))
        elif curve_type == "weak_to_strong":
            return t ** (1 / curve_param)
        elif curve_type == "linear":
            return t
        elif curve_type == "ease_in":
            return t ** curve_param
        elif curve_type == "ease_out":
            return 1 - (1 - t) ** curve_param
        elif curve_type == "ease_in_out":
            return np.where(t < 0.5, 
                           2 ** (curve_param - 1) * t ** curve_param,
                           1 - (-2 * t + 2) ** curve_param / 2)
        elif curve_type == "sine_wave":
            return (np.sin(t * curve_param * 2 * np.pi) + 1) / 2
        elif curve_type == "bell_curve":
            return np.exp(-((t - 0.5) ** 2) / (2 * (0.15 / curve_param) ** 2))
        elif curve_type == "reverse_bell":
            bell = np.exp(-((t - 0.5) ** 2) / (2 * (0.15 / curve_param) ** 2))
            return 1 - bell
        elif curve_type == "exponential_up":
            return (np.exp(curve_param * t) - 1) / (np.exp(curve_param) - 1)
        elif curve_type == "exponential_down":
            return (np.exp(curve_param * (1 - t)) - 1) / (np.exp(curve_param) - 1)
        elif curve_type == "bounce":
            return np.abs(np.sin(t * curve_param * np.pi))
        elif curve_type == "custom_bezier":
            return 3 * (1 - t) ** 2 * t * curve_param / 10 + 3 * (1 - t) * t ** 2 * (1 - curve_param / 10) + t ** 3
        else:
            return t
    
    def apply_lora_schedule(self, model, clip, num_steps, 
                           lora_1_name, lora_1_start_step, lora_1_end_step, lora_1_start_strength, 
                           lora_1_end_strength, lora_1_curve_type, lora_1_curve_param, lora_1_strength_clip,
                           lora_2_name, lora_2_start_step, lora_2_end_step, lora_2_start_strength,
                           lora_2_end_strength, lora_2_curve_type, lora_2_curve_param, lora_2_strength_clip,
                           lora_3_name, lora_3_start_step, lora_3_end_step, lora_3_start_strength,
                           lora_3_end_strength, lora_3_curve_type, lora_3_curve_param, lora_3_strength_clip,
                           print_schedule=False, show_graph=True):
        """Apply multiple LoRAs with independent curved weight scheduling"""
        
        try:
            import folder_paths
            import comfy.utils
            import comfy.lora
            
            # Collect LoRA configurations
            lora_configs = [
                {
                    'name': lora_1_name,
                    'start_step': lora_1_start_step,
                    'end_step': lora_1_end_step,
                    'start_strength': lora_1_start_strength,
                    'end_strength': lora_1_end_strength,
                    'curve_type': lora_1_curve_type,
                    'curve_param': lora_1_curve_param,
                    'strength_clip': lora_1_strength_clip,
                    'index': 1
                },
                {
                    'name': lora_2_name,
                    'start_step': lora_2_start_step,
                    'end_step': lora_2_end_step,
                    'start_strength': lora_2_start_strength,
                    'end_strength': lora_2_end_strength,
                    'curve_type': lora_2_curve_type,
                    'curve_param': lora_2_curve_param,
                    'strength_clip': lora_2_strength_clip,
                    'index': 2
                },
                {
                    'name': lora_3_name,
                    'start_step': lora_3_start_step,
                    'end_step': lora_3_end_step,
                    'start_strength': lora_3_start_strength,
                    'end_strength': lora_3_end_strength,
                    'curve_type': lora_3_curve_type,
                    'curve_param': lora_3_curve_param,
                    'strength_clip': lora_3_strength_clip,
                    'index': 3
                }
            ]
            
            # Filter out "None" LoRAs
            active_loras = [config for config in lora_configs if config['name'] != "None"]
            
            if len(active_loras) == 0:
                # No LoRAs selected
                print("[LoRA Scheduler] No LoRAs selected")
                return (model, clip, self.create_dummy_image())
            
            # Clone model and clip
            model_lora = model.clone()
            clip_lora = clip.clone()
            
            # Store all schedules for graphing
            all_schedules = []
            
            # Process each LoRA
            for config in active_loras:
                lora_name = config['name']
                start_step = min(config['start_step'], num_steps)
                end_step = min(config['end_step'], num_steps)
                
                if start_step >= end_step:
                    print(f"[LoRA Scheduler] Warning: LoRA {config['index']} ({lora_name}) has invalid step range, skipping")
                    continue
                
                # Load LoRA
                lora_path = folder_paths.get_full_path("loras", lora_name)
                lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                
                # Generate schedule
                schedule_length = end_step - start_step
                t = np.linspace(0, 1, schedule_length)
                curve = self.generate_curve(t, config['curve_type'], config['curve_param'])
                
                # Map curve to strength range
                weights = config['start_strength'] + (config['end_strength'] - config['start_strength']) * curve
                
                # Create full schedule
                full_schedule = np.zeros(num_steps)
                full_schedule[start_step:end_step] = weights
                
                # Calculate average weight
                avg_weight = np.mean(weights)
                
                # Store schedule for graph
                all_schedules.append({
                    'name': lora_name,
                    'schedule': full_schedule,
                    'avg_weight': avg_weight,
                    'start_step': start_step,
                    'end_step': end_step,
                    'curve_type': config['curve_type'],
                    'curve_param': config['curve_param'],
                    'index': config['index']
                })
                
                if print_schedule:
                    print(f"\n[LoRA Scheduler] LoRA {config['index']}: {lora_name}")
                    print(f"  Steps: {start_step} → {end_step}")
                    print(f"  Strength: {config['start_strength']:.3f} → {config['end_strength']:.3f}")
                    print(f"  Curve: {config['curve_type']} (param={config['curve_param']:.2f})")
                    print(f"  Applied weight: {avg_weight:.3f}")
                
                # Get key mappings
                key_map = {}
                try:
                    key_map = comfy.lora.model_lora_keys_unet(model_lora.model, key_map)
                except:
                    pass
                
                try:
                    key_map = comfy.lora.model_lora_keys_clip(clip_lora.cond_stage_model, key_map)
                except:
                    pass
                
                # Load patches
                loaded = comfy.lora.load_lora(lora, key_map)
                
                # Apply to model and CLIP
                if abs(avg_weight) > 1e-6:
                    model_lora.add_patches(loaded, avg_weight)
                
                if abs(config['strength_clip']) > 1e-6:
                    clip_lora.add_patches(loaded, config['strength_clip'])
                
                print(f"[LoRA Scheduler] Applied LoRA {config['index']}: {lora_name} (weight: {avg_weight:.3f})")
            
            # Generate combined graph
            graph_image = None
            if show_graph and len(all_schedules) > 0:
                try:
                    graph_image = self.generate_multi_graph(all_schedules, num_steps)
                except Exception as e:
                    print(f"[LoRA Scheduler] Graph generation failed: {e}")
                    import traceback
                    traceback.print_exc()
                    graph_image = None
            
            if graph_image is None:
                graph_image = self.create_dummy_image()
            
            return (model_lora, clip_lora, graph_image)
            
        except Exception as e:
            print(f"[LoRA Scheduler] ERROR: {e}")
            import traceback
            traceback.print_exc()
            dummy_image = self.create_dummy_image()
            return (model, clip, dummy_image)
    
    def generate_multi_graph(self, schedules, num_steps):
        """Generate a matplotlib graph showing multiple LoRA schedules"""
        
        fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
        
        # Color palette for different LoRAs
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        steps = np.arange(num_steps)
        
        # Plot each LoRA schedule
        for i, sched in enumerate(schedules):
            color = colors[i % len(colors)]
            label = f"LoRA {sched['index']}: {sched['name']}"
            
            # Plot the schedule
            ax.plot(steps, sched['schedule'], linewidth=2.5, label=label, 
                   color=color, alpha=0.8, zorder=2+i)
            
            # Highlight active region
            active_steps = steps[sched['start_step']:sched['end_step']]
            active_weights = sched['schedule'][sched['start_step']:sched['end_step']]
            
            if len(active_steps) > 0:
                ax.scatter(active_steps, active_weights, c=color, s=20, 
                          zorder=10+i, alpha=0.5)
                
                # Fill under curve
                ax.fill_between(active_steps, 0, active_weights, alpha=0.15, color=color)
                
                # Show average line
                ax.axhline(y=sched['avg_weight'], color=color, linestyle=':', 
                          alpha=0.5, linewidth=1.5)
        
        # Styling
        ax.set_xlabel('Sampling Step', fontsize=12, fontweight='bold')
        ax.set_ylabel('LoRA Strength', fontsize=12, fontweight='bold')
        ax.set_title('Multi-LoRA Schedule (Independent Curves)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', fontsize=9)
        
        # Set axis limits
        ax.set_xlim(-1, num_steps)
        
        # Calculate y-axis range from all schedules
        all_weights = np.concatenate([s['schedule'] for s in schedules])
        y_min = min(0, np.min(all_weights) - 0.2)
        y_max = max(0, np.max(all_weights) + 0.2)
        ax.set_ylim(y_min, y_max)
        
        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add info box
        info_lines = [f'Total Steps: {num_steps}', f'Active LoRAs: {len(schedules)}', '']
        for sched in schedules:
            short_name = sched['name'].split('/')[-1][:25]  # Truncate long names
            info_lines.append(f"LoRA {sched['index']}: {short_name}")
            info_lines.append(f"  Avg: {sched['avg_weight']:.3f} | {sched['curve_type']}")
        
        info_text = '\n'.join(info_lines)
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='lightyellow', alpha=0.85),
               fontsize=8, family='monospace')
        
        plt.tight_layout()
        
        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        # Convert to ComfyUI image format
        img_array = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array)[None,]
        
        return img_tensor
    
    def create_dummy_image(self):
        """Create a small dummy image"""
        img_array = np.zeros((64, 64, 3), dtype=np.float32)
        img_tensor = torch.from_numpy(img_array)[None,]
        return img_tensor


# Node registration
NODE_CLASS_MAPPINGS = {
    "CurvedLoRAScheduler": CurvedLoRAScheduler
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CurvedLoRAScheduler": "Curved LoRA Scheduler (Multi)"
}