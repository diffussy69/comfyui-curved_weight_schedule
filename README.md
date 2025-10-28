# ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, LoRA scheduling, regional prompting, and image utilities for ComfyUI. Control your ControlNet and LoRA strengths across time and space with precision and visual feedback, plus powerful masking and regional prompting tools.

## 🌟 Features

### ControlNet Scheduling
- **Curved ControlNet Scheduler**: Schedule ControlNet strength across generation steps with 13 different curve types
- **Visual Feedback**: Real-time graph preview showing your strength curve
- **Multi-Mask Strength Combiner**: Apply different ControlNet strengths to different regions of your image

### LoRA Scheduling
- **Curved LoRA Scheduler (Multi)**: Apply up to 3 LoRAs with independent curved weight schedules
- **Independent Control**: Each LoRA gets its own curve, strength range, and active steps
- **Multi-LoRA Visualization**: See all LoRA schedules on one graph with color-coded curves

### Regional Prompting & Masking
- **Regional Prompting**: Use different text prompts for different masked areas
- **Regional Prompt Interpolation**: Smooth gradient transitions between different prompts
- **Mask Symmetry Tool**: Mirror masks across axes for symmetrical compositions
- **Auto Person Mask**: AI-powered automatic person/foreground detection and masking
- **Auto Background Mask**: Automatic background masking (inverted person mask)

## 📦 Installation

