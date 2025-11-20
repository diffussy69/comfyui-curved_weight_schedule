# ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, regional prompting, and image utilities for ComfyUI. Control your ControlNet strength across time and space with precision and visual feedback, plus powerful masking and regional prompting tools.

## 🌟 Features

### ControlNet Scheduling
- **Curved ControlNet Scheduler**: Schedule ControlNet strength across generation steps with multiple curve types
- **Advanced Curved ControlNet Scheduler**: Feature-rich version with presets, custom formulas, curve blending, and more
- **Multi-ControlNet Curve Coordinator**: 🌟 NEW! Coordinate up to 4 ControlNet curves simultaneously with independent timing
- **Curved Blur Batch Preprocessor**: ⭐ Generate batches of progressively blurred images following curves
- **Batch Images to Timestep Keyframes**: ⭐ Map blur batches to ControlNet timestep keyframes
- **Curve Formula Builder**: Beginner-friendly pattern builder - select shapes and adjust sliders!
- **Visual Curve Designer**: Plot control points with numeric inputs for precise curves
- **Interactive Curve Designer**: 🎨 Draw curves with your mouse on an interactive canvas!
- **Visual Feedback**: Real-time graph preview showing your strength curve
- **Multi-Mask Strength Combiner**: Apply different ControlNet strengths to different regions of your image

### Regional Prompting & Masking
- **Multi-Layer Mask Editor**: 🎨 NEW! Interactive canvas-based mask editor with multiple layers
- **Regional Prompting**: Use different text prompts for different masked areas
- **Regional Prompt Interpolation**: Smooth gradient transitions between different prompts
- **Mask Symmetry Tool**: Mirror masks across axes for symmetrical compositions
- **Auto Person Mask**: AI-powered automatic person/foreground detection and masking
- **Auto Background Mask**: Automatic background masking (inverted person mask)

## 🎯 Choose Your Curve Creation Method

Different tools for different skill levels and preferences:

| Method | Best For | Skill Level | Interface |
|--------|----------|-------------|-----------|
| **Presets** | Quick workflows | 🟢 Beginner | Dropdown menu |
| **Curve Formula Builder** | Pattern-based curves | 🟢 Beginner | Sliders + patterns |
| **Visual Curve Designer** | Precise coordinates | 🟡 Intermediate | Number inputs |
| **Interactive Canvas** 🎨 | Drawing curves | 🟢 Beginner | Mouse drawing |
| **Custom Formulas** | Mathematical curves | 🔴 Advanced | Code/math |

**Recommendation:** Start with **Interactive Canvas** or **Presets** for the easiest experience!

## 📦 Installation

1. Navigate to your ComfyUI custom nodes directory:
```bash
cd ComfyUI/custom_nodes/
```

2. Clone this repository:
```bash
git clone https://github.com/diffussy69/comfyui-curved_weight_schedule.git
```

3. Clone Kosinkadink's repository (Advanced ControlNet):
```bash
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git
```

4. Install dependencies (if not already installed):
```bash
pip install matplotlib pillow numpy torch scipy
```

5. Restart ComfyUI

**That's it!** ✨ The JavaScript UI extension is included automatically. Presets will update UI fields instantly with no additional setup required!

### 🎉 What You Get Out of the Box

When you select a preset:
- ✅ **All UI fields update automatically** - No manual adjustments needed
- ✅ **True one-click experience** - Select "Fade Out" and watch it apply instantly
- ✅ **Visual confirmation** - See exactly what values are being used
- ✅ **No confusion** - What you see is what you get!

**Before (old behavior):**
```
Select "Fade Out" → UI fields don't change → Confusing 😕
```

**After (with this version):**
```
Select "Fade Out" → All fields update instantly → Perfect! ✨
```

### Verification

After installing and restarting:
1. Hard refresh browser (Ctrl+Shift+F5 / Cmd+Shift+R)
2. Add the Advanced Curved ControlNet Scheduler node
3. Select any preset (like "Fade Out")
4. Watch the UI fields update automatically! 🎊
5. Optional: Check browser console (F12) for success messages

The nodes will appear in:
- `conditioning/controlnet` → Curved ControlNet Scheduler, Advanced Curved ControlNet Scheduler, Multi-ControlNet Curve Coordinator, Curve Formula Builder, Visual Curve Designer, Interactive Curve Designer 🎨
- `ControlNet Preprocessors/tile` → Curved Blur (Batch) ⭐ NEW!
- `ControlNet/Keyframing` → Batch Images to Timestep Keyframes ⭐ NEW!
- `mask` → Multi-Layer Mask Editor, Multi-Mask Strength Combiner, Mask Symmetry Tool
- `conditioning` → Regional Prompting, Regional Prompt Interpolation

