ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, regional prompting, masking, and LoRA weight automation tools for ComfyUI.
Control your ControlNet and LoRA strength across time and space with precision and visual feedback.

🌟 Features
🧠 ControlNet & Masking Tools

Curved Timestep Keyframes – schedule ControlNet strength across generation steps with 14 curve types

Visual Feedback – real-time matplotlib graph of your strength curves

Multi-Mask Strength Combiner – different ControlNet strengths for multiple masked regions

Regional Prompting + Interpolation – different prompts per region with smooth gradient transitions

Mask Symmetry Tool – mirror or radial symmetry for masks

Auto Person / Background Masking – AI-powered foreground/background segmentation

Multiple Blend Modes – Max, Add, Multiply, Average

🎚️ LoRA Scheduling (New!)

Curved LoRA Scheduler (Multi) – apply up to 3 LoRA models with independent activation ranges, strength curves, and CLIP scaling

13 curve types (linear, ease_in/out, strong_to_weak, bell_curve, sine_wave, bounce, etc.)

Automatic matplotlib graph preview for all LoRA weight schedules

Fine-grained temporal control: fade LoRAs in/out, layer multiple styles, or alternate strengths over time

Works with any LoRA available in your ComfyUI environment

📦 Installation

(unchanged)

🎯 Node Overview
1–7. (Existing Nodes)

(Curved Timestep Keyframes, Multi-Mask Combiner, Regional Prompting, Regional Prompt Interpolation, Mask Symmetry Tool, Auto Person Mask, Auto Background Mask – as in your current README)

8. Curved LoRA Scheduler (Multi)

Apply multiple LoRA models with independent curved weight scheduling across sampling steps.

Purpose:
Precisely control how up to three LoRAs fade in, fade out, or vary in strength over the generation timeline — each with its own curve type, strength range, and active step range.

Key Parameters

Parameter	Description
model / clip	Base model and CLIP to apply LoRAs to
num_steps	Total number of sampler steps (should match your sampler)
lora_X_name	Select LoRA file for slot X (1–3)
lora_X_start_step / end_step	When each LoRA becomes active/inactive
lora_X_start_strength / end_strength	Strength range during its active window
lora_X_curve_type / curve_param	Defines curve shape and steepness
lora_X_strength_clip	Additional scaling applied to CLIP encoder
print_schedule	Prints LoRA scheduling details to console
show_graph	Displays matplotlib graph of all LoRA curves

Available Curve Types

linear, ease_in, ease_out, ease_in_out, strong_to_weak, weak_to_strong, sine_wave, bell_curve, reverse_bell, exponential_up, exponential_down, bounce, custom_bezier

Outputs

Output	Description
MODEL	Model with LoRAs dynamically applied
CLIP	CLIP with LoRAs applied
curve_graph	PNG visualization of LoRA strength curves

Visual Feedback

Real-time matplotlib chart showing:

Each LoRA’s active range and curve

Average applied weight per LoRA

Combined overview of all active curves

Use Cases

Fade in style LoRAs early for composition lock

Introduce character LoRAs late for detail refinement

Blend multiple styles or themes over time

Oscillate LoRA strengths for experimental effects

Category: loaders → Curved LoRA Scheduler (Multi)

## 💡 Usage Examples

### Understanding How Timestep and Mask Strengths Work Together

Both **Curved Timestep Keyframes** and **Multi-Mask Strength Combiner** control ControlNet strength, but in complementary ways that work **together**, not against each other.

**The Formula:**
```
Final ControlNet Strength = Timestep Strength × Mask Strength
```

**Curved Timestep Keyframes (TIME control):**
- Controls **WHEN** ControlNet is strong during generation (across steps)
- Affects the **entire image** at once
- Changes over time: Step 1 might be 1.3, Step 10 might be 0.8, Step 20 might be 0.3

**Multi-Mask Combiner (SPACE control):**
- Controls **WHERE** ControlNet is strong in the image (per region)
- Affects **specific areas** based on masks
- Stays consistent across time (unless you change it)

**Example Scenario:**