1. Navigate to your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes/
```

2. Clone this repository:
```bash
git clone https://github.com/diffussy69/comfyui-curved_weight_schedule.git
```

3. Install dependencies (if not already installed):
```bash
pip install matplotlib pillow numpy torch
```

4. Restart ComfyUI

The nodes will appear in:
- `conditioning/controlnet` → Curved ControlNet Scheduler
- `loaders` → Curved LoRA Scheduler (Multi)
- `mask` → Multi-Mask Strength Combiner, Mask Symmetry Tool
- `conditioning` → Regional Prompting, Regional Prompt Interpolation

## 🎯 Node Overview

### 1. Curved ControlNet Scheduler

Control ControlNet strength across generation steps using mathematical curves.

**Key Parameters:**
- `num_keyframes`: Number of control points (2-100)
- `start_percent` / `end_percent`: When to start/stop the curve (0.0-1.0)
- `start_strength` / `end_strength`: Strength values at start and end
- `curve_type`: Shape of the strength transition
- `curve_param`: Controls transition speed/steepness

**Available Curve Types:**
- `strong_to_weak`: Start with high control, gradually release
- `weak_to_strong`: Build up control over time
- `linear`: Straight line transition
- `ease_in` / `ease_out` / `ease_in_out`: Smooth acceleration curves
- `bell_curve`: Strong in middle, weak at ends
- `reverse_bell`: Weak in middle, strong at ends
- `exponential_up` / `exponential_down`: Dramatic transitions
- `sine_wave`: Oscillating control (experimental)
- `bounce`: Bouncing effect
- `custom_bezier`: Customizable bezier curve

**Outputs:**
- `TIMESTEP_KF`: Connect to Apply Advanced ControlNet's timestep_kf input
- `curve_graph`: Visual preview (connect to Preview Image)

### 2. Curved LoRA Scheduler (Multi)

Apply up to 3 LoRAs with completely independent curved weight schedules over the generation process.

**Key Parameters (Per LoRA):**
- `lora_X_name`: Select LoRA file from your loras folder
- `lora_X_start_step`: Step to start applying this LoRA (0 to num_steps)
- `lora_X_end_step`: Step to stop applying this LoRA
- `lora_X_start_strength`: LoRA strength at start_step (-5.0 to 5.0)
- `lora_X_end_strength`: LoRA strength at end_step (-5.0 to 5.0)
- `lora_X_curve_type`: Same 13 curve types as ControlNet scheduler
- `lora_X_curve_param`: Controls curve steepness (0.1 to 10.0)
- `lora_X_strength_clip`: Separate CLIP strength multiplier

**Global Parameters:**
- `num_steps`: Total number of sampling steps (must match your sampler)
- `print_schedule`: Print detailed weight schedules to console
- `show_graph`: Generate visual preview graph

**Outputs:**
- `MODEL`: Model with all LoRA patches applied
- `CLIP`: CLIP with all LoRA patches applied
- `curve_graph`: Multi-LoRA visualization (connect to Preview Image)

**Use Cases:**
- **Style Crossfade**: Fade from one style LoRA to another
  - LoRA 1: Style A (1.0→0.0, strong_to_weak)
  - LoRA 2: Style B (0.0→1.0, weak_to_strong)
  
- **Character + Detail**: Strong character early, add details later
  - LoRA 1: Character (1.2→0.5, exponential_down, steps 0-20)
  - LoRA 2: Details (0.0→1.0, ease_in, steps 10-30)
  
- **Bell Curve Effect**: Emphasize LoRA in middle of generation
  - LoRA 1: Style (0.3→0.3, bell_curve, steps 0-30)

- **Oscillating Style**: Create rhythmic style variations
  - LoRA 1: Effect (sine_wave with high curve_param)

**Important Notes:**
- Set any LoRA to "None" to disable it (use 1, 2, or all 3 LoRAs as needed)
- Each LoRA's schedule is completely independent
- The node applies the **averaged weight** from each LoRA's curve for stability
- The graph shows the full curve and indicates the applied average
- Make sure `num_steps` matches your sampler's step count

### 3. Multi-Mask Strength Combiner

Combine up to 5 separate masks with different ControlNet strengths.

**Key Parameters:**
- `base_strength`: Global multiplier for all masks
- `mask_X`: Individual mask inputs (1-5)
- `mask_X_strength`: Strength multiplier for each mask
- `blend_mode`: How overlapping masks combine
- `normalize_output`: Clamp result to [0,1]

**Blend Modes:**
- `max`: Takes highest strength (best for separate regions)
- `add`: Adds strengths together (for layering)
- `multiply`: Multiplies strengths (for soft effects)
- `average`: Averages all strengths (for smooth blending)

**Output:**
- `combined_mask`: Connect to Apply Advanced ControlNet's mask_optional input

### 4. Regional Prompting

Apply different text prompts to different regions of your image.

**Key Parameters:**
- `clip`: Your CLIP model
- `base_positive`: Base prompt applied to entire image
- `region_X_mask`: Mask for each region (1-5)
- `region_X_prompt`: Text prompt for that region
- `region_X_strength`: How strongly the prompt affects the region

**Output:**
- `conditioning`: Connect to KSampler's positive input

### 5. Regional Prompt Interpolation

Smoothly interpolate between different prompts across regions with gradient transitions.

**Key Parameters:**
- `clip`: Your CLIP model
- `base_positive`: Base prompt applied everywhere
- `region_X_mask`: Masks for regions to interpolate between (supports 3 regions)
- `region_X_prompt`: Prompts for each region
- `region_X_strength`: Conditioning strength for each region
- `interpolation_steps`: Number of gradient steps between regions (2-20)
- `transition_mode`: How to blend between regions
  - `linear`: Straight blend
  - `smooth`: Smoothstep S-curve
  - `ease_in_out`: Slow start/end, fast middle
- `gradient_direction`: Direction of transition flow
  - `auto`: Detects from mask positions
  - `left_to_right`, `right_to_left`, `top_to_bottom`, `bottom_to_top`, `radial`

**Outputs:**
- `conditioning`: Connect to KSampler's positive input
- `interpolation_viz`: Visual preview of interpolation zones

**Use Cases:**
- Sunrise → Day → Sunset transitions
- Sky → Horizon → Ground gradients
- Temperature transitions (hot → cold)
- Depth-based prompts (near → far)

### 6. Mask Symmetry Tool

Mirror and flip masks across different axes for symmetrical compositions.

**Key Parameters:**
- `mask`: Input mask to mirror
- `symmetry_mode`: Type of symmetry to apply
  - `none`: No symmetry (passthrough)
  - `horizontal`: Left ↔ Right mirror
  - `vertical`: Top ↔ Bottom mirror
  - `both`: Mirror both axes (4 copies)
  - `diagonal_tl_br`: Mirror along \ diagonal
  - `diagonal_tr_bl`: Mirror along / diagonal
  - `radial_4way`: 4-way radial symmetry (kaleidoscope)
- `blend_mode`: How to combine original with mirrored
  - `replace`: Use mirrored where it exists
  - `add`: Add mirrored to original
  - `max`: Take highest value
  - `average`: Average both
- `blend_strength`: Strength of mirrored portion (0.0-1.0)
- `invert_mirrored`: Invert the mirrored portion

**Output:**
- `symmetrical_mask`: Mirrored mask ready to use

**Use Cases:**
- Portraits: Paint one side of face, mirror to other
- Architecture: Paint half of building
- Butterflies/symmetrical subjects
- Quick masking workflows

## 💡 Usage Examples

### Example 1: LoRA Style Crossfade

Smoothly transition from one LoRA style to another during generation.

**Workflow:**
```
┌─────────────────────────────────┐
│ Curved LoRA Scheduler (Multi)   │
│                                 │
│ LoRA 1: anime_style.safetensors│
│ - start_step: 0                 │
│ - end_step: 20                  │
│ - start_strength: 1.5           │
│ - end_strength: 0.0             │
│ - curve_type: strong_to_weak    │
│ - curve_param: 2.5              │
│                                 │
│ LoRA 2: photorealistic.safetensors│
│ - start_step: 10                │
│ - end_step: 30                  │
│ - start_strength: 0.0           │
│ - end_strength: 1.2             │
│ - curve_type: weak_to_strong    │
│ - curve_param: 2.0              │
│                                 │
│ LoRA 3: None                    │
└────────┬────────────────────────┘
         │
         ├─────────┐
         │         │
    ┌────▼───┐  ┌─▼────────┐
    │ MODEL  │  │ CLIP     │
    │ Output │  │ Output   │
    └────┬───┘  └──────────┘
         │
    ┌────▼──────┐
    │ KSampler  │
    └───────────┘