## 🎯 Node Overview

### 1. Curved ControlNet Scheduler (Original)

Control ControlNet strength across generation steps using mathematical curves.

**Key Parameters:**
- `num_keyframes`: Number of control points (2-100)
- `start_percent` / `end_percent`: When to start/stop the curve (0.0-1.0)
- `start_strength` / `end_strength`: Strength values at start and end (YOU control the direction)
- `curve_type`: Shape of the strength transition
- `curve_param`: Controls transition speed/steepness (higher = more extreme)
- `invert_curve`: Flip the curve shape
- <img width="1029" height="752" alt="image" src="https://github.com/user-attachments/assets/49c76b2e-44a7-4669-aa93-aabc4aff3c10" />

**Available Curve Types:**
- `linear`: Straight line transition
- `ease_in`: Slow start, fast end (accelerating)
- `ease_out`: Fast start, slow end (decelerating)
- `ease_in_out`: Slow start and end, fast middle (smooth S-curve)
- `sine_wave`: Oscillating control (experimental)
- `bell_curve`: Peak in middle, low at edges
- `reverse_bell`: Low in middle, high at edges
- `exponential`: Dramatic exponential curve
- `bounce`: Bouncing effect
- `custom_bezier`: Customizable bezier curve

**Outputs:**
- `TIMESTEP_KF`: Connect to Apply Advanced ControlNet's timestep_kf input
- `curve_graph`: Visual preview (connect to Preview Image)

### 2. Advanced Curved ControlNet Scheduler

Enhanced version with powerful new features for maximum control and flexibility.

**All Original Features Plus:**

#### 🎨 Preset System
- **9 Pre-configured Presets**: Quick one-click setups (with optional JS extension for automatic UI updates!)
  - `Fade Out`: Strong start → weak end (composition lock)
  - `Fade In`: Weak start → strong end (detail refinement)
  - `Peak Control`: Peaks in middle (bell curve strength)
  - `Valley Control`: Strong edges, weak middle
  - `Strong Start+End`: Bookend control
  - `Oscillating`: Wave pattern control
  - `Exponential Decay`: Dramatic fade
  - `Smooth Transition`: Gentle S-curve
  - `Custom`: Manual configuration

> **💡 Pro Tip:** Install the JavaScript extension (see Installation section) to make presets automatically update all UI fields for a truly seamless experience!

#### 🔢 Advanced Easing Functions
- **Professional animation easing curves**:
  - `ease_in/out/in_out_quad` (quadratic)
  - `ease_in/out/in_out_cubic` (cubic)
  - `ease_in/out/in_out_quart` (quartic)
- More precise control over acceleration/deceleration

#### 🧮 Custom Formula Support
- **Mathematical Expression Input**
  - Use custom formulas with variable `t` (0 to 1)
  - Examples: `sin(t*3.14)`, `t**2`, `1-exp(-5*t)`
  - Safe evaluation with whitelisted functions
  - Supports: sin, cos, tan, exp, log, sqrt, abs, pi, e, numpy operations

#### 🎛️ Curve Modulation
- **Mirror Curve**: Create symmetrical curves around midpoint
- **Repeat Curve**: Repeat the pattern 1-10 times for multi-segment control
- **Adaptive Keyframes**: Automatically place more keyframes where curve changes rapidly
- **Curve Blending**: Mix two different curve types
  - Blend between any two curve types
  - Adjustable blend amount (0.0-1.0)

#### 📊 Enhanced Features
- **A/B Comparison**: Show two curves side-by-side for visual comparison
- **CSV Export**: Save curve data for reuse and sharing
- **Curve Statistics Output**: Detailed stats (average, max, min, area under curve, rate of change)
- **Step Mode**: Use absolute steps instead of percentages
- **Comparison Graphs**: Overlay multiple curves for testing

**New Parameters:**
- `preset`: Quick preset selection
- `mode`: "percent" or "steps"
- `total_steps`: For step mode (1-10000)
- `custom_formula`: Math expression for custom curves
- `mirror_curve`: Create symmetrical curves
- `repeat_curve`: Repeat pattern N times
- `adaptive_keyframes`: Smart keyframe distribution
- `blend_curve_type`: Second curve for blending
- `blend_amount`: Blend strength (0.0-1.0)
- `comparison_curve`: Show comparison curve
- `save_curve`: Export to CSV
- `curve_filename`: Export filename

**Additional Outputs:**
- `curve_stats`: TEXT output with detailed statistics

**Use Cases:**
- **Quick Workflows**: Use presets for instant results
- **Experimentation**: Try comparison curves before committing
- **Complex Patterns**: Repeat and mirror for intricate schedules
- **Data Analysis**: Export curves for documentation and sharing
- **Custom Curves**: Write any mathematical function you can imagine

