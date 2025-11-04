# ComfyUI Curved Weight Schedule

Advanced ControlNet scheduling, regional prompting, and image utilities for ComfyUI. Control your ControlNet strength across time and space with precision and visual feedback, plus powerful masking and regional prompting tools.

## 🌟 Features

### ControlNet Scheduling
- **Curved ControlNet Scheduler**: Schedule ControlNet strength across generation steps with multiple curve types
- **Advanced Curved ControlNet Scheduler**: Feature-rich version with presets, custom formulas, curve blending, and more
- **Curve Formula Builder**: NEW! Beginner-friendly visual curve builder - no math knowledge required!
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
git clone https://github.com/diffussy69/comfyui-curved_weight_schedule.git
```

3. Clone Kosinkadink's repository (Advanced ControlNet):
```bash
git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git
```

4. Install dependencies (if not already installed):
```bash
pip install matplotlib pillow numpy torch
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
- `conditioning/controlnet` → Curved ControlNet Scheduler, Advanced Curved ControlNet Scheduler, Curve Formula Builder
- `mask` → Multi-Mask Strength Combiner, Mask Symmetry Tool
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

### 2. Advanced Curved ControlNet Scheduler (NEW!)

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

### 3. Curve Formula Builder (NEW!)

**Beginner-friendly curve creator - no math knowledge required!**

Build custom curves visually using simple patterns and sliders. Perfect for users who want custom formulas without learning math syntax.

**Key Features:**
- **9 Pattern Types**: Choose from pre-made curve shapes
  - Straight Line, Ease In, Ease Out, S-Curve
  - Wave, Peak, Valley
  - Exponential Growth, Exponential Decay
- **Simple Controls**:
  - `pattern`: Select the basic curve shape
  - `strength` (0-100%): How dramatic the effect
  - `speed` (0-100%): How fast the change happens
  - `num_points`: Preview resolution (10-500)
- **Visual Modifiers**:
  - `flip_vertical`: Upside down
  - `flip_horizontal`: Reverse direction
  - `repeat_times`: Repeat pattern 1-10 times
  - `show_formula`: Display the generated math (optional)

**Outputs:**
- `formula` (STRING): Generated formula - copy to Advanced Scheduler
- `preview_graph` (IMAGE): Visual preview of your curve
- `description` (STRING): Human-readable explanation

**How to Use:**
1. Add Curve Formula Builder node
2. Select a pattern (e.g., "Ease Out (Slow End)")
3. Adjust strength and speed sliders
4. Connect `preview_graph` to Preview Image to see it
5. Copy the `formula` output
6. In Advanced Curved ControlNet Scheduler:
   - Set `curve_type` to "custom_formula"
   - Paste formula into `custom_formula` field
7. Generate!

**Example Patterns:**
- **"Fade Out"**: Pattern: Ease Out + Strength: 70% → Strong start, smooth fade
- **"Pulse Effect"**: Pattern: Wave + Speed: 40% + Repeat: 3x → Control pulses 3 times
- **"Focus Middle"**: Pattern: Peak + Strength: 80% → Strong only in middle portion
- **"Dramatic Late Change"**: Pattern: Exponential Growth + Strength: 90% → Huge impact at end

**Benefits:**
- ✅ **No math needed** - Visual controls only
- ✅ **Instant preview** - See exactly what you'll get
- ✅ **Learn gradually** - Can show formula when ready
- ✅ **Experiment freely** - Try patterns without breaking anything
- ✅ **Perfect for beginners** - Plain English descriptions

### 4. Multi-Mask Strength Combiner

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

### 5. Regional Prompting

Apply different text prompts to different regions of your image.

**Key Parameters:**
- `clip`: Your CLIP model
- `base_positive`: Base prompt applied to entire image
- `region_X_mask`: Mask for each region (1-5)
- `region_X_prompt`: Text prompt for that region
- `region_X_strength`: How strongly the prompt affects the region

**Output:**
- `conditioning`: Connect to KSampler's positive input

### 6. Regional Prompt Interpolation

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

### 7. Mask Symmetry Tool

Mirror and flip masks across different axes for symmetrical compositions.