```

**Result:** Starts with strong anime style that gradually fades out while photorealistic style fades in, creating a smooth artistic transition.

### Example 2: Character + Environment + Details

Layer multiple LoRAs with different timing for complex compositions.

**Workflow:**
```
┌─────────────────────────────────┐
│ Curved LoRA Scheduler (Multi)   │
│                                 │
│ LoRA 1: character_lora          │
│ - start_step: 0, end_step: 25   │
│ - start_str: 1.2, end_str: 0.6  │
│ - curve_type: exponential_down  │
│                                 │
│ LoRA 2: environment_lora        │
│ - start_step: 5, end_step: 30   │
│ - start_str: 0.8, end_str: 0.8  │
│ - curve_type: linear            │
│                                 │
│ LoRA 3: detail_enhancer         │
│ - start_step: 15, end_step: 30  │
│ - start_str: 0.0, end_str: 1.0  │
│ - curve_type: ease_in           │
└─────────────────────────────────┘
```

**Result:** Character establishes strongly early then maintains moderate influence, environment provides consistent context throughout, details ramp up in final stages for refinement.

### Example 3: Composition Lock (ControlNet Strong Start, Fade Out)

Lock in composition early with ControlNet, then let the model add details freely.

**Workflow:**
```
┌─────────────────┐
│ Load ControlNet │
└────────┬────────┘
         │
┌────────▼───────────────────┐
│ Curved ControlNet Scheduler│
│ - curve_type: strong_to_weak
│ - start_percent: 0.0
│ - end_percent: 0.4
│ - start_strength: 1.0
│ - end_strength: 0.1
│ - curve_param: 3.0
└────────┬───────────────────┘
         │
┌────────▼──────────────────┐
│ Apply Advanced ControlNet │
│ (timestep_kf input)       │
└───────────────────────────┘
```

**Result:** ControlNet strongly guides early steps (structure), then releases control by 40% for creative details.

### Example 4: Regional Control with Different Strengths

Apply ControlNet more strongly to some areas than others.

**Workflow:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Mountains    │     │ Flowers      │     │ Sky          │
│ Mask         │     │ Mask         │     │ Mask         │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                ┌───────────▼──────────────┐
                │ Multi-Mask Strength      │
                │ Combiner                 │
                │ - mask_1_strength: 1.5   │  (mountains - high)
                │ - mask_2_strength: 0.4   │  (flowers - low)
                │ - mask_3_strength: 0.8   │  (sky - medium)
                │ - blend_mode: max        │
                └───────────┬──────────────┘
                            │
                ┌───────────▼──────────────┐
                │ Apply Advanced ControlNet│
                │ (mask_optional input)    │
                └──────────────────────────┘
```