### 3. Multi-ControlNet Curve Coordinator 🌟

**NEW!** Coordinate multiple ControlNet curves simultaneously with independent timing windows. Perfect for complex multi-ControlNet workflows where you need different curves with different timing for each ControlNet model.

**Key Features:**
- **Up to 4 Independent Slots**: Each with its own complete curve configuration
- **Per-Slot Timing**: Each slot has independent `start_percent` and `end_percent`
- **Visual Coordination**: Combined graph shows all curves with shaded active windows
- **All Curve Types**: Full access to all curve types and presets per slot
- **Clean Organization**: Visual dividers separate each slot's settings

**Slot Parameters (A, B, C, D):**
- `enable_slot_X`: Toggle slot on/off
- `start_percent_X` / `end_percent_X`: **Independent timing window** for this slot
- `preset_X`: Quick preset selection (Fade Out, Fade In, Peak Control, etc.)
- `curve_type_X`: Shape of the curve
- `start_strength_X` / `end_strength_X`: Strength range
- `curve_param_X`: Curve steepness/shape parameter

**Outputs:**
- `SLOT_A`, `SLOT_B`, `SLOT_C`, `SLOT_D`: Individual TIMESTEP_KF outputs
- `combined_graph`: Visual preview showing all active curves overlaid with shaded windows
- `info`: Text summary of all active slots

**Powerful Workflow Patterns:**

*Sequential Control:*
```
Slot A (Canny):    [0.0-0.3]  Fade Out  → Early composition lock
Slot B (Depth):    [0.3-0.7]  Fade In   → Mid-gen structure
Slot C (Tile):     [0.7-1.0]  Peak      → Late detail refinement
```

*Overlapping Transitions:*
```
Slot A (Canny):    [0.0-0.5]  Fade Out  → Gradually release
Slot B (Depth):    [0.3-0.8]  Fade In   → Cross-fade overlap
```

*Targeted Bursts:*
```
Slot A (Line):     [0.0-0.2]  Strong    → Quick early guide
Slot B (Tile):     [0.8-1.0]  Peak      → Final polish only
```

**How to Use:**
1. Configure each slot with its own curve and timing
2. Connect each SLOT output to its own "Apply Advanced ControlNet" node
3. Each Apply node uses a different ControlNet model
4. Chain them: First Apply's positive/negative → Second Apply → Third Apply → KSampler
5. View `combined_graph` to see how all curves interact

**Pro Tips:**
- Use shaded regions in the graph to visualize when each ControlNet is active
- Overlapping windows create smooth transitions between different controls
- Non-overlapping windows create distinct phases
- Disable unused slots to reduce clutter
<img width="882" height="832" alt="image" src="https://github.com/user-attachments/assets/33653f85-a6d7-4e28-ac9e-38e6ddd0f432" />


### 4. Curved Blur Batch Preprocessor ⭐ NEW v3.2!

**The missing piece for dynamic tile ControlNet workflows!**

Creates a batch of images with progressively varying Gaussian blur following mathematical curves. Pair this with the Batch Images to Timestep Keyframes node to synchronize blur progression with your ControlNet strength curves.
<img width="970" height="774" alt="image" src="https://github.com/user-attachments/assets/2858f0b3-2e7d-4642-8cac-4398eaab4064" />

**What It Does:**
Takes a single image and generates multiple versions with different blur amounts, perfect for pairing with ControlNet tile models. Low blur = more structure preserved, high blur = more creative freedom for the AI.

**Key Parameters:**
- `image`: Input image to process
- `num_keyframes`: How many blur variations to create (2-200)
  - **⚠️ MUST MATCH the num_keyframes in your ControlNet Scheduler!**
- `start_percent` / `end_percent`: Timeline range (0.0-1.0)
- `start_sigma` / `end_sigma`: Gaussian blur sigma values
  - **0.0-0.5**: Minimal blur (almost sharp)
  - **0.5-2.0**: Light blur
  - **2.0-6.0**: Moderate blur
  - **6.0-12.0**: Heavy blur
  - **12.0+**: Extreme blur
- `curve_type`: Same curve options as the scheduler
- `curve_param`: Curve steepness/shape control
- `show_graph`: Display blur curve visualization

**Outputs:**
- `batch_images`: Batch of K blurred images (K,H,W,C)
- `curve_graph`: Visual preview of blur progression
- `stats`: Text summary of blur schedule

**Technical Notes:**
- Uses proper Gaussian blur with 3-sigma kernel sizing
- Separable filter implementation for efficiency
- Reflect padding to prevent edge darkening
- Sigma = 0 produces identity (no blur)

