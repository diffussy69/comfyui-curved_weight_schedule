// Advanced Curved ControlNet Scheduler - UI Update Extension
// Waits for node registration before patching

console.log("🎨 Advanced Curved Scheduler Extension Loading...");

// Preset configurations (must match Python side)
const CURVE_PRESETS = {
    "Custom": null,
    "Fade Out": { start_strength: 1.0, end_strength: 0.0, curve_type: "ease_out", curve_param: 2.0 },
    "Fade In": { start_strength: 0.0, end_strength: 1.0, curve_type: "ease_in", curve_param: 2.0 },
    "Peak Control": { start_strength: 0.0, end_strength: 0.0, curve_type: "bell_curve", curve_param: 2.0 },
    "Valley Control": { start_strength: 1.0, end_strength: 1.0, curve_type: "reverse_bell", curve_param: 2.0 },
    "Strong Start+End": { start_strength: 1.0, end_strength: 1.0, curve_type: "reverse_bell", curve_param: 3.0 },
    "Oscillating": { start_strength: 0.5, end_strength: 0.5, curve_type: "sine_wave", curve_param: 3.0 },
    "Exponential Decay": { start_strength: 1.0, end_strength: 0.0, curve_type: "exponential", curve_param: 4.0 },
    "Smooth Transition": { start_strength: 1.0, end_strength: 0.0, curve_type: "ease_in_out", curve_param: 2.0 }
};

console.log("✅ CURVE_PRESETS defined");

let patched = false;

function patchNode() {
    if (patched) {
        console.log("⏭️ Already patched, skipping");
        return true;
    }
    
    console.log("🔧 Attempting to patch node...");
    
    const nodeType = window.LiteGraph?.registered_node_types?.["Advanced Curved ControlNet Scheduler"];
    
    if (!nodeType) {
        console.log("⏳ Node type not registered yet, will retry...");
        return false;
    }
    
    console.log("✅ Node type found! Patching...");
    
    // Patch the onNodeCreated method
    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    
    nodeType.prototype.onNodeCreated = function() {
        console.log("🏗️ Node created, setting up preset handler...");
        
        // Call original
        if (originalOnNodeCreated) {
            originalOnNodeCreated.apply(this, arguments);
        }
        
        // Wait a tick for widgets to be fully initialized
        setTimeout(() => {
            console.log("⏰ Delayed setup starting...");
            console.log("📋 Available widgets:", this.widgets?.map(w => w.name));
            
            const presetWidget = this.widgets?.find(w => w.name === "preset");
            
            if (!presetWidget) {
                console.error("❌ Preset widget not found!");
                return;
            }
            
            console.log("✅ Preset widget found!");
            
            // Store reference to node
            const node = this;
            
            // Store original callback
            const originalCallback = presetWidget.callback;
            
            // Override callback
            presetWidget.callback = function(value) {
                console.log("🎯 PRESET CHANGED TO:", value);
                
                // Call original
                if (originalCallback) {
                    originalCallback.call(this, value);
                }
                
                // Apply preset
                if (value !== "Custom" && CURVE_PRESETS[value]) {
                    const preset = CURVE_PRESETS[value];
                    console.log("📋 Applying preset values:", preset);
                    
                    const widgets = {
                        start_strength: node.widgets.find(w => w.name === "start_strength"),
                        end_strength: node.widgets.find(w => w.name === "end_strength"),
                        curve_type: node.widgets.find(w => w.name === "curve_type"),
                        curve_param: node.widgets.find(w => w.name === "curve_param")
                    };
                    
                    console.log("🔧 Widgets found:", Object.keys(widgets).filter(k => widgets[k]));
                    
                    if (widgets.start_strength) {
                        console.log(`  start_strength: ${widgets.start_strength.value} → ${preset.start_strength}`);
                        widgets.start_strength.value = preset.start_strength;
                    }
                    
                    if (widgets.end_strength) {
                        console.log(`  end_strength: ${widgets.end_strength.value} → ${preset.end_strength}`);
                        widgets.end_strength.value = preset.end_strength;
                    }
                    
                    if (widgets.curve_type) {
                        console.log(`  curve_type: ${widgets.curve_type.value} → ${preset.curve_type}`);
                        widgets.curve_type.value = preset.curve_type;
                    }
                    
                    if (widgets.curve_param) {
                        console.log(`  curve_param: ${widgets.curve_param.value} → ${preset.curve_param}`);
                        widgets.curve_param.value = preset.curve_param;
                    }
                    
                    // Force redraw
                    if (node.setDirtyCanvas) {
                        node.setDirtyCanvas(true, true);
                    }
                    
                    console.log("✅ Preset applied successfully!");
                } else {
                    console.log("ℹ️ Custom preset selected");
                }
            };
            
            console.log("✅ Preset callback attached!");
        }, 100);
    };
    
    patched = true;
    console.log("✅ Node patched successfully!");
    return true;
}

// Keep trying to patch until successful
let attempts = 0;
const maxAttempts = 50; // Try for 5 seconds
const patchInterval = setInterval(() => {
    attempts++;
    console.log(`🔄 Patch attempt ${attempts}/${maxAttempts}`);
    
    if (patchNode()) {
        console.log("🎉 Patching successful, stopping retry");
        clearInterval(patchInterval);
    } else if (attempts >= maxAttempts) {
        console.error("❌ Failed to patch after", maxAttempts, "attempts");
        clearInterval(patchInterval);
    }
}, 100);

export default {
    name: "AdvancedCurvedControlNetScheduler.PresetUpdater",
    async setup() {
        console.log("🔧 Extension setup called, attempting patch");
        patchNode();
    }
};

console.log("🚀 Extension module loaded, waiting for node registration...");