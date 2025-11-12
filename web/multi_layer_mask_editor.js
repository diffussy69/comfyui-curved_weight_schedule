import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const LAYER_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA15E", "#C084FC", "#FB5607", "#8338EC", "#06FFA5"
];

class MaskLayer {
    constructor(width, height, index) {
        this.canvas = document.createElement('canvas');
        this.canvas.width = width;
        this.canvas.height = height;
        this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
        this.visible = true;
        this.index = index;
        this.name = `Layer ${index + 1}`;
        this.color = LAYER_COLORS[index % LAYER_COLORS.length];
        this.ctx.clearRect(0, 0, width, height);
    }
    
    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    getMaskData() {
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const maskData = new Uint8Array(this.canvas.width * this.canvas.height);
        
        for (let i = 0, j = 3; i < maskData.length; i++, j += 4) {
            maskData[i] = imageData.data[j];
        }
        
        const bytes = [];
        for (let i = 0; i < maskData.length; i++) {
            bytes.push(String.fromCharCode(maskData[i]));
        }
        
        return {
            width: this.canvas.width,
            height: this.canvas.height,
            data: btoa(bytes.join(''))
        };
    }
    
    setMaskData(data) {
        if (!data || !data.data) return;
        
        const binaryString = atob(data.data);
        const maskData = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            maskData[i] = binaryString.charCodeAt(i);
        }
        
        const imageData = this.ctx.createImageData(data.width, data.height);
        for (let i = 0, j = 3; i < maskData.length; i++, j += 4) {
            imageData.data[j - 3] = 255;
            imageData.data[j - 2] = 255;
            imageData.data[j - 1] = 255;
            imageData.data[j] = maskData[i];
        }
        
        this.ctx.putImageData(imageData, 0, 0);
    }
}

class MaskEditorDialog {
    constructor(imageElement, initialMasks, numLayers, onSave) {
        this.imageElement = imageElement;
        this.onSave = onSave;
        this.layers = [];
        this.activeLayerIndex = 0;
        this.numLayers = numLayers;
        
        this.brushSize = 50;
        this.brushOpacity = 1.0;
        this.brushHardness = 0.5;
        this.isPainting = true;
        
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        
        // Pan and zoom state
        this.zoom = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.panStartX = 0;
        this.panStartY = 0;
        this.minZoom = 0.1;
        this.maxZoom = 10.0;
        this.transformScheduled = false;
        
        this.createDialog();
        this.loadImage(initialMasks);
    }
    