**Result:** Mountains follow reference closely (1.5x), flowers have creative freedom (0.4x), sky is moderately guided (0.8x).

### Example 5: Regional Prompting with Different Descriptions

Use different text prompts for different regions.

**Workflow:**
```
┌──────────────┐
│ CLIP Model   │
└──────┬───────┘
       │
┌──────▼────────────────────────┐
│ Regional Prompting            │
│ - base_positive:              │
│   "masterpiece, photorealistic"│
│                               │
│ - region_1_mask: mountains    │
│ - region_1_prompt:            │
│   "snowy peaks, dramatic"     │
│ - region_1_strength: 1.2      │
│                               │
│ - region_2_mask: flowers      │
│ - region_2_prompt:            │
│   "wildflowers, soft bokeh"   │
│ - region_2_strength: 1.0      │
└───────────┬───────────────────┘
            │
    ┌───────▼────────┐
    │ KSampler       │
    │ (positive)     │
    └────────────────┘
```

**Result:** Mountains get "snowy peaks" style, flowers get "wildflowers" style, with base quality tags applied everywhere.

### Example 6: Ultimate Combo - LoRA + ControlNet + Regional Prompts

Combine LoRA scheduling, ControlNet scheduling, and regional prompts for maximum control.

**Workflow:**
```
┌────────────────────────┐
│ Curved LoRA Scheduler  │
│ - Style LoRA fading    │
│ - Detail LoRA ramping  │
└──────────┬─────────────┘
           │
    ┌──────▼──────┐
    │ MODEL/CLIP  │
    └──────┬──────┘
           │
┌──────────▼─────────────────────┐
│ Regional Prompting             │
│ - Different prompts per region │
└──────────┬─────────────────────┘
           │
    ┌──────▼──────┐
    │ KSampler    │
    └──────┬──────┘
           │
┌──────────▼──────────────────────┐
│ Curved ControlNet Scheduler     │
│ - Composition lock early        │
└──────────┬──────────────────────┘
           │
┌──────────▼──────────────────────┐
│ Multi-Mask Strength Combiner    │
│ - Different strengths per region│
└──────────┬──────────────────────┘
           │
┌──────────▼──────────────────────┐
│ Apply Advanced ControlNet       │
└─────────────────────────────────┘
```

**Result:** Complete control over style, composition, and content - with everything changing dynamically over time and space!

## 🎨 Practical Tips

### LoRA Scheduling Tips

**Curve Selection:**
- `strong_to_weak`: Great for style LoRAs that should guide early then fade
- `weak_to_strong`: Perfect for detail LoRAs that refine in later steps
- `bell_curve`: Emphasize LoRA during middle structure-forming steps
- `linear`: Simple, predictable transitions
- `sine_wave`: Experimental - creates rhythmic variations

**Strength Values:**
- Start conservative: 0.8-1.2 for most LoRAs
- Can go higher (1.5-2.0) for subtle LoRAs that need boosting
- Negative values work for some LoRAs (style removal)
- CLIP strength often works well at 1.0

**Step Ranges:**
- Early steps (0-10): Structure and composition
- Mid steps (10-20): Main content and style
- Late steps (20-30): Details and refinement
- Overlap ranges for smooth transitions

**Multi-LoRA Strategy:**
- LoRA 1: Primary style/character (strong, covers most steps)
- LoRA 2: Secondary effect (targeted timing)
- LoRA 3: Details/enhancement (late steps only)

### ControlNet Curve Selection

**For Composition Control:**
- `strong_to_weak` with curve_param=2.5-4.0 → Lock composition early, release later
- Set end_percent=0.3-0.5 → Only control first 30-50% of generation

**For Detail Refinement:**
- `weak_to_strong` with curve_param=2.0 → Let model generate freely, then guide details
- Set start_percent=0.5 → Only apply ControlNet in second half

**For Style Consistency:**
- `bell_curve` with curve_param=2.0-3.0 → Strong guidance during structure formation
- Weak at start/end for creative freedom

**For Experimental Effects:**
- `sine_wave` → Oscillating control (wild results!)
- `bounce` → Rhythmic control variations

