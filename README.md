# comfyui-curved_weight_schedule
Custom Node for ComfyUI that allows you set a weighted curve to your ControlNet giving you more control over the weight of the model over the course of generation. 

==INSTALL==
1. clone this repository to: yourcomfyuipath\custom_nodes
2. install matplotlib
   2a. pip install matplotlib pillow
3. This node is built with using Kosinkadink's ComfyUI-Advanced-ControlNet in mind, so go install that awesome node!
   3a. https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet

Boom, that's it.

<img width="631" height="514" alt="image" src="https://github.com/user-attachments/assets/a815bc01-b577-425b-8fa4-c4f0fec11560" />
To adjust the fade speed:

Lower curve_param (like 0.5-1.0) = drops fast at first, then slowly
Higher curve_param (like 3.0-5.0) = stays strong longer, then drops quickly at the end

To change the range:

Adjust end_percent (e.g., 0.7 instead of 1.0) to stop the fade at 70% through generation
Adjust start_percent if you want to delay when ControlNet kicks in

Other useful curve types to try:

weak_to_strong - opposite effect, builds up influence over time
bell_curve - strong in the middle, weak at start and end
ease_in_out - smooth transitions at both ends

Recommended Values:

5-10 keyframes: Usually enough for smooth curves
10-20 keyframes: Very smooth, more control points
More keyframes = smoother curve, but diminishing returns after ~20

The Math:
If you set:

num_keyframes = 10
start_percent = 0.0
end_percent = 0.7

You get keyframes at: 0%, 7.8%, 15.6%, 23.3%, 31.1%, 38.9%, 46.7%, 54.4%, 62.2%, 70%
No matter if you're running 20 steps or 50 steps, these percentages apply.
TL;DR: Use 10-20 keyframes regardless of step count. More keyframes = smoother curve, but you don't need one per step!