You have:
- mask_1 = person's face (strength: 1.0)
- mask_2 = person's body (strength: 0.5)
- mask_3 = background (strength: 0.2)

Your timestep curve starts at 1.2 and fades to 0.6

**At Step 5 (early, timestep = 1.2):**
```
Face:       1.2 × 1.0 = 1.20 (very strong - lock in structure)
Body:       1.2 × 0.5 = 0.60 (medium - guide pose)
Background: 1.2 × 0.2 = 0.24 (weak - creative freedom)
```

**At Step 20 (late, timestep = 0.6):**
```
Face:       0.6 × 1.0 = 0.60 (medium - refine details)
Body:       0.6 × 0.5 = 0.30 (weak - add variation)
Background: 0.6 × 0.2 = 0.12 (very weak - mostly free)
```

**Why This Is Powerful:**
- **Without timestep curves**: All regions stay at fixed strength the entire time (rigid)
- **Without masks**: Entire image gets same strength everywhere (no regional control)
- **With both**: Each region has its own strength that evolves over time naturally

**Key Insight:** Mask strengths set the **relative priorities** (face more important than background), while timestep curves control the **overall intensity over time** (strong start, gentle finish). The ratios between regions are maintained throughout generation.

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

### Example 4: Smooth Prompt Transitions with Interpolation

Create gradient transitions between different prompt regions.

**Workflow:**
```
┌──────────────┐
│ CLIP Model   │
└──────┬───────┘
       │
┌──────▼────────────────────────────┐
│ Regional Prompt Interpolation     │
│ - base_positive: "photorealistic" │
│                                   │
│ - region_1_mask: sky              │
│ - region_1_prompt: "blue sky"     │
│                                   │
│ - region_2_mask: horizon          │
│ - region_2_prompt: "golden hour"  │
│                                   │
│ - region_3_mask: ground           │
│ - region_3_prompt: "green grass"  │
│                                   │
│ - interpolation_steps: 8          │
│ - transition_mode: smooth         │
│ - gradient_direction: top_to_bottom│
└───────────┬───────────────────────┘
            │
    ┌───────▼────────┐
    │ KSampler       │
    │ (positive)     │
    └────────────────┘
```

**Result:** Smooth gradient transition from "blue sky" → "golden hour" → "green grass" with 8 intermediate blended prompts creating natural color/atmosphere transitions.

### Example 5: Automated Person/Background Masking

Automatically separate person from background for different ControlNet strengths.

**Workflow:**
```
┌──────────────┐
│ Load Image   │
└──────┬───────┘
       │
       ├─────────────────────┐
       │                     │
┌──────▼──────────┐   ┌──────▼──────────────┐
│ Auto Person     │   │ Auto Background     │
│ Mask            │   │ Mask                │
│ - model: u2net  │   │ - model: u2net      │
└──────┬──────────┘   └──────┬──────────────┘
       │                     │
       │ person_mask         │ background_mask
       │                     │
       └─────────┬───────────┘
                 │
    ┌────────────▼─────────────────┐
    │ Multi-Mask Strength Combiner │
    │ - mask_1_strength: 1.0       │ (person - strong)
    │ - mask_2_strength: 0.3       │ (background - weak)
    └────────────┬─────────────────┘
                 │
    ┌────────────▼─────────────┐
    │ Apply Advanced ControlNet│
    │ (mask_optional)          │
    └──────────────────────────┘
```

**Result:** Person follows ControlNet closely (1.0 strength), background has creative freedom (0.3 strength) - fully automated, no manual masking!

### Example 6: Symmetrical Masking for Portraits

Quickly create symmetrical masks for portraits or architecture.

**Workflow:**
```
┌──────────────────┐
│ Load Image       │
│ (portrait)       │
└────────┬─────────┘
         │
┌────────▼─────────┐
│ Mask Editor      │
│ Paint left eye   │
└────────┬─────────┘
         │
┌────────▼──────────────┐
│ Mask Symmetry Tool    │
│ - symmetry: horizontal│
│ - blend_mode: max     │
│ - blend_strength: 1.0 │
└────────┬──────────────┘
         │
    Both eyes masked!
```