**Typical Workflow:**
```
[Load Image]
    ↓
[Curved Blur Batch Preprocessor]
    num_keyframes: 10
    start_sigma: 0.5 (sharp)
    end_sigma: 8.0 (blurry)
    curve_type: ease_out
    ↓
[Batch Images to Timestep Keyframes]
    (see next node)
```

### 5. Batch Images to Timestep Keyframes ⭐ NEW v3.2!

**The bridge between dynamic blur and ControlNet scheduling.**

Maps a batch of images to existing ControlNet timestep keyframes by index. This is the "glue" that connects your blur progression with ControlNet strength curves.
<img width="970" height="774" alt="image" src="https://github.com/user-attachments/assets/1cc271b1-dad7-4aa3-900d-cad10ccffbb5" />

**What It Does:**
Takes the batch of blurred images from the Curved Blur Preprocessor and attaches each image to the corresponding keyframe created by your scheduler. Image 0 goes to keyframe 0, image 1 to keyframe 1, etc.

**Key Parameters:**
- `images`: Batch of images from Curved Blur Preprocessor
- `prev_timestep_kf`: Keyframes from Advanced Curved Scheduler
- `print_keyframes`: Debug option to see mapping in console

**Outputs:**
- `timestep_kf`: Updated keyframes with images attached
- `info`: Summary of mapping operation

**Important Notes:**
- ⚠️ **Match keyframe counts!** `num_keyframes` in both Curved Blur and Curved Scheduler must be identical
- Images are mapped by index: `keyframe[i]` ← `image[i]`
- Automatically warns if counts don't match
- Works across different ComfyUI-Advanced-ControlNet API versions with automatic compatibility handling

**Complete Workflow:**
```
[Load Image]
    ↓
[Curved Blur Batch Preprocessor]
    num_keyframes: 10
    start_sigma: 0.5
    end_sigma: 8.0
    curve_type: ease_out
    ↓
[Advanced Curved ControlNet Scheduler]
    num_keyframes: 10  ← MUST MATCH!
    start_strength: 1.0
    end_strength: 0.3
    curve_type: ease_out
    ↓
[Batch Images to Timestep Keyframes]
    images: from Curved Blur
    prev_timestep_kf: from Scheduler
    ↓
[Load ControlNet Model]
    model: tile_controlnet
    ↓
[Apply Advanced ControlNet]
    timestep_keyframe: from Batch mapper
    ↓
[KSampler]
    Generate!
```

**Result Explanation:**

*Early in generation (0-20%):*
- **Sharp image (sigma 0.5)** + **Strong ControlNet (1.0)** = Strict adherence to composition

*Mid generation (20-60%):*
- **Increasing blur (sigma 2-5)** + **Decreasing strength (0.7-0.5)** = Balanced guidance

*Late generation (60-100%):*
- **Heavy blur (sigma 6-8)** + **Weak ControlNet (0.3)** = Creative freedom for details

### 6. Curve Formula Builder

**Beginner-friendly curve creator - no math knowledge required!**

Build custom curves using pre-made patterns with simple sliders. Perfect for learning and experimentation without needing to understand mathematical formulas.

**Pattern Types:**
- **Fade In/Out**: Simple transitions
- **S-Curve**: Smooth acceleration/deceleration
- **Wave**: Oscillating patterns
- **Spike**: Sharp peaks
- **Bell**: Center emphasis
- **Valley**: Edge emphasis
- **Step**: Abrupt changes
- **Exponential**: Dramatic transitions
- **Bounce**: Elastic effects

**Key Parameters:**
- `pattern_type`: Choose your curve pattern
- `intensity`: Control the dramatic effect (0.1-5.0)
- `phase_shift`: Move the pattern left/right (0-360°)
- `cycles`: Number of repetitions (1-10)
- `num_points`: Curve resolution (10-200)
- `show_preview`: Visual graph output

**Outputs:**
- `formula`: TEXT output - copy this to Advanced Scheduler's custom_formula
- `preview_graph`: Visual representation of your curve
- `curve_values`: Raw numeric values for advanced use

**How to Use:**
1. Select a pattern_type
2. Adjust intensity slider
3. Preview the graph
4. Copy the generated formula
5. Paste into Advanced Curved ControlNet Scheduler's custom_formula field

**Pro Tips:**
- Start with intensity=1.0 and adjust from there
- Use phase_shift to offset patterns without recreating
- Combine with Advanced Scheduler's blend feature for complex curves
- Export formulas to a text file for your personal library

### 7. Visual Curve Designer

**Point-based curve creation with numeric precision.**

Define curves by specifying exact control point coordinates. Perfect when you know exactly what values you want at specific times.

**Key Parameters:**
- `point_1` through `point_10`: (x, y) coordinate pairs
  - x: Timeline position (0.0-1.0)
  - y: Strength value (0.0-1.0)