**Key Parameters:**
- `mask`: Input mask to mirror
- `symmetry_mode`: Type of symmetry to apply
  - `none`: No symmetry (passthrough)
  - `horizontal`: Left ↔ Right mirror
  - `vertical`: Top ↔ Bottom mirror
  - `both`: Both axes (4-way symmetry)
  - `diagonal_tl_br`: Top-left to bottom-right
  - `diagonal_tr_bl`: Top-right to bottom-left
  - `radial_4way`: 4-way radial symmetry
  - `radial_8way`: 8-way radial symmetry
- `blend_mode`: How to combine original and mirrored
- `blend_strength`: Strength of symmetry effect (0.0-1.0)
- `invert_mirrored`: Invert the mirrored portion

**Output:**
- `symmetrical_mask`: Symmetrical mask output

### 8. Auto Person Mask

AI-powered automatic person detection and masking.

**Key Parameters:**
- `image`: Input image
- `threshold`: Detection confidence (0.0-1.0)
- `expand_mask`: Pixels to expand detection (0-100)
- `blur_radius`: Mask edge softening (0-50)

**Output:**
- `mask`: Person/foreground mask

### 9. Auto Background Mask

Automatic background masking (inverted person mask).

**Key Parameters:**
- Same as Auto Person Mask

**Output:**
- `mask`: Background mask (everything except person)

## 💡 Usage Tips

### Getting Started with Presets

**With JavaScript Extension (Recommended):**
1. Install the JS extension (see Installation)
2. Select any preset from dropdown
3. Watch all fields update automatically! ✨
4. Generate immediately - no manual adjustment needed

**Without JavaScript Extension:**
- Presets still work internally
- UI fields won't update visually, but preset values ARE being used
- Check console output to see applied values
- Consider installing JS extension for better UX

### Advanced Custom Formulas

Write any mathematical curve you can imagine! The formula uses `t` as variable (0 to 1).

**Popular Formulas:**
```python
# Sine wave (3 oscillations)
"sin(t * 3 * 3.14159)"

# Ease-in-out cubic
"3*t**2 - 2*t**3"

# Double peak
"exp(-((t-0.3)**2)/0.05) + exp(-((t-0.7)**2)/0.05)"

# Exponential rise with plateau
"1 - exp(-t*5)"

# Polynomial curve
"3*t**2 - 2*t**3"

# Sawtooth wave
"(t*4) % 1"
```

**Curve Blending Strategies:**
- Blend `linear` with `sine_wave` for subtle rhythm
- Blend `ease_out` with `bell_curve` for complex transitions
- Use low blend amounts (0.1-0.3) for subtle variations

**Adaptive Keyframes:**
- Turn ON for custom formulas with rapid changes
- Turn OFF for simple curves (saves computation)
- Most useful with sine waves, bounce, and custom formulas

**CSV Export:**
- Save successful curves for reuse
- Share curves with the community
- Document your workflows

### Understanding Curve Direction

**The curve type controls the SHAPE, your strength values control the DIRECTION:**

Example with `ease_in` (slow start, fast end):
- `start=1.0, end=0.0` → Stays at 1.0 for a while, then drops quickly to 0.0
- `start=0.0, end=1.0` → Stays at 0.0 for a while, then rises quickly to 1.0

Example with `exponential` (dramatic growth):
- `start=0.2, end=1.5` → Slowly starts at 0.2, then dramatically shoots up to 1.5
- `start=1.5, end=0.2` → Stays high at 1.5, then drops dramatically to 0.2

**Pro Tip:** Use the graph preview to verify your curve looks correct before generating!

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

## 🛠 Troubleshooting

**Issue: ControlNet not working at all / no effect**
- ⚠️ **Solution**: Check your Advanced ControlNet node settings!
  - Set `strength` to **1.00**
  - Set `start_percent` to **0.000**
  - Set `end_percent` to **1.000**
  - These settings must be correct for the scheduler to work!

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

**Issue: Effect too strong everywhere**
- Solution:
  - Decrease `start_strength` and `end_strength` values
  - Decrease individual mask strengths in Multi-Mask Combiner
  - Check that Advanced ControlNet strength isn't multiplying your values

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
- Python packages: matplotlib, pillow, numpy, torch

## 🆕 What's New

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

**Version:** 2.2 (Added Curve Formula Builder - Beginner-Friendly Visual Curve Creator)