**Result:** Paint one eye, instantly get both eyes masked perfectly symmetrically.

### Example 7: Ultimate Control (All Nodes Combined)

Combine timestep curves + regional ControlNet strengths + regional prompts + interpolation + symmetry + auto-masking.

**Workflow:**
```
                    ┌─────────────┐
                    │ Load Image  │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
    ┌───────▼────────┐ ┌──▼───────────┐ │
    │ Auto Person    │ │ Auto         │ │
    │ Mask           │ │ Background   │ │
    └───────┬────────┘ │ Mask         │ │
            │          └──┬───────────┘ │
            │             │             │
            └──────┬──────┘             │
                   │                    │
         ┌─────────▼────────┐           │
         │ Multi-Mask       │           │
         │ Combiner         │           │
         └─────────┬────────┘           │
                   │                    │
         ┌─────────▼────────┐           │
         │ Regional Prompt  │           │
         │ Interpolation    │◄──────────┘
         └─────────┬────────┘
                   │
    ┌──────────────▼───────────┐
    │ Curved Timestep Keyframes│
    └──────────────┬────────────┘
                   │
    ┌──────────────▼─────────────┐
    │ Apply Advanced ControlNet  │
    └────────────────────────────┘
```

**Result:** 
- AI automatically masks person and background
- Smooth prompt transitions between regions (no harsh boundaries)
- Different ControlNet strengths per region (strong, medium, weak)
- Strength fades over time (starts strong, ends weak)
- Symmetrical masks if needed (portraits, architecture)
- Complete automation with maximum creative control! 🎨

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

### Auto Masking Tips

**Model Selection:**
- `u2net`: Best for general use, handles most subjects
- `u2net_human_seg`: Best for people/portraits
- `u2netp`: Faster but slightly lower quality
- Try different models if one doesn't work well

**Better Quality:**
- Enable `alpha_matting` for professional edge quality
- Handles hair, fur, and fine details much better
- Slower but worth it for final renders

**Common Issues:**
- Multiple people: All masked together (can't separate individuals)
- Complex backgrounds: May need alpha_matting enabled
- Fine details (hair): Always use alpha_matting

**Performance:**
- First run downloads model (~176MB)
- Processing: 2-5 seconds per image
- Cached for future use

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
  - Make sure masks don't overlap (or use interpolation node for intentional blending)
  - Use more specific prompts
  - Adjust region strength values

**Issue:** Symmetry creating unexpected results
- **Solution:**
  - Check that your mask doesn't already cover both sides
  - Try different blend modes
  - Reduce `blend_strength` for subtler effect
  - Use `show_debug=true` to see what's happening

**Issue:** Interpolation not visible
- **Solution:**
  - Increase `interpolation_steps` (try 10-15)
  - Use `transition_mode=smooth` for more obvious gradients
  - Check that masks are positioned to allow transition zones
  - Enable `show_debug=true` to verify regions are being created

**Issue:** Auto masking not working
- **Solution:**
  - Check that rembg is installed: `pip install rembg`
  - First run will download model (~176MB), be patient
  - Try different model types (u2net vs u2net_human_seg)
  - Enable `show_debug=true` to see what's happening

**Issue:** Bad mask quality from auto-masking
- **Solution:**
  - Enable `alpha_matting=true` for better edges
  - Increase alpha_matting thresholds if too aggressive
  - Try `u2net_human_seg` specifically for people
  - Enable `post_process_mask` for cleanup

**Issue:** ControlNet effect too strong/weak everywhere
- **Solution:**
  - Adjust `base_strength` in Multi-Mask Combiner
  - Check `strength` value on Apply Advanced ControlNet node
  - Verify `start_strength` and `end_strength` values in Curved Timestep Keyframes

## 📋 Requirements

- ComfyUI
- [ComfyUI-Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet) (for ControlNet nodes)
- Python packages: `matplotlib`, `pillow`, `numpy`, `torch`, `rembg`

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