- `num_active_points`: How many points to use (2-10)
- `interpolation_method`: How to connect points
  - `linear`: Straight lines between points
  - `spline`: Smooth curves through points
  - `cubic`: Cubic interpolation
- `normalize_y`: Auto-scale y values to 0-1 range
- `num_keyframes`: Output resolution (2-200)

**Outputs:**
- `TIMESTEP_KF`: Keyframes for ControlNet
- `curve_graph`: Visual preview
- `point_data`: TEXT summary of coordinates

**Use Cases:**
- Precise timing requirements
- Replicating specific curves from data
- Mathematical precision needed
- Building libraries of exact curves

### 8. Interactive Curve Designer 🎨

**The most intuitive way to create curves - draw with your mouse!**

Click and drag on an interactive canvas to create custom curves visually. No numbers, no formulas - just draw what you want!

**Features:**
- **Click-and-drag interface**: Directly manipulate curves
- **Real-time preview**: See changes instantly
- **Visual control points**: Coordinate labels show exact values
- **Quick actions**:
  - `Symmetry`: Mirror your curve around center
  - `Invert`: Flip curve vertically
  - `Clear`: Start fresh
  - `Reset`: Return to default
- **Interpolation methods**: Linear, spline, or cubic
- **Auto-formula generation**: Exports mathematical formula

**Key Parameters:**
- `canvas_width` / `canvas_height`: Drawing area size
- `num_control_points`: How many points to place (2-20)
- `interpolation`: Connection method
- `show_coordinates`: Display point values
- `grid_lines`: Visual guides
- `num_keyframes`: Output resolution (2-200)

**Outputs:**
- `TIMESTEP_KF`: Keyframes for ControlNet
- `curve_canvas`: Interactive drawing surface
- `curve_graph`: Standard preview
- `formula_output`: Generated formula for reuse

**How to Use:**
1. Open the Interactive Curve Designer node
2. Click on canvas to place control points
3. Drag points to adjust curve shape
4. Use quick action buttons as needed
5. Connect output to Apply Advanced ControlNet

**Pro Tips:**
- Start with fewer points (5-8), add more if needed
- Use symmetry for fade-in-fade-out effects
- Enable grid_lines for precise alignment
- Save formula_output for your favorite curves

### 9. Multi-Layer Mask Editor

🎨 Interactive canvas-based mask editor with multiple layers, pan/zoom, and professional painting tools. Perfect for creating complex masks with separate elements.

**Key Features:**
- **Multiple layers**: Up to 10 independent mask layers
- **Layer management**: Toggle visibility, reorder, add/remove layers
- **Professional tools**: Paint/erase with adjustable brush size
- **Pan & zoom**: Navigate high-resolution images easily
- **Layer fill**: Quickly fill or clear entire layers
- **Color-coded layers**: Each layer has a unique color for easy identification
- **Real-time preview**: See all layers composited together

**Key Parameters:**
- `image`: Base image to paint masks on
- `num_layers`: Number of mask layers (1-10)
- `masks_data`: Stored mask data (auto-managed)

**Controls:**
- **Paint/Erase**: Toggle between adding and removing mask
- **Brush Size**: Adjust from 1-200px
- **Fill Layer**: Fill entire layer based on Paint/Erase mode
- **Mouse wheel**: Zoom in/out
- **Space + Drag** or **Middle click + Drag**: Pan around canvas
- **Layer visibility toggle**: Show/hide individual layers

**Outputs:**
- `layer_1` through `layer_10`: Individual layer masks
- `combined_mask`: All visible layers merged together

**Use Cases:**
- Multi-character masking with separate layers per character
- Complex inpainting with isolated regions
- Architectural elements (walls, floors, ceiling as separate layers)
- Object-specific regional prompting
- Iterative mask refinement without losing previous work

**How to Use:**
1. Upload a base image
2. Click "Open Mask Editor"
3. Select a layer from the layer panel
4. Paint your mask using the canvas
5. Add more layers as needed for different regions
6. Toggle layer visibility to check individual masks
7. Save and use output masks in your workflow

**Pro Tips:**
- Use different layers for each distinct element
- Toggle layer visibility to focus on one mask at a time
- Start with lower zoom for broad strokes, zoom in for details
- Use Fill Layer to quickly block out large areas
- Combined mask output is perfect for simple workflows
- Individual layer outputs allow maximum control downstream

### 10. Multi-Mask Strength Combiner

Apply different ControlNet strengths to different regions of your image using masks.

**Key Parameters:**
- `base_strength`: Default strength for unmasked areas
- `mask_1` through `mask_8`: Region masks
- `strength_1` through `strength_8`: Strength per mask
- `blend_mode`: How masks interact
- `normalize_output`: Auto-balance strengths