### Mask Painting Tips

- Paint each region as a separate mask - don't worry about opacity
- Use full opacity - the strength settings control the effect
- Allow small overlaps - use blend_mode=max to handle them
- Test one region at a time - easier to dial in individual strengths

### Regional Prompting Best Practices

**Base Prompt:**
- Use for universal quality tags: "masterpiece, high quality, detailed"
- Avoid specific objects/subjects

**Regional Prompts:**
- Be specific about what's in that region
- Include style/lighting/atmosphere for that area
- Can include negative concepts if needed

**Strength Values:**
- Start at 1.0 for all regions
- Increase if a region isn't responding (1.2-1.5)
- Decrease if a region is overpowering others (0.6-0.8)

### Prompt Interpolation Tips

**Interpolation Steps:**
- 3-5 steps: Faster, more distinct regions
- 8-12 steps: Smooth, natural transitions
- 15-20 steps: Ultra-smooth, subtle gradients

**Transition Modes:**
- `linear`: Quick experiments, testing
- `smooth`: Best for natural transitions (recommended)
- `ease_in_out`: Dramatic effects, artistic shots

**Gradient Direction:**
- Use `auto` first - it usually picks correctly
- Override if transition looks wrong
- `radial` great for center → edge effects

### Symmetry Tool Tips

**When to Use:**
- Portraits (faces, eyes, facial features)
- Architecture (buildings, windows, facades)
- Nature (butterflies, flowers, leaves)
- Any symmetrical subject

**Blend Modes:**
- `max`: Default, works for most cases
- `add`: When you want overlap to be stronger
- `average`: For subtle, softer symmetry
- `replace`: For hard-edge symmetrical masks

**Pro Tip:**
- Use `radial_4way` for mandala-like patterns
- Combine with `invert_mirrored` for creative negative space effects

## 🐛 Troubleshooting

**Issue: Graph not showing**
- Solution: Make sure matplotlib is installed: `pip install matplotlib`
- Set show_graph=false if you don't need it

**Issue: LoRA not affecting output**
- Solution:
  - Verify LoRA file exists in ComfyUI/models/loras/
  - Check that start_step < end_step
  - Try increasing strength values (1.2-1.5)
  - Ensure num_steps matches your sampler
  - Enable print_schedule=true to see applied weights

**Issue: Multiple LoRAs conflicting**
- Solution:
  - Check strength values aren't too high (try 0.8-1.2 range)
  - Stagger step ranges so they don't all peak at once
  - Use different curve types for variety
  - Start with 2 LoRAs before adding a third

**Issue: Masks not affecting output**
- Solution:
  - Check that masks are actually painted (not empty)
  - Verify mask is connected to correct input
  - Try increasing strength values
  - Enable show_debug=true to see what the node is processing

**Issue: Regional prompts bleeding into each other**
- Solution:
  - Make sure masks don't overlap (or use interpolation node for intentional blending)
  - Use more specific prompts
  - Adjust region strength values

**Issue: Symmetry creating unexpected results**
- Solution:
  - Check that your mask doesn't already cover both sides
  - Try different blend modes
  - Reduce blend_strength for subtler effect
  - Use show_debug=true to see what's happening

**Issue: Interpolation not visible**
- Solution:
  - Increase interpolation_steps (try 10-15)
  - Use transition_mode=smooth for more obvious gradients
  - Check that masks are positioned to allow transition zones
  - Enable show_debug=true to verify regions are being created

**Issue: ControlNet effect too strong/weak everywhere**
- Solution:
  - Adjust base_strength in Multi-Mask Combiner
  - Check strength value on Apply Advanced ControlNet node
  - Verify start_strength and end_strength values in Curved ControlNet Scheduler

## 📋 Requirements

- ComfyUI
- ComfyUI-Advanced-ControlNet
- Python packages: matplotlib, pillow, numpy, torch

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new curve types or features
- Request improvements
- Submit pull requests

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Credits

Created with assistance from Claude (Anthropic). Special thanks to the ComfyUI and Advanced ControlNet communities.

---

**Enjoy creating with precise control over every aspect of your generation!** 🎨✨

If you find this useful, consider starring the repo and sharing your creations!
