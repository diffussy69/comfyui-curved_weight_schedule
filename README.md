# ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, regional prompting, and image utilities for ComfyUI. Control your ControlNet strength across time and space with precision and visual feedback, plus powerful masking and regional prompting tools.

## 🌟 Features

### ControlNet Scheduling
- **Curved ControlNet Scheduler**: Schedule ControlNet strength across generation steps with 13 different curve types
- **Visual Feedback**: Real-time graph preview showing your strength curve
- **Multi-Mask Strength Combiner**: Apply different ControlNet strengths to different regions of your image

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
git clone https://github.com/yourusername/comfyui-curved_weight_schedule
```

3. Install dependencies (if not already installed):
```bash
pip install matplotlib pillow numpy torch
```

4. Restart ComfyUI

The nodes will appear in:
- `conditioning/controlnet` → Curved ControlNet Scheduler
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

### 2. Multi-Mask Strength Combiner

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

### 3. Regional Prompting

Apply different text prompts to different regions of your image.

**Key Parameters:**
- `clip`: Your CLIP model
- `base_positive`: Base prompt applied to entire image
- `region_X_mask`: Mask for each region (1-5)
- `region_X_prompt`: Text prompt for that region
- `region_X_strength`: How strongly the prompt affects the region

**Output:**
- `conditioning`: Connect to KSampler's positive input

### 4. Regional Prompt Interpolation

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

### 5. Mask Symmetry Tool

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

### Example 1: Composition Lock (ControlNet Strong Start, Fade Out)

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

### Example 2: Regional Control with Different Strengths

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

### Example 3: Regional Prompting with Different Descriptions

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

### Example 4: Ultimate Combo - ControlNet + Regional Prompts

Combine ControlNet scheduling and regional prompts for maximum control.

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