**Outputs:**
- `TIMESTEP_KF`: Combined keyframes
- `strength_map`: Visual representation

**Use Cases:**
- Emphasize subject over background
- Different strengths for different objects
- Gradual strength transitions
- Complex multi-region control

### 11. Regional Prompting

Use different text prompts for different masked areas.

**Key Parameters:**
- `base_prompt`: Default prompt
- `region_1` through `region_4`: Area masks
- `prompt_1` through `prompt_4`: Per-region prompts
- `region_strength`: Influence of regional prompts

**Outputs:**
- `conditioning`: Combined prompt conditioning

### 12. Regional Prompt Interpolation

Create smooth transitions between different prompts using gradient masks.

**Key Parameters:**
- `prompt_a` / `prompt_b`: Start and end prompts
- `mask_a` / `mask_b`: Region definitions
- `interpolation_steps`: Smoothness (3-20)
- `transition_mode`: linear, smooth, ease_in_out
- `direction`: auto, horizontal, vertical, radial

**Outputs:**
- `conditioning`: Interpolated conditioning
- `gradient_mask`: Visual transition preview

### 13. Mask Symmetry Tool

Mirror masks across axes for symmetrical compositions.

**Key Parameters:**
- `mask`: Input mask
- `symmetry_mode`: horizontal, vertical, both, radial_4way
- `blend_mode`: How to combine mirrors
- `blend_strength`: Mixing amount
- `invert_mirrored`: Create negative space

**Outputs:**
- `mask`: Symmetrical result
- `preview`: Visual representation

### 14. Auto Person Mask & Auto Background Mask

AI-powered automatic segmentation for quick masking.

**Outputs:**
- `mask`: Person or background mask
- `preview`: Visual confirmation

## 💡 Usage Tips & Workflows

### Dynamic Blur + Strength Workflow ⭐ NEW!

**The Power Combination for Tile ControlNet:**

This workflow gives you synchronized control over both blur and ControlNet strength, perfect for maintaining composition while allowing creative freedom.

**Recommended Settings for Composition Lock:**
```
Curved Blur Batch Preprocessor:
- num_keyframes: 10
- start_sigma: 0.5 (sharp)
- end_sigma: 8.0 (blurred)
- curve_type: ease_out

Advanced Curved ControlNet Scheduler:
- num_keyframes: 10 (MATCH!)
- start_strength: 1.0 (strong)
- end_strength: 0.3 (weak)
- curve_type: ease_out
```

**Result:** Strong compositional adherence early (sharp + strong) transitioning to creative detail generation late (blurry + weak).

**Recommended Settings for Detail Refinement:**
```
Curved Blur Batch Preprocessor:
- start_sigma: 8.0 (blurred)
- end_sigma: 0.5 (sharp)
- curve_type: ease_in

Advanced Curved ControlNet Scheduler:
- start_strength: 0.3 (weak)
- end_strength: 1.0 (strong)
- curve_type: ease_in
```

**Result:** Creative freedom early, then lock in details as generation progresses.

**Coordinating Curves:**

You can use **different curve types** for blur vs. strength:
- Blur: `ease_out` (sharp → blurred)
- Strength: `exponential` (strong fade)
- Result: Extra emphasis on early composition control

Or use **matching curves** for synchronized progression:
- Both: `ease_in_out`
- Result: Smooth, balanced transition

**Critical Reminder:** ⚠️ Always match `num_keyframes` between Curved Blur and Scheduler!

### Curve Selection Guide

**For Fade Out (Strong → Weak):**
- Presets: "Fade Out" or "Exponential Decay"
- Curve: ease_out, exponential
- Use case: Lock composition, let details emerge

**For Fade In (Weak → Strong):**
- Presets: "Fade In"
- Curve: ease_in
- Use case: Rough sketch → detailed refinement

**For Peak Control:**
- Presets: "Peak Control"
- Curve: bell_curve
- Use case: Strong control in middle steps

**For Smooth Transitions:**
- Presets: "Smooth Transition"
- Curve: ease_in_out
- Use case: Natural, organic progression

**For Experimental:**
- Presets: "Oscillating"
- Curve: sine_wave, bounce
- Use case: Wave patterns, bouncing effects

### Custom Formula Examples

**Delayed Fade:**
```
1 if t < 0.3 else 1 - ((t-0.3)/0.7)**2
```
Stay at full strength until 30%, then fade

**Sharp Drop:**
```
exp(-8*t)
```
Exponential decay, very dramatic

**Double Peak:**
```
sin(t*6.28)*0.5 + 0.5
```
Full wave cycle, oscillates twice

**Ease Out Cubic:**
```
1 - (1-t)**3
```
Cubic easing, very smooth