    createDialog() {
        this.backdrop = document.createElement('div');
        this.backdrop.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); z-index: 9998;
            display: flex; align-items: center; justify-content: center;
        `;
        
        this.dialog = document.createElement('div');
        this.dialog.style.cssText = `
            background: #1e1e1e; border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            display: flex; flex-direction: column;
            width: 90vw; height: 90vh; z-index: 9999;
        `;
        
        // Header
        const header = document.createElement('div');
        header.style.cssText = `
            padding: 15px 20px; border-bottom: 1px solid #333;
            display: flex; justify-content: space-between; align-items: center;
            background: #252525; border-radius: 8px 8px 0 0;
        `;
        
        const title = document.createElement('h3');
        title.textContent = 'Multi-Layer Mask Editor';
        title.style.cssText = 'margin: 0; color: #fff; font-size: 18px;';
        
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.style.cssText = `
            background: none; border: none; color: #999; font-size: 32px;
            cursor: pointer; width: 32px; height: 32px;
        `;
        closeBtn.onclick = () => this.close();
        
        header.appendChild(title);
        header.appendChild(closeBtn);
        
        // Main content
        const content = document.createElement('div');
        content.style.cssText = 'display: flex; flex: 1; overflow: hidden;';
        
        this.createToolbar();
        this.createCanvasArea();
        this.createLayerPanel();
        
        content.appendChild(this.toolbar);
        content.appendChild(this.canvasArea);
        content.appendChild(this.layerPanel);
        
        // Footer
        const footer = document.createElement('div');
        footer.style.cssText = `
            padding: 15px 20px; border-top: 1px solid #333;
            display: flex; justify-content: space-between; align-items: center;
            background: #252525; border-radius: 0 0 8px 8px;
        `;
        
        // Zoom info in footer
        this.zoomInfo = document.createElement('div');
        this.zoomInfo.style.cssText = 'color: #999; font-size: 12px;';
        this.updateZoomInfo();
        footer.appendChild(this.zoomInfo);
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = 'display: flex; gap: 10px;';
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = `
            padding: 8px 24px; background: #444; border: none;
            border-radius: 4px; color: white; cursor: pointer;
        `;
        cancelBtn.onclick = () => this.close();
        
        const saveBtn = document.createElement('button');
        saveBtn.textContent = 'Save';
        saveBtn.style.cssText = `
            padding: 8px 24px; background: #4CAF50; border: none;
            border-radius: 4px; color: white; cursor: pointer; font-weight: 600;
        `;
        saveBtn.onclick = () => this.save();
        
        buttonContainer.appendChild(cancelBtn);
        buttonContainer.appendChild(saveBtn);
        footer.appendChild(buttonContainer);
        
        this.dialog.appendChild(header);
        this.dialog.appendChild(content);
        this.dialog.appendChild(footer);
        this.backdrop.appendChild(this.dialog);
        document.body.appendChild(this.backdrop);
        
        this.backdrop.addEventListener('click', (e) => {
            if (e.target === this.backdrop) this.close();
        });
        
        this.escapeHandler = (e) => {
            if (e.key === 'Escape') this.close();
        };
        document.addEventListener('keydown', this.escapeHandler);
    }
    
    createToolbar() {
        this.toolbar = document.createElement('div');
        this.toolbar.style.cssText = `
            width: 200px; background: #2a2a2a; border-right: 1px solid #333;
            padding: 15px; overflow-y: auto;
        `;
        
        // Tool section
        const toolHeader = document.createElement('div');
        toolHeader.textContent = '🖌️ Tool';
        toolHeader.style.cssText = 'color: #fff; font-size: 14px; font-weight: 600; margin-bottom: 10px;';
        this.toolbar.appendChild(toolHeader);
        
        const paintBtn = this.createButton('Paint', true);
        const eraseBtn = this.createButton('Erase', false);
        
        paintBtn.onclick = () => {
            this.isPainting = true;
            paintBtn.style.background = '#4CAF50';
            eraseBtn.style.background = '#444';
        };
        eraseBtn.onclick = () => {
            this.isPainting = false;
            eraseBtn.style.background = '#4CAF50';
            paintBtn.style.background = '#444';
        };
        
        this.toolbar.appendChild(paintBtn);
        this.toolbar.appendChild(eraseBtn);
        
        // Add bucket fill button
        const fillHeader = document.createElement('div');
        fillHeader.textContent = '🪣 Fill';
        fillHeader.style.cssText = 'color: #fff; font-size: 14px; font-weight: 600; margin: 20px 0 10px;';
        this.toolbar.appendChild(fillHeader);
        
        const fillBtn = this.createButton('Fill Layer', false);
        fillBtn.onclick = () => {
            const layer = this.layers[this.activeLayerIndex];
            const ctx = layer.ctx;
            
            if (this.isPainting) {
                // Fill entire layer with white (mask on)
                ctx.fillStyle = 'rgba(255, 255, 255, 1)';
                ctx.fillRect(0, 0, layer.canvas.width, layer.canvas.height);
            } else {
                // Clear entire layer (mask off)
                ctx.clearRect(0, 0, layer.canvas.width, layer.canvas.height);
            }
            
            this.redraw();
        };
        this.toolbar.appendChild(fillBtn);
        
        const fillHelpText = document.createElement('div');
        fillHelpText.innerHTML = '<div style="color: #888; font-size: 11px; margin-top: 5px; line-height: 1.3;">Fills entire layer based on Paint/Erase mode</div>';
        this.toolbar.appendChild(fillHelpText);
        
        // Brush size section
        const brushHeader = document.createElement('div');
        brushHeader.textContent = '🎨 Brush Size';
        brushHeader.style.cssText = 'color: #fff; font-size: 14px; font-weight: 600; margin: 20px 0 10px;';
        this.toolbar.appendChild(brushHeader);
        
        const sizeSlider = document.createElement('input');
        sizeSlider.type = 'range';
        sizeSlider.min = 1;
        sizeSlider.max = 200;
        sizeSlider.value = 50;
        sizeSlider.style.cssText = 'width: 100%;';
        
        const sizeLabel = document.createElement('div');
        sizeLabel.textContent = '50';
        sizeLabel.style.cssText = 'color: #4CAF50; text-align: center; margin-top: 5px; font-weight: 600;';
        
        sizeSlider.addEventListener('input', (e) => {
            this.brushSize = parseInt(e.target.value);
            sizeLabel.textContent = e.target.value;
        });
        
        this.toolbar.appendChild(sizeSlider);
        this.toolbar.appendChild(sizeLabel);
        
        // View controls section
        const viewHeader = document.createElement('div');
        viewHeader.textContent = '🔍 View';
        viewHeader.style.cssText = 'color: #fff; font-size: 14px; font-weight: 600; margin: 20px 0 10px;';
        this.toolbar.appendChild(viewHeader);
        
        const fitBtn = this.createButton('Fit to View', false);
        fitBtn.onclick = () => this.fitToView();
        this.toolbar.appendChild(fitBtn);
        
        const resetBtn = this.createButton('Reset View (1:1)', false);
        resetBtn.onclick = () => this.resetView();
        this.toolbar.appendChild(resetBtn);
        
        const zoomInBtn = this.createButton('Zoom In (+)', false);
        zoomInBtn.onclick = () => this.zoomBy(1.2);
        this.toolbar.appendChild(zoomInBtn);
        
        const zoomOutBtn = this.createButton('Zoom Out (-)', false);
        zoomOutBtn.onclick = () => this.zoomBy(0.8);
        this.toolbar.appendChild(zoomOutBtn);
        
        // Help text
        const helpText = document.createElement('div');
        helpText.innerHTML = `
            <div style="color: #888; font-size: 11px; margin-top: 10px; line-height: 1.4;">
                <strong style="color: #aaa;">Controls:</strong><br>
                • Mouse wheel: Zoom<br>
                • Space + Drag: Pan<br>
                • Middle click + Drag: Pan
            </div>
        `;
        this.toolbar.appendChild(helpText);
        
        // Actions section
        const actionsHeader = document.createElement('div');
        actionsHeader.textContent = '⚡ Actions';
        actionsHeader.style.cssText = 'color: #fff; font-size: 14px; font-weight: 600; margin: 20px 0 10px;';
        this.toolbar.appendChild(actionsHeader);
        
        const clearBtn = this.createButton('Clear Layer', false);
        clearBtn.onclick = () => {
            this.layers[this.activeLayerIndex].clear();
            this.redraw();
        };
        this.toolbar.appendChild(clearBtn);
        
        const clearAllBtn = this.createButton('Clear All Layers', false);
        clearAllBtn.style.background = '#d32f2f';
        clearAllBtn.onclick = () => {
            if (confirm('Clear all layers? This cannot be undone.')) {
                this.layers.forEach(layer => layer.clear());
                this.redraw();
            }
        };
        this.toolbar.appendChild(clearAllBtn);
    }
    
    createButton(text, active) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.style.cssText = `
            width: 100%; padding: 8px; margin-bottom: 5px;
            background: ${active ? '#4CAF50' : '#444'}; border: none;
            border-radius: 4px; color: white; cursor: pointer;
            font-size: 13px;
        `;
        return btn;
    }
    
    createCanvasArea() {
        this.canvasArea = document.createElement('div');
        this.canvasArea.style.cssText = `
            flex: 1; background: #2a2a2a;
            display: flex; align-items: center; justify-content: center;
            position: relative; overflow: hidden;
        `;
        
        // Canvas container for transforms
        this.canvasContainer = document.createElement('div');
        this.canvasContainer.style.cssText = `
            position: relative;
            transform-origin: 0 0;
            will-change: transform;
        `;
        
        // Single canvas for everything
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = 'cursor: crosshair; display: block;';
        this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
        
        this.canvasContainer.appendChild(this.canvas);
        this.canvasArea.appendChild(this.canvasContainer);
        
        // Mouse events on canvas area (not canvas itself) for proper coordinate handling
        this.canvasArea.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvasArea.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvasArea.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvasArea.addEventListener('mouseleave', (e) => this.handleMouseLeave(e));
        
        // Wheel event for zooming
        this.canvasArea.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });
        
        // Keyboard events for panning modifier
        this.spacePressed = false;
        this.keydownHandler = (e) => {
            if (e.code === 'Space' && !this.spacePressed && !e.repeat) {
                this.spacePressed = true;
                if (!this.isDrawing && !this.isPanning) {
                    this.canvasArea.style.cursor = 'grab';
                    this.canvas.style.cursor = 'grab';
                }
                e.preventDefault();
            }
        };
        this.keyupHandler = (e) => {
            if (e.code === 'Space') {
                this.spacePressed = false;
                if (!this.isPanning) {
                    this.canvasArea.style.cursor = 'default';
                    this.canvas.style.cursor = 'crosshair';
                }
            }
        };
        document.addEventListener('keydown', this.keydownHandler);
        document.addEventListener('keyup', this.keyupHandler);
    }
    
    handleMouseDown(e) {
        e.preventDefault();
        
        // Get coordinates relative to canvasContainer (accounts for flexbox centering)
        const rect = this.canvasContainer.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        // Middle mouse button or space + left click for panning
        if (e.button === 1 || (e.button === 0 && this.spacePressed)) {
            this.isPanning = true;
            this.panStartX = e.clientX;
            this.panStartY = e.clientY;
            this.panStartOffsetX = this.panX;
            this.panStartOffsetY = this.panY;
            this.canvasArea.style.cursor = 'grabbing';
            this.canvas.style.cursor = 'grabbing';
            return;
        }
        
        // Left mouse button for drawing
        if (e.button === 0 && !this.spacePressed) {
            this.isDrawing = true;
            const canvasCoords = this.screenToCanvas(screenX, screenY);
            
            // Bounds check
            if (canvasCoords.x < 0 || canvasCoords.x >= this.canvas.width ||
                canvasCoords.y < 0 || canvasCoords.y >= this.canvas.height) {
                this.isDrawing = false;
                return;
            }
            
            this.lastX = canvasCoords.x;
            this.lastY = canvasCoords.y;
            this.lastRedrawTime = 0;
            this.drawPoint(this.lastX, this.lastY);
            this.redraw();
        }
    }
    
    handleMouseMove(e) {
        // Get coordinates relative to canvasContainer
        const rect = this.canvasContainer.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        if (this.isPanning) {
            const dx = e.clientX - this.panStartX;
            const dy = e.clientY - this.panStartY;
            this.panX = this.panStartOffsetX + dx;
            this.panY = this.panStartOffsetY + dy;
            this.updateTransform();
            return;
        }
        
        if (this.isDrawing) {
            const canvasCoords = this.screenToCanvas(screenX, screenY);
            
            // Bounds check
            if (canvasCoords.x < 0 || canvasCoords.x >= this.canvas.width ||
                canvasCoords.y < 0 || canvasCoords.y >= this.canvas.height) {
                return;
            }
            
            this.drawLine(this.lastX, this.lastY, canvasCoords.x, canvasCoords.y);
            this.lastX = canvasCoords.x;
            this.lastY = canvasCoords.y;
            
            const now = Date.now();
            if (!this.lastRedrawTime || now - this.lastRedrawTime > 50) {
                this.redraw();
                this.lastRedrawTime = now;
            }
        }
        
        // Update cursor based on whether we're over the canvas
        const canvasCoords = this.screenToCanvas(screenX, screenY);
        const isOverCanvas = canvasCoords.x >= 0 && canvasCoords.x < this.canvas.width &&
                            canvasCoords.y >= 0 && canvasCoords.y < this.canvas.height;
        
        if (!this.isPanning && !this.isDrawing) {
            if (this.spacePressed) {
                this.canvas.style.cursor = isOverCanvas ? 'grab' : 'default';
            } else {
                this.canvas.style.cursor = isOverCanvas ? 'crosshair' : 'default';
            }
        }
    }
    
    handleMouseUp(e) {
        if (this.isPanning) {
            this.isPanning = false;
            this.canvasArea.style.cursor = 'default';
            this.canvas.style.cursor = this.spacePressed ? 'grab' : 'crosshair';
        }
        
        if (this.isDrawing) {
            this.isDrawing = false;
            this.redraw();
        }
    }
    
    handleMouseLeave(e) {
        if (this.isDrawing) {
            this.isDrawing = false;
            this.redraw();
        }
        if (this.isPanning) {
            this.isPanning = false;
            this.canvasArea.style.cursor = 'default';
            this.canvas.style.cursor = 'default';
        }
    }
    
    handleWheel(e) {
        e.preventDefault();
        
        // Get coordinates relative to canvasContainer
        const rect = this.canvasContainer.getBoundingClientRect();
        const screenX = e.clientX - rect.left;
        const screenY = e.clientY - rect.top;
        
        // Zoom factor
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newZoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom * delta));
        
        if (newZoom !== this.zoom) {
            // Zoom toward mouse position
            const canvasCoords = this.screenToCanvas(screenX, screenY);
            
            this.zoom = newZoom;
            
            // Adjust pan to keep the point under the mouse in the same position
            const newScreenCoords = this.canvasToScreen(canvasCoords.x, canvasCoords.y);
            this.panX += screenX - newScreenCoords.x;
            this.panY += screenY - newScreenCoords.y;
            
            this.updateTransform(true); // Immediate for responsive zoom
            this.updateZoomInfo();
        }
    }
    
    screenToCanvas(screenX, screenY) {
        // screenX and screenY are relative to canvasContainer
        // canvasContainer.getBoundingClientRect() already accounts for translate(panX, panY)
        // So we only need to undo the scale, NOT subtract pan again!
        return {
            x: screenX / this.zoom,
            y: screenY / this.zoom
        };
    }
    
    canvasToScreen(canvasX, canvasY) {
        // Convert canvas coordinates to screen coordinates
        // Just apply the scale - the pan is already in the container's position
        return {
            x: canvasX * this.zoom,
            y: canvasY * this.zoom
        };
    }
    
    updateTransform(immediate = false) {
        if (immediate) {
            // Apply transform immediately (for initial setup, zoom buttons, etc.)
            this.canvasContainer.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`;
            this.transformScheduled = false;
        } else {
            // Use requestAnimationFrame for smooth updates during panning
            if (!this.transformScheduled) {
                this.transformScheduled = true;
                requestAnimationFrame(() => {
                    this.canvasContainer.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`;
                    this.transformScheduled = false;
                });
            }
        }
    }
    
    updateZoomInfo() {
        const zoomPercent = Math.round(this.zoom * 100);
        this.zoomInfo.textContent = `Zoom: ${zoomPercent}% | Canvas: ${this.canvas.width}×${this.canvas.height}px`;
    }
    
    fitToView() {
        const containerRect = this.canvasArea.getBoundingClientRect();
        const padding = 40;
        const availableWidth = containerRect.width - padding;
        const availableHeight = containerRect.height - padding;
        
        const scaleX = availableWidth / this.canvas.width;
        const scaleY = availableHeight / this.canvas.height;
        
        this.zoom = Math.min(scaleX, scaleY, 1.0);
        
        // Center the canvas
        this.panX = (containerRect.width - this.canvas.width * this.zoom) / 2;
        this.panY = (containerRect.height - this.canvas.height * this.zoom) / 2;
        
        this.updateTransform(true); // Immediate update
        this.updateZoomInfo();
    }
    
    resetView() {
        this.zoom = 1.0;
        
        // Center the canvas
        const containerRect = this.canvasArea.getBoundingClientRect();
        this.panX = (containerRect.width - this.canvas.width) / 2;
        this.panY = (containerRect.height - this.canvas.height) / 2;
        
        this.updateTransform(true); // Immediate update
        this.updateZoomInfo();
    }
    
    zoomBy(factor) {
        const containerRect = this.canvasArea.getBoundingClientRect();
        const centerX = containerRect.width / 2;
        const centerY = containerRect.height / 2;
        
        // Get rect of the container to find where center maps to
        const rect = this.canvasContainer.getBoundingClientRect();
        const screenX = centerX + containerRect.left - rect.left;
        const screenY = centerY + containerRect.top - rect.top;
        
        const canvasCoords = this.screenToCanvas(screenX, screenY);
        
        const oldZoom = this.zoom;
        this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoom * factor));
        
        const newScreenCoords = this.canvasToScreen(canvasCoords.x, canvasCoords.y);
        this.panX += screenX - newScreenCoords.x;
        this.panY += screenY - newScreenCoords.y;
        
        this.updateTransform(true); // Immediate update
        this.updateZoomInfo();
    }
    
    createLayerPanel() {
        this.layerPanel = document.createElement('div');
        this.layerPanel.style.cssText = `
            width: 200px; background: #2a2a2a; border-left: 1px solid #333;
            padding: 15px; overflow-y: auto;
        `;
        
        const header = document.createElement('div');
        header.style.cssText = 'display: flex; justify-content: space-between; margin-bottom: 10px;';
        header.innerHTML = '<div style="color: #fff; font-weight: 600;">Layers</div>';
        
        const addBtn = document.createElement('button');
        addBtn.textContent = '+';
        addBtn.style.cssText = `
            width: 24px; height: 24px; background: #4CAF50;
            border: none; border-radius: 4px; color: white; cursor: pointer;
        `;
        addBtn.onclick = () => this.addLayer();
        header.appendChild(addBtn);
        
        this.layerPanel.appendChild(header);
        
        this.layerList = document.createElement('div');
        this.layerPanel.appendChild(this.layerList);
    }
    
    updateLayerList() {
        this.layerList.innerHTML = '';
        
        // Display layers 1-5 from top to bottom (more intuitive)
        for (let i = 0; i < this.layers.length; i++) {
            const layer = this.layers[i];
            const isActive = i === this.activeLayerIndex;
            
            const layerDiv = document.createElement('div');
            layerDiv.style.cssText = `
                padding: 10px; margin-bottom: 5px; border-radius: 4px;
                background: ${isActive ? '#3a3a3a' : '#2a2a2a'};
                border: 2px solid ${isActive ? layer.color : '#333'};
                cursor: pointer; display: flex; align-items: center;
                justify-content: space-between;
            `;
            
            layerDiv.onclick = () => {
                this.activeLayerIndex = i;
                this.updateLayerList();
            };
            
            const info = document.createElement('div');
            info.style.cssText = 'display: flex; align-items: center; flex: 1;';
            
            const colorDot = document.createElement('div');
            colorDot.style.cssText = `
                width: 16px; height: 16px; border-radius: 50%;
                background: ${layer.color}; margin-right: 8px;
            `;
            
            const name = document.createElement('span');
            name.textContent = layer.name;
            name.style.cssText = 'color: #fff; font-size: 13px;';
            
            info.appendChild(colorDot);
            info.appendChild(name);
            
            const visibilityBtn = document.createElement('button');
            visibilityBtn.textContent = layer.visible ? '👁' : '👁‍🗨';
            visibilityBtn.style.cssText = `
                background: none; border: none; cursor: pointer;
                font-size: 16px; padding: 0 5px;
            `;
            visibilityBtn.onclick = (e) => {
                e.stopPropagation();
                layer.visible = !layer.visible;
                this.updateLayerList();
                this.redraw();
            };
            
            layerDiv.appendChild(info);
            layerDiv.appendChild(visibilityBtn);
            this.layerList.appendChild(layerDiv);
        }
    }
    
    addLayer() {
        if (this.layers.length >= 10) return;
        const layer = new MaskLayer(
            this.imageElement.width,
            this.imageElement.height,
            this.layers.length
        );
        this.layers.push(layer);
        this.activeLayerIndex = this.layers.length - 1;
        this.updateLayerList();
        this.redraw();
    }
    
    loadImage(initialMasks) {
        const img = this.imageElement;
        
        // Set canvas to image size (full resolution)
        this.canvas.width = img.width;
        this.canvas.height = img.height;
        
        // Draw background image
        this.ctx.drawImage(img, 0, 0);
        
        // Store background
        this.bgImageData = this.ctx.getImageData(0, 0, img.width, img.height);
        
        // Create layers
        for (let i = 0; i < this.numLayers; i++) {
            const layer = new MaskLayer(img.width, img.height, i);
            if (initialMasks && initialMasks[i]) {
                layer.setMaskData(initialMasks[i]);
            }
            this.layers.push(layer);
        }
        
        this.updateLayerList();
        this.redraw();
        
        // Wait for layout to complete before calculating initial view
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                this.fitToView();
            });
        });
    }
    
    drawPoint(x, y) {
        const layer = this.layers[this.activeLayerIndex];
        const ctx = layer.ctx;
        
        ctx.globalCompositeOperation = this.isPainting ? 'source-over' : 'destination-out';
        ctx.fillStyle = `rgba(255, 255, 255, ${this.brushOpacity})`;
        ctx.beginPath();
        ctx.arc(x, y, this.brushSize / 2, 0, Math.PI * 2);
        ctx.fill();
    }
    
    drawLine(x1, y1, x2, y2) {
        const dist = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const steps = Math.max(1, Math.floor(dist / 2));
        
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            const x = x1 + (x2 - x1) * t;
            const y = y1 + (y2 - y1) * t;
            this.drawPoint(x, y);
        }
    }
    
    redraw() {
        // Draw background
        this.ctx.putImageData(this.bgImageData, 0, 0);
        
        // Draw all visible layers with color overlays
        this.layers.forEach((layer, idx) => {
            if (!layer.visible) return;
            
            const layerData = layer.ctx.getImageData(0, 0, layer.canvas.width, layer.canvas.height);
            const overlay = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            
            const color = this.hexToRgb(layer.color);
            const isActive = idx === this.activeLayerIndex;
            const opacity = isActive ? 0.5 : 0.3;
            
            for (let i = 0; i < layerData.data.length; i += 4) {
                const alpha = layerData.data[i + 3] / 255;
                if (alpha > 0) {
                    const idx = i;
                    overlay.data[idx] = Math.floor(overlay.data[idx] * (1 - alpha * opacity) + color.r * alpha * opacity);
                    overlay.data[idx + 1] = Math.floor(overlay.data[idx + 1] * (1 - alpha * opacity) + color.g * alpha * opacity);
                    overlay.data[idx + 2] = Math.floor(overlay.data[idx + 2] * (1 - alpha * opacity) + color.b * alpha * opacity);
                }
            }
            
            this.ctx.putImageData(overlay, 0, 0);
        });
    }
    
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : { r: 255, g: 255, b: 255 };
    }
    
    save() {
        const masks = this.layers.map(layer => layer.getMaskData());
        this.onSave(masks);
        this.close();
    }
    
    close() {
        document.removeEventListener('keydown', this.escapeHandler);
        document.removeEventListener('keydown', this.keydownHandler);
        document.removeEventListener('keyup', this.keyupHandler);
        this.backdrop.remove();
    }
}

app.registerExtension({
    name: "Comfy.MultiLayerMaskEditor",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "MultiLayerMaskEditor" && nodeData.name !== "MultiLayerMaskEditorSimple") {
            return;
        }
        
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            
            const imageWidget = this.widgets.find(w => w.name === 'image');
            if (imageWidget) {
                imageWidget.type = "hidden";
                imageWidget.computeSize = () => [0, -4];
            }
            
            const uploadWidget = this.addWidget("button", "choose file to upload", "image", () => {
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = 'image/*';
                fileInput.style.display = 'none';
                document.body.appendChild(fileInput);
                
                fileInput.onchange = async (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        const formData = new FormData();
                        formData.append('image', file);
                        formData.append('subfolder', '');
                        formData.append('type', 'input');
                        
                        try {
                            uploadWidget.value = "Uploading...";
                            const response = await fetch('/upload/image', {
                                method: 'POST',
                                body: formData
                            });
                            const data = await response.json();
                            if (imageWidget) {
                                imageWidget.value = data.name;
                                if (this.maskDataWidget) {
                                    this.maskDataWidget.value = "";
                                    this._lastImage = data.name;
                                }
                            }
                            uploadWidget.value = data.name;
                        } catch (error) {
                            console.error(error);
                            uploadWidget.value = "Upload Failed";
                        }
                    }
                    document.body.removeChild(fileInput);
                };
                
                fileInput.click();
            });
            uploadWidget.serialize = false;
            
            this.addWidget("button", "open_editor", "Open Mask Editor", () => {
                const imageWidget = this.widgets.find(w => w.name === 'image');
                if (!imageWidget || !imageWidget.value || imageWidget.value === "image") {
                    alert('Please upload an image first');
                    return;
                }
                
                // Check if image changed
                if (this.maskDataWidget && this._lastImage && this._lastImage !== imageWidget.value) {
                    this.maskDataWidget.value = "";
                }
                this._lastImage = imageWidget.value;
                
                const numLayersWidget = this.widgets.find(w => w.name === 'num_layers');
                const numLayers = numLayersWidget ? numLayersWidget.value : 5;
                
                const imgSrc = `/view?filename=${encodeURIComponent(imageWidget.value)}&type=input&subfolder=`;
                const img = new Image();
                
                img.onload = async () => {
                    let initialMasks = null;
                    if (this.maskDataWidget && this.maskDataWidget.value) {
                        try {
                            const maskDataValue = this.maskDataWidget.value;
                            
                            if (maskDataValue.endsWith('.json')) {
                                const response = await fetch(`/view?filename=${encodeURIComponent(maskDataValue)}&type=temp&subfolder=masks`);
                                const data = await response.json();
                                initialMasks = [];
                                for (let i = 0; i < numLayers; i++) {
                                    initialMasks.push(data[`layer_${i}`] || null);
                                }
                            } else {
                                const data = JSON.parse(maskDataValue);
                                initialMasks = [];
                                for (let i = 0; i < numLayers; i++) {
                                    initialMasks.push(data[`layer_${i}`] || null);
                                }
                            }
                        } catch (e) {
                            console.error('[MultiLayerMaskEditor] Error loading masks:', e);
                        }
                    }
                    
                    new MaskEditorDialog(img, initialMasks, numLayers, async (masks) => {
                        const maskData = {};
                        masks.forEach((mask, i) => {
                            maskData[`layer_${i}`] = mask;
                        });
                        
                        const filename = `mask_${this.id}_${Date.now()}.json`;
                        const blob = new Blob([JSON.stringify(maskData)], { type: 'application/json' });
                        const formData = new FormData();
                        formData.append('image', blob, filename);
                        formData.append('type', 'temp');
                        formData.append('subfolder', 'masks');
                        
                        try {
                            await fetch('/upload/image', {
                                method: 'POST',
                                body: formData
                            });
                            
                            this.maskDataWidget.value = filename;
                            console.log('[MultiLayerMaskEditor] Saved masks to:', filename);
                        } catch (e) {
                            console.error('[MultiLayerMaskEditor] Failed to save masks:', e);
                        }
                    });
                };
                
                img.src = imgSrc;
            });
            
            const maskDataWidget = ComfyWidgets.STRING(this, "masks_data", ["STRING", { default: "" }], app).widget;
            maskDataWidget.type = "hidden";
            maskDataWidget.computeSize = () => [0, -4];
            this.maskDataWidget = maskDataWidget;
            
            return result;
        };
    }
});