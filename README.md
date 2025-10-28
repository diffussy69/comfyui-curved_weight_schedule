ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, regional prompting, masking, and LoRA weight automation tools for ComfyUI.
Control your ControlNet and LoRA strength across time and space with precision and visual feedback.

🌟 Features
🧠 ControlNet & Masking

Curved Timestep Keyframes: Schedule ControlNet strength across generation steps with 14 different curve types
Visual Feedback: Real-time graph preview showing your strength curve
Multi-Mask Strength Combiner: Apply different ControlNet strengths to different regions of your image
Regional Prompting: Use different text prompts for different masked areas
Regional Prompt Interpolation: Smooth gradient transitions between different prompts
Mask Symmetry Tool: Mirror masks across axes for symmetrical compositions
Auto Person Mask: AI-powered automatic person/foreground detection and masking
Auto Background Mask: Automatic background masking (inverted person mask)
Multiple Blend Modes: Max, Add, Multiply, and Average for flexible mask combination

🎚️ LoRA Scheduling (New!)

Curved LoRA Scheduler (Multi): Apply up to 3 LoRA models with independent activation ranges, strength curves, and CLIP scaling
Independent Curves: Each LoRA can start, stop, and change strength at different sampling steps
13 Curve Types: linear, ease_in, ease_out, ease_in_out, strong_to_weak, weak_to_strong, sine_wave, bell_curve, reverse_bell, exponential_up, exponential_down, bounce, custom_bezier
Graph Visualization: Generates a matplotlib chart showing all LoRA schedules in one view
Dynamic Layering: Fade styles in/out, overlap influences, or alternate effects over time
Fully Compatible: Works with any LoRA in your ComfyUI folder

📦 Installation

Navigate to your ComfyUI custom nodes directory:

cd ComfyUI/custom_nodes/


Clone this repository:

git clone https://github.com/diffussy69/comfyui-curved_weight_schedule.git


Install dependencies (if not already installed):

pip install matplotlib pillow numpy torch rembg


💡 Note: rembg is only required for Auto Person/Background Mask nodes.
The first run will automatically download the AI models (~176 MB).

Restart ComfyUI.
Your nodes will appear in the following categories:

conditioning/controlnet → Curved Timestep Keyframes

mask → Multi-Mask Strength Combiner, Mask Symmetry Tool, Auto Person Mask, Auto Background Mask

conditioning → Regional Prompting, Regional Prompt Interpolation

loaders → Curved LoRA Scheduler (Multi)

🎯 Node Overview
1–7. (Existing Nodes)

(Curved Timestep Keyframes, Multi-Mask Combiner, Regional Prompting, Regional Prompt Interpolation, Mask Symmetry Tool, Auto Person Mask, Auto Background Mask – see above for details.)

8. Curved LoRA Scheduler (Multi)

Category: loaders → Curved LoRA Scheduler (Multi)

Control multiple LoRA models across your diffusion timeline with custom strength curves and activation ranges.

Purpose:
Blend styles, swap characters, or evolve composition dynamically by adjusting each LoRA’s strength over time.

Key Parameters

Parameter	Description
model / clip	The model and CLIP inputs to apply LoRAs to
num_steps	Total sampler steps (should match your sampler)
lora_X_name	Choose LoRA file for slot X (1–3)
lora_X_start_step / end_step	When the LoRA becomes active and stops
lora_X_start_strength / end_strength	Strength values at start and end of its active range
lora_X_curve_type / curve_param	Defines the shape and steepness of the curve
lora_X_strength_clip	Optional additional CLIP scaling
print_schedule	Prints each LoRA’s weight schedule in the console
show_graph	Displays a visual graph of all LoRA curves

Available Curve Types:
linear, ease_in, ease_out, ease_in_out, strong_to_weak, weak_to_strong, sine_wave, bell_curve, reverse_bell, exponential_up, exponential_down, bounce, custom_bezier

Outputs

Output	Description
MODEL	Model with all LoRAs applied dynamically
CLIP	CLIP with LoRA scaling applied
curve_graph	Real-time PNG preview of all LoRA strength curves

Visual Feedback

Each LoRA is color-coded in the graph

Active step range is shaded for clarity

Average applied weight shown as dotted line

Embedded info box lists LoRA names, curves, and parameters

Use Cases

🎨 Style Fading: Fade in one artstyle LoRA while fading out another

🧍 Character Blending: Introduce a character LoRA mid-generation

🌅 Timed Variation: Use bell_curve or sine_wave to oscillate intensity

🧠 Fine Control: Keep composition stable early, refine details later

💡 Example Workflow

Apply three LoRAs with different activation windows and curve shapes:

┌──────────────────┐
│   Load Checkpoint │
└─────────┬─────────┘
          │
┌─────────▼──────────────────┐
│  Curved LoRA Scheduler     │
│  - LoRA 1: strong_to_weak  │
│  - LoRA 2: weak_to_strong  │
│  - LoRA 3: bell_curve      │
│  - num_steps: 30           │
└─────────┬──────────────────┘
          │
┌─────────▼─────────────┐
│      KSampler          │
│   (uses MODEL + CLIP)  │
└────────────────────────┘


Result:
LoRA 1 dominates early and fades out, LoRA 2 grows in mid-steps,
LoRA 3 peaks at the middle for balanced blending — all visualized in the graph output.

🎨 Practical Tips

(Keep your existing ControlNet and Mask tips here — they remain valid and helpful.)

🐛 Troubleshooting

(Your existing troubleshooting section remains unchanged.)

📋 Requirements

ComfyUI

ComfyUI-Advanced-ControlNet (for ControlNet nodes)

Python packages: matplotlib, pillow, numpy, torch, rembg

🤝 Contributing

Contributions are welcome! Feel free to:

Report bugs

Suggest new curve types

Request features

Submit pull requests

📄 License

MIT License — free to use, modify, and build upon.

## 🙏 Credits

Created with assistance from Claude (Anthropic). Special thanks to the ComfyUI and Advanced ControlNet communities.

---

**Enjoy creating with precise control! 🎨✨**

If you find this useful, consider starring the repo and sharing your creations!