### Preset Combinations

**Photobash Workflow:**
1. Load reference image
2. Curved Blur: sharp → blurred (ease_out)
3. Use "Fade Out" preset
4. Strong early adherence, creative details

**Detail Enhancement:**
1. Load rough generation
2. Curved Blur: blurred → sharp (ease_in)
3. Use "Fade In" preset
4. Refine and sharpen progressively

**Oscillating Experiments:**
1. Any input
2. Curved Blur: sine_wave
3. Use "Oscillating" preset
4. Wave pattern for creative effects

### Multi-Mask Strength Tips

**Region Priority:**
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

## 🛠 Troubleshooting

**Issue: ControlNet not working at all / no effect**
- ⚠️ **Solution**: Check your Advanced ControlNet node settings!
  - Set `strength` to **1.00**
  - Set `start_percent` to **0.000**
  - Set `end_percent` to **1.000**
  - These settings must be correct for the scheduler to work!

**Issue: Blur not applying or all images look the same** ⭐ NEW
- **Solution**: 
  - Verify `start_sigma` ≠ `end_sigma` in Curved Blur node
  - Check that `num_keyframes` matches between Curved Blur and Scheduler
  - Enable `show_graph` to verify curve is not flat
  - Look for console warnings about keyframe mismatches

**Issue: "Keyframe count mismatch" warning** ⭐ NEW
- **Solution**:
  - Set identical `num_keyframes` in both Curved Blur and Scheduler nodes
  - Only the minimum count will be used if they differ
  - Check console output to see how many keyframes were actually mapped

**Issue: Blur progression not visible in generation** ⭐ NEW
- **Solution**:
  - Ensure Batch Images to Timestep Keyframes node is connected
  - Verify ControlNet model is tile_controlnet (or compatible tile model)
  - Check that Apply Advanced ControlNet is using the timestep_kf from the Batch mapper
  - Try increasing sigma range (e.g., 0.5 to 12.0 instead of 2.0 to 6.0)

**Issue: Curve going in wrong direction**
- Solution: The curve shape is correct, but swap your `start_strength` and `end_strength` values
- Remember: Curve types control SHAPE, not direction

**Issue: Graph not showing**
- Solution: Make sure matplotlib is installed: `pip install matplotlib`
- Set show_graph=false if you don't need it

**Issue: Custom formula not working**
- Solution:
  - Check syntax - use `t` as the variable
  - Make sure formula evaluates to numbers between 0-1 (auto-normalized)
  - Avoid forbidden operations (import, exec, eval)
  - Test with simple formulas first: `t**2`, `sin(t*3.14)`

**Issue: Preset UI fields not updating**
- **Solution**: Make sure you restarted ComfyUI after installation
  - Hard refresh browser (Ctrl+Shift+F5 / Cmd+Shift+R)  
  - Check browser console (F12) - you should see `✅ Node patched successfully!`
  - If you don't see that message, the extension may not have loaded
  - Verify `/web/advanced_curved_scheduler.js` exists in your node folder
- Alternative: Presets still work without UI updates - values are applied internally
  - Check browser console (F12) for `✅ Preset applied successfully!` message when changing presets
  - The correct values ARE being used even if UI doesn't update visually

**Issue: Masks not affecting output**
- Solution:
  - Check that masks are actually painted (not empty)
  - Verify mask is connected to correct input
  - Try increasing strength values
  - Verify Advanced ControlNet base strength is 1.0

**Issue: Effect too weak everywhere**
- Solution:
  - Check Advanced ControlNet `strength` setting (should be 1.0)
  - Increase `start_strength` and `end_strength` values in scheduler
  - Increase `base_strength` in Multi-Mask Strength Combiner
  - For blur workflows: decrease sigma values (more sharp = more control)

**Issue: Effect too strong everywhere**
- Solution:
  - Decrease `start_strength` and `end_strength` values
  - Decrease individual mask strengths in Multi-Mask Combiner
  - Check that Advanced ControlNet strength isn't multiplying your values
  - For blur workflows: increase sigma values (more blur = less control)

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

**Issue: Interpolation not visible**
- Solution:
  - Increase interpolation_steps (try 10-15)
  - Use transition_mode=smooth for more obvious gradients
  - Check that masks are positioned to allow transition zones

**Issue: CSV export not working**
- Solution:
  - Check file permissions in ComfyUI/output/curves directory
  - Verify save_curve is set to True
  - Check console for error messages

## 📋 Requirements

- ComfyUI
- ComfyUI-Advanced-ControlNet (required)
- Python packages: matplotlib, pillow, numpy, torch, scipy

## 🆕 What's New

