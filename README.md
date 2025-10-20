# ControlNet - Curved weights and multi-mask weights.
Custom Node for ComfyUI that allows you to set a weighted curve to your ControlNet giving you more control over the weight of the model over the course of image generation. 

# ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling and regional prompting nodes for ComfyUI. Control your ControlNet strength across time and space with precision and visual feedback.

## 🌟 Features

- **Curved Timestep Keyframes**: Schedule ControlNet strength across generation steps with 14 different curve types
- **Visual Feedback**: Real-time graph preview showing your strength curve
- **Multi-Mask Strength Combiner**: Apply different ControlNet strengths to different regions of your image
- **Regional Prompting**: Use different text prompts for different masked areas
- **Multiple Blend Modes**: Max, Add, Multiply, and Average for flexible mask combination

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
- `conditioning/controlnet` → **Curved Timestep Keyframes**
- `mask` → **Multi-Mask Strength Combiner**
- `conditioning` → **Regional Prompting**

## 🎯 Node Overview

### 1. Curved Timestep Keyframes

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
- `TIMESTEP_KF`: Connect to Apply Advanced ControlNet's `timestep_kf` input
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
- `combined_mask`: Connect to Apply Advanced ControlNet's `mask_optional` input

### 3. Regional Prompting

Apply different text prompts to different regions of your image.

**Key Parameters:**
- `clip`: Your CLIP model
- `base_positive`: Base prompt applied to entire image
- `region_X_mask`: Mask for each region (1-5)
- `region_X_prompt`: Text prompt for that region
- `region_X_strength`: How strongly the prompt affects the region

**Output:**
- `conditioning`: Connect to KSampler's `positive` input

## 💡 Usage Examples

### Example 1: Composition Lock (Strong Start, Fade Out)

Lock in composition early, then let the model add details freely.

**Workflow:**
```
┌─────────────────┐
│ Load ControlNet │
└────────┬────────┘
         │
┌────────▼──────────────────┐
│ Curved Timestep Keyframes │
│ - curve_type: strong_to_weak
│ - start_percent: 0.0
│ - end_percent: 0.4
│ - start_strength: 1.0
│ - end_strength: 0.1
│ - curve_param: 3.0
└────────┬──────────────────┘
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

### Example 4: Ultimate Control (All Three Nodes Combined)

Combine timestep curves + regional ControlNet strengths + regional prompts.

**Workflow:**
```
                    ┌─────────────┐
                    │ CLIP Model  │
                    └──────┬──────┘
                           │
            ┌──────────────▼─────────────────┐
            │ Regional Prompting             │
            │ - Different prompts per region │
            └──────────┬─────────────────────┘
                       │
                       ├─────────────────────┐
                       │                     │
         ┌─────────────▼──────┐    ┌────────▼─────────────┐
         │ KSampler           │    │ Curved Timestep      │
         │ (positive input)   │    │ Keyframes            │
         └────────────────────┘    │ - Strength over time │
                                   └────────┬─────────────┘
                                            │
                  ┌─────────────────────────┤
                  │                         │
    ┌─────────────▼──────────────┐   ┌─────▼──────────────────┐
    │ Multi-Mask Strength        │   │ Apply Advanced         │
    │ Combiner                   │───│ ControlNet             │
    │ - Different strengths      │   │ - timestep_kf          │
    │   per region               │   │ - mask_optional        │
    └────────────────────────────┘   └────────────────────────┘
```

**Result:** 
- Different prompts per region (mountains, flowers, sky)
- Different ControlNet strengths per region (strong, medium, weak)
- Strength fades over time (starts strong, ends weak)
- Maximum creative control! 🎨

## 🎨 Practical Tips

### Curve Selection Guide

**For Composition Control:**
- `strong_to_weak` with `curve_param=2.5-4.0` → Lock composition early, release later
- Set `end_percent=0.3-0.5` → Only control first 30-50% of generation

**For Detail Refinement:**
- `weak_to_strong` with `curve_param=2.0` → Let model generate freely, then guide details
- Set `start_percent=0.5` → Only apply ControlNet in second half

**For Style Consistency:**
- `bell_curve` with `curve_param=2.0-3.0` → Strong guidance during structure formation
- Weak at start/end for creative freedom

**For Experimental Effects:**
- `sine_wave` → Oscillating control (wild results!)
- `bounce` → Rhythmic control variations

### Mask Painting Tips

1. **Paint each region as a separate mask** - don't worry about opacity
2. **Use full opacity** - the strength settings control the effect
3. **Allow small overlaps** - use `blend_mode=max` to handle them
4. **Test one region at a time** - easier to dial in individual strengths

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

## 🐛 Troubleshooting

**Issue:** Graph not showing
- **Solution:** Make sure matplotlib is installed: `pip install matplotlib`
- Set `show_graph=false` if you don't need it

**Issue:** Masks not affecting output
- **Solution:** 
  - Check that masks are actually painted (not empty)
  - Verify mask is connected to correct input
  - Try increasing strength values
  - Enable `show_debug=true` to see what the node is processing

**Issue:** Regional prompts bleeding into each other
- **Solution:**
  - Make sure masks don't overlap
  - Use more specific prompts
  - Adjust region strength values

**Issue:** ControlNet effect too strong/weak everywhere
- **Solution:**
  - Adjust `base_strength` in Multi-Mask Combiner
  - Check `strength` value on Apply Advanced ControlNet node
  - Verify `start_strength` and `end_strength` values in Curved Timestep Keyframes

## 📋 Requirements

- ComfyUI
- [ComfyUI-Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet)
- Python packages: `matplotlib`, `pillow`, `numpy`, `torch`

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new curve types
- Request features
- Submit pull requests

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Credits

Created with assistance from Claude (Anthropic). Special thanks to the ComfyUI and Advanced ControlNet communities.

---

**Enjoy creating with precise control! 🎨✨**

If you find this useful, consider starring the repo and sharing your creations!
