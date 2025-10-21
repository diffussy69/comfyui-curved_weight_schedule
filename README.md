# ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, regional prompting, and image utilities for ComfyUI. Control your ControlNet strength across time and space with precision and visual feedback, plus powerful image saving and watermarking tools.

## 🌟 Features

### ControlNet & Masking
- **Curved Timestep Keyframes**: Schedule ControlNet strength across generation steps with 14 different curve types
- **Visual Feedback**: Real-time graph preview showing your strength curve
- **Multi-Mask Strength Combiner**: Apply different ControlNet strengths to different regions of your image
- **Regional Prompting**: Use different text prompts for different masked areas
- **Regional Prompt Interpolation**: Smooth gradient transitions between different prompts
- **Mask Symmetry Tool**: Mirror masks across axes for symmetrical compositions
- **Auto Person Mask**: AI-powered automatic person/foreground detection and masking
- **Auto Background Mask**: Automatic background masking (inverted person mask)

### Image Utilities
- **Multi-Save Image (Clean)**: Save images to multiple locations with thorough metadata removal
- **Advanced Repeating Watermark**: Stock-photo style repeating watermarks with rotation and styling
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
   pip install matplotlib pillow numpy torch rembg
   ```
   
   **Note:** `rembg` is only required if you plan to use the Auto Person/Background Mask nodes. First run will download AI models (~176MB automatically).

4. Restart ComfyUI

The nodes will appear in:
- `conditioning/controlnet` → **Curved Timestep Keyframes**
- `mask` → **Multi-Mask Strength Combiner**, **Mask Symmetry Tool**, **Auto Person Mask**, **Auto Background Mask**
- `conditioning` → **Regional Prompting**, **Regional Prompt Interpolation**
- `image/save` → **Multi-Save Image (Clean)**
- `image/watermark` → **Advanced Repeating Watermark**

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
- `conditioning`: Connect to KSampler's `positive` input
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

### 6. Auto Person Mask

Automatically detect and mask people/foreground objects using AI (U2-Net).

**Key Parameters:**
- `image`: Input image
- `model`: AI model to use
  - `u2net`: General purpose, best quality (default)
  - `u2netp`: Faster, slightly lower quality
  - `u2net_human_seg`: Optimized for people/portraits
  - `silueta`: Alternative general model
- `alpha_matting`: Enable for better edge quality (slower but handles hair/fine details)
- `alpha_matting_foreground_threshold`: Fine-tune edge detection (0-255)
- `alpha_matting_background_threshold`: Fine-tune edge detection (0-255)
- `alpha_matting_erode_size`: Edge refinement size
- `post_process_mask`: Clean up mask with morphological operations

**Outputs:**
- `person_mask`: White = person, Black = background
- `masked_image`: Preview of person with transparent background

**Use Cases:**
- Automated masking for Multi-Mask Combiner
- Different ControlNet strengths for person vs background
- Regional prompting automation
- Background removal/replacement

**First Run:** Will automatically download AI model (~176MB), only happens once.

### 7. Auto Background Mask

Automatically generate background mask (inverted person mask).

**Key Parameters:**
- Same as Auto Person Mask

**Output:**
- `background_mask`: White = background, Black = person

**Use Cases:**
- Pair with Auto Person Mask for complete scene separation
- Apply different effects to background only
- Automated regional masking workflows

### 8. Multi-Save Image (Clean)

Save multiple images to different locations with thorough metadata removal.

**Key Parameters:**
- `image_1` / `image_2`: Images to save
- `save_path_1` / `save_path_2`: Full paths to save locations
- `filename_prefix_1` / `filename_prefix_2`: Filename prefixes
- `filename_suffix_1` / `filename_suffix_2`: Filename suffixes
- `format`: Output format (png/jpg/jpeg)
- `quality`: JPEG quality (1-100)
- `use_exiftool`: Enable thorough exiftool metadata removal (requires exiftool.exe)

**Features:**
- **Two-stage metadata removal**: PIL strips on save, exiftool thoroughly cleans
- Auto-creates directories
- Handles filename conflicts (appends numbers)
- Timestamps in filenames
- Separate filename formats per image

**Metadata Removal:**
For maximum thoroughness:
1. Download exiftool from https://exiftool.org/
2. Place `exiftool.exe` in ComfyUI root folder
3. Enable `use_exiftool` in node

Without exiftool, still removes most metadata via PIL.

**Use Cases:**
- Save watermarked + clean versions simultaneously
- Remove all metadata before sharing images
- Organized multi-destination workflows

### 9. Advanced Repeating Watermark

Create stock-photo style repeating watermarks with full control over styling and positioning.

**Key Parameters:**
- `image`: Input image
- `text`: Watermark text
- `pattern_type`: Watermark pattern
  - `single`: One centered watermark
  - `grid`: Regular grid pattern
  - `diagonal`: Offset rows for diagonal pattern (stock photo style)
  - `dense_grid`: Tighter spacing for maximum coverage
- `font_size`: Text size (8-500)
- `font_color`: Preset colors or custom hex
- `opacity`: Transparency (0.0-1.0)
- `rotation`: Angle in degrees (-180 to 180)
- `bold` / `italic`: Text styling
- `spacing_x` / `spacing_y`: Distance between watermarks
- `x_offset` / `y_offset`: Position adjustment
- `font_name`: Font file (e.g., "arial.ttf")

**Features:**
- Multiple pattern types (single, grid, diagonal, dense)
- Full rotation control
- Bold and italic text support
- Custom spacing and positioning
- Automatic font variant detection (arialbd.ttf, ariali.ttf, etc.)

**Stock Photo Style Settings:**
- `pattern_type`: diagonal
- `rotation`: -45
- `opacity`: 0.15-0.3
- `bold`: true
- `spacing_x/y`: 350-500

**Use Cases:**
- Protect images from unauthorized use
- Professional watermarking workflows
- Copyright notices
- Branding

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

### Example 6: Watermark + Clean Save Workflow

Create watermarked and clean versions simultaneously.

**Workflow:**
```
┌──────────────┐
│ Generate     │
│ Image        │
└──────┬───────┘
       │
       ├─────────────────────────┐
       │                         │
