# ControlNet- Curved weights and multi-mask weights.
Custom Node for ComfyUI that allows you set a weighted curve to your ControlNet giving you more control over the weight of the model over the course of generation. 

==INSTALL==
1. clone this repository to: yourcomfyuipath\custom_nodes
2. install matplotlib

   2a. pip install matplotlib pillow

4. This node is built with using Kosinkadink's ComfyUI-Advanced-ControlNet in mind, so go install that awesome node!

   3a. https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet

Boom, that's it.

<img width="982" height="604" alt="image" src="https://github.com/user-attachments/assets/4be11dc7-562c-406a-a7ad-25a72b3c3f30" />
<img width="631" height="514" alt="image" src="https://github.com/user-attachments/assets/a815bc01-b577-425b-8fa4-c4f0fec11560" />
<img width="737" height="475" alt="image" src="https://github.com/user-attachments/assets/b7692f72-2ded-4926-ada8-690dd794689f" />
<img width="773" height="400" alt="image" src="https://github.com/user-attachments/assets/7e80f214-b83c-477c-8b02-484a29a5220c" />
<img width="734" height="367" alt="image" src="https://github.com/user-attachments/assets/a51c7549-4677-4f5f-b218-682ec728978c" />
<img width="665" height="727" alt="image" src="https://github.com/user-attachments/assets/e4a1a95a-6169-4301-91f0-7a6780307054" />
How it works: Takes the highest strength value at each pixel
Example:

Pixel in mask_1: 0.8 strength
Same pixel in mask_2: 0.5 strength
Result: 0.8 (takes the max)

Best for:

Non-overlapping regions (mountains, flowers, sky)
When masks might slightly overlap and you want the stronger one to win
Most predictable behavior


add
How it works: Adds all mask strengths together
Example:

Pixel in mask_1: 0.8 strength
Same pixel in mask_2: 0.5 strength
Result: 1.3 (adds them, can exceed 1.0!)

Best for:

Layering effects where overlaps should be stronger
When you want cumulative strength
Warning: Can easily go above 1.0, might need to reduce individual strengths


multiply
How it works: Multiplies masks together (darker result)
Example:

Pixel in mask_1: 0.8 strength
Same pixel in mask_2: 0.5 strength
Result: 0.4 (0.8 × 0.5)

Best for:

Creating "cutout" effects (one mask removes from another)
When you want overlaps to be WEAKER, not stronger
More subtle, softer results
Note: Can make things very weak quickly


average
How it works: Averages all mask strengths together
Example:

Pixel in mask_1: 0.8 strength
Same pixel in mask_2: 0.4 strength
Same pixel in mask_3: 0.6 strength
Result: 0.6 ((0.8 + 0.4 + 0.6) / 3)

Best for:

Balancing multiple overlapping masks
When you want consistent, moderate strength
Smoother blending between regions


Quick Comparison:
Blend ModeOverlaps behaviorResult rangeBest usemaxStronger wins0.0 - 2.0Separate regions ✅addGets stronger0.0 - 10.0+Layered effectsmultiplyGets weaker0.0 - 1.0Soft/subtleaverageBalanced0.0 - 2.0Smooth blending
My recommendation: Start with max - it's the most intuitive and predictable for your use case (different regions like mountains, flowers, sky).