### Version 3.3 - Multi-ControlNet Coordination 🎯
- **🌟 MAJOR: Multi-ControlNet Curve Coordinator** - Coordinate multiple ControlNets simultaneously!
  - Manage up to 4 independent ControlNet curves in one node
  - **Per-slot timing**: Each slot has its own start_percent and end_percent
  - Visual dividers for clean organization
  - Combined graph with shaded active windows
  - All curve types and presets available per slot
  - Perfect for complex multi-ControlNet workflows
- **✨ Use Cases**:
  - Sequential control: Different CNs at different stages
  - Overlapping transitions: Smooth handoffs between controls
  - Targeted bursts: Activate specific CNs only when needed
  - Coordinated effects: Visualize how multiple curves interact
- **🐛 Bug Fixes**:
  - Fixed bell_curve and oscillating presets (were showing flat lines)
  - Updated all curve presets to use proper start/end strength values

### Version 3.2 - Dynamic Blur Workflow 🌊
- **🌊 MAJOR: Curved Blur Batch Preprocessor** - Sync blur with ControlNet scheduling!
  - Generate batches of progressively blurred images following curves
  - Gaussian blur with proper 3-sigma kernels and reflect padding
  - Full curve type support matching the scheduler
  - Visual graph preview of blur progression
  - Sigma range from 0.0 (sharp) to 32.0+ (extreme blur)
  - Perfect for tile ControlNet workflows
- **🔗 Batch Images to Timestep Keyframes** - The missing link!
  - Maps blur batches directly to ControlNet keyframes
  - Automatic API compatibility across different Advanced ControlNet versions
  - Smart warnings for mismatched keyframe counts
  - Seamless integration with existing workflow
- **🎯 Complete Workflow Integration**:
  - Synchronize blur progression with strength curves
  - Lock composition early, creative freedom late
  - Or reverse: rough start, detailed refinement
  - Mix and match curve types for blur vs strength
- **⚡ Technical Improvements**:
  - Robust fallback handling for TimestepKeyframe imports
  - Better error messages and user warnings
  - Improved graph generation with graceful failure handling
  - Zero blur (sigma=0) optimization

### Version 3.0 - Interactive Curve Designer 🎨
- **🎨 MAJOR: Interactive Curve Designer** - Draw curves with your mouse!
  - Click and drag interface on an interactive canvas
  - Real-time curve preview as you draw
  - Visual control points with coordinate labels
  - Quick actions: Symmetry, Invert, Clear, Reset
  - Multiple interpolation methods
  - Auto-generates formulas from your drawings
  - **The most intuitive way to create curves!**
- **📊 Visual Curve Designer** - Point-based curve creation
  - Define up to 10 control points with numeric inputs
  - Three interpolation methods (linear, spline, cubic)
  - Precise coordinate control
  - Perfect for mathematical precision
- **🐛 Bug Fixes**:
  - Fixed bell curve and sine wave presets (were showing flat lines)
  - Improved preset handling for pattern-based curves
  - Better normalization for oscillating curves

### Version 2.2 - Curve Formula Builder
- **🎨 NEW: Curve Formula Builder** - Beginner-friendly visual curve creator!
  - Build custom curves without any math knowledge
  - 9 pre-made pattern types with simple sliders
  - Live preview graph shows your curve in real-time
  - Generates formulas for use in Advanced Scheduler
  - Perfect for experimentation and learning

### Version 2.1 - UI Enhancement Update
- **🎨 JavaScript UI Extension** - Now included automatically!
  - Automatic UI field updates when selecting presets
  - True one-click preset experience
  - Visual confirmation of preset application
  - No manual installation required - works out of the box!
- **📚 Enhanced Documentation** - Clearer installation and usage guides

### Version 2.0 - Advanced Curved ControlNet Scheduler
- **9 built-in presets** for instant workflows
- **Custom formula support** - write any mathematical curve
- **Professional easing functions** - quad, cubic, quart variants
- **Curve blending** - mix two curve types
- **Adaptive keyframes** - smart distribution based on curve steepness
- **A/B comparison** - compare curves side-by-side
- **CSV export** - save and share your curves
- **Statistics output** - detailed curve analysis
- **Mirror & repeat** - create complex multi-segment patterns
- **Step mode** - use absolute steps instead of percentages

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new curve types, presets, or features
- Request improvements
- Submit pull requests
- Share your custom formulas and workflows

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Credits

Created with assistance from Claude (Anthropic). Special thanks to the ComfyUI and Advanced ControlNet communities.

---

**Enjoy creating with precise control over every aspect of your generation!** 🎨✨

If you find this useful, consider starring the repo and sharing your creations!

### 🔗 Links
- [Advanced ControlNet](https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet) - Required dependency
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - The amazing UI this runs on

---

**Version:** 3.3 (Multi-ControlNet Coordination! 🎯)