┌──────▼────────────────┐   ┌────┴──────┐
│ Advanced Repeating    │   │ (Bypass)  │
│ Watermark             │   └────┬──────┘
│ - pattern: diagonal   │        │
│ - rotation: -45       │        │
│ - text: "© 2025"      │        │
└──────┬────────────────┘        │
       │ watermarked             │ clean
       │                         │
       └────────┬────────────────┘
                │
    ┌───────────▼──────────────────┐
    │ Multi-Save Image (Clean)     │
    │ - image_1: watermarked       │
    │ - save_path_1: [WM] folder   │
    │ - image_2: clean             │
    │ - save_path_2: [NO WM] folder│
    │ - use_exiftool: true         │
    └──────────────────────────────┘
```

**Result:** Automatically saves watermarked version to one folder, clean version to another, both with metadata stripped!

### Example 7: Symmetrical Masking for Portraits

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

### Example 8: Ultimate Control (All Nodes Combined)

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
- Save with watermark + clean version simultaneously
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

### Watermarking Tips

**Stock Photo Style:**
- `pattern_type`: diagonal
- `rotation`: -45
- `opacity`: 0.15-0.3
- `bold`: true
- `spacing_x/y`: 350-500

**Security (Heavy Watermarking):**
- `pattern_type`: dense_grid
- `opacity`: 0.4-0.6
- `spacing_x/y`: 200-300

**Subtle Branding:**
- `pattern_type`: single
- `opacity`: 0.2-0.3
- Adjust with `x_offset`/`y_offset` for corner placement

### Multi-Save Tips

**Maximum Metadata Removal:**
1. Download exiftool from https://exiftool.org/
2. Place `exiftool.exe` in ComfyUI root
3. Enable `use_exiftool` in node
4. Two-stage removal ensures complete cleaning

**Without exiftool:**
- Still removes most metadata via PIL
- Good enough for most use cases
- Enable if sharing images publicly

**Filename Organization:**
- Use descriptive prefixes: "watermarked", "clean", "final"
- Suffixes for variants: "v1", "exported", "web"
- Timestamps automatically added

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

**Issue:** Watermarks not showing or wrong position
- **Solution:**
  - Check opacity isn't too low
  - Verify `pattern_type` is not "single" if you want repeating
  - Adjust `spacing_x/y` if too sparse
  - Check `rotation` isn't making text unreadable

**Issue:** Multi-Save not removing metadata
- **Solution:**
  - Download and install exiftool.exe in ComfyUI root
  - Enable `use_exiftool=true`
  - Check file permissions on save directories
  - Verify paths are correct and writable

**Issue:** ControlNet effect too strong/weak everywhere
- **Solution:**
  - Adjust `base_strength` in Multi-Mask Combiner
  - Check `strength` value on Apply Advanced ControlNet node
  - Verify `start_strength` and `end_strength` values in Curved Timestep Keyframes

## 📋 Requirements

- ComfyUI
- [ComfyUI-Advanced-ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet) (for ControlNet nodes)
- Python packages: `matplotlib`, `pillow`, `numpy`, `torch`, `rembg`

**Optional but Recommended:**
- `exiftool.exe` for thorough metadata removal (Multi-Save node)
- Place in ComfyUI root directory
- Download from https://exiftool.org/

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
