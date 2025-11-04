import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

// Interactive Canvas Curve Designer Widget
class CanvasCurveWidget {
    constructor(node, inputName, inputData, app) {
        this.node = node;
        this.name = inputName;
        this.app = app;
        
        // Canvas settings
        this.width = 700;
        this.height = 450;
        this.padding = 50;
        
        // Point management
        this.points = [
            { x: 0, y: 1 },
            { x: 0.25, y: 0.75 },
            { x: 0.5, y: 0.5 },
            { x: 0.75, y: 0.25 },
            { x: 1, y: 0 }
        ];
        this.selectedPoint = null;
        this.hoverPoint = null;
        this.isDragging = false;
        
        // Create canvas element
        this.canvas = document.createElement("canvas");
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        this.canvas.style.border = "2px solid #555";
        this.canvas.style.borderRadius = "8px";
        this.canvas.style.cursor = "crosshair";
        this.canvas.style.backgroundColor = "#1a1a1a";
        this.canvas.style.display = "block";
        this.canvas.style.maxWidth = "100%";
        this.canvas.style.height = "auto";
        this.canvas.style.imageRendering = "pixelated"; // Prevent blur on scaling
        
        this.ctx = this.canvas.getContext("2d");
        
        // Mouse event handlers
        this.canvas.addEventListener("mousedown", this.onMouseDown.bind(this));
        this.canvas.addEventListener("mousemove", this.onMouseMove.bind(this));
        this.canvas.addEventListener("mouseup", this.onMouseUp.bind(this));
        this.canvas.addEventListener("mouseleave", this.onMouseLeave.bind(this));
        this.canvas.addEventListener("dblclick", this.onDoubleClick.bind(this));
        
        // Control buttons
        this.buttonContainer = document.createElement("div");
        this.buttonContainer.style.marginTop = "10px";
        this.buttonContainer.style.marginBottom = "10px";
        this.buttonContainer.style.display = "flex";
        this.buttonContainer.style.gap = "8px";
        this.buttonContainer.style.flexWrap = "wrap";
        this.buttonContainer.style.alignItems = "center";
        
        this.createButtons();
        
        // Initial draw
        this.draw();
        
        // Update node with initial points
        this.updateNodePoints();
    }
    
    createButtons() {
        const buttonStyle = `
            padding: 6px 12px;
            background: #333;
            color: #fff;
            border: 1px solid #555;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        `;
        
        const buttons = [
            { label: "Clear All", action: () => this.clearPoints() },
            { label: "Reset Default", action: () => this.resetDefault() },
            { label: "Add Point", action: () => this.addPoint() },
            { label: "Symmetry", action: () => this.makeSymmetric() },
            { label: "Invert Y", action: () => this.invertY() },
            { label: "Sort Points", action: () => this.sortPoints() },
        ];
        
        buttons.forEach(btn => {
            const button = document.createElement("button");
            button.textContent = btn.label;
            button.style.cssText = buttonStyle;
            button.onmouseover = () => button.style.background = "#444";
            button.onmouseout = () => button.style.background = "#333";
            button.onclick = btn.action;
            this.buttonContainer.appendChild(button);
        });
        
        // Info text
        const info = document.createElement("div");
        info.style.cssText = "margin-top: 10px; font-size: 12px; color: #aaa; width: 100%; text-align: center; padding: 8px; background: #222; border-radius: 4px;";
        info.textContent = "💡 Click: Add point | Drag: Move point | Double-click: Delete point";
        this.buttonContainer.appendChild(info);
    }
    
    toCanvasX(normalizedX) {
        return this.padding + normalizedX * (this.width - 2 * this.padding);
    }
    
    toCanvasY(normalizedY) {
        return this.height - this.padding - normalizedY * (this.height - 2 * this.padding);
    }
    
    toNormalizedX(canvasX) {
        return Math.max(0, Math.min(1, (canvasX - this.padding) / (this.width - 2 * this.padding)));
    }
    
    toNormalizedY(canvasY) {
        return Math.max(0, Math.min(2, (this.height - this.padding - canvasY) / (this.height - 2 * this.padding)));
    }
    
    findPointAt(canvasX, canvasY, threshold = 15) {
        for (let i = 0; i < this.points.length; i++) {
            const point = this.points[i];
            const px = this.toCanvasX(point.x);
            const py = this.toCanvasY(point.y);
            const dist = Math.sqrt((canvasX - px) ** 2 + (canvasY - py) ** 2);
            if (dist < threshold) {
                return i;
            }
        }
        return null;
    }
    
    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        
        const pointIndex = this.findPointAt(x, y);
        
        if (pointIndex !== null) {
            // Start dragging existing point
            this.selectedPoint = pointIndex;
            this.isDragging = true;
        } else {
            // Add new point
            const normX = this.toNormalizedX(x);
            const normY = this.toNormalizedY(y);
            this.points.push({ x: normX, y: normY });
            this.sortPoints();
            this.updateNodePoints();
            this.draw();
        }
    }
    
    onMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        
        if (this.isDragging && this.selectedPoint !== null) {
            // Drag point
            const normX = this.toNormalizedX(x);
            const normY = this.toNormalizedY(y);
            this.points[this.selectedPoint] = { x: normX, y: normY };
            this.updateNodePoints();
            this.draw();
        } else {
            // Check hover
            const pointIndex = this.findPointAt(x, y);
            if (pointIndex !== this.hoverPoint) {
                this.hoverPoint = pointIndex;
                this.draw();
            }
        }
    }
    
    onMouseUp(e) {
        if (this.isDragging) {
            this.sortPoints();
        }
        this.isDragging = false;
        this.selectedPoint = null;
    }
    
    onMouseLeave(e) {
        this.isDragging = false;
        this.selectedPoint = null;
        this.hoverPoint = null;
        this.draw();
    }
    
    onDoubleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        
        const pointIndex = this.findPointAt(x, y);
        if (pointIndex !== null && this.points.length > 2) {
            this.points.splice(pointIndex, 1);
            this.updateNodePoints();
            this.draw();
        }
    }
    
    draw() {
        const ctx = this.ctx;
        
        // Clear canvas
        ctx.fillStyle = "#1a1a1a";
        ctx.fillRect(0, 0, this.width, this.height);
        
        // Draw grid
        this.drawGrid();
        
        // Draw curve
        this.drawCurve();
        
        // Draw points
        this.drawPoints();
        
        // Draw axes labels
        this.drawLabels();
    }
    
    drawGrid() {
        const ctx = this.ctx;
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let i = 0; i <= 10; i++) {
            const x = this.padding + (i / 10) * (this.width - 2 * this.padding);
            ctx.beginPath();
            ctx.moveTo(x, this.padding);
            ctx.lineTo(x, this.height - this.padding);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let i = 0; i <= 10; i++) {
            const y = this.padding + (i / 10) * (this.height - 2 * this.padding);
            ctx.beginPath();
            ctx.moveTo(this.padding, y);
            ctx.lineTo(this.width - this.padding, y);
            ctx.stroke();
        }
        
        // Axes
        ctx.strokeStyle = "#666";
        ctx.lineWidth = 2;
        
        // X axis
        ctx.beginPath();
        ctx.moveTo(this.padding, this.height - this.padding);
        ctx.lineTo(this.width - this.padding, this.height - this.padding);
        ctx.stroke();
        
        // Y axis
        ctx.beginPath();
        ctx.moveTo(this.padding, this.padding);
        ctx.lineTo(this.padding, this.height - this.padding);
        ctx.stroke();
    }
    
    drawCurve() {
        if (this.points.length < 2) return;
        
        const ctx = this.ctx;
        
        // Sort points by x for drawing
        const sortedPoints = [...this.points].sort((a, b) => a.x - b.x);
        
        // Draw smooth curve using cardinal spline interpolation
        ctx.strokeStyle = "#4a9eff";
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        const firstPoint = sortedPoints[0];
        ctx.moveTo(this.toCanvasX(firstPoint.x), this.toCanvasY(firstPoint.y));
        
        // Simple interpolation for now
        for (let i = 1; i < sortedPoints.length; i++) {
            const point = sortedPoints[i];
            ctx.lineTo(this.toCanvasX(point.x), this.toCanvasY(point.y));
        }
        
        ctx.stroke();
        
        // Draw filled area under curve
        ctx.fillStyle = "rgba(74, 158, 255, 0.1)";
        ctx.lineTo(this.toCanvasX(sortedPoints[sortedPoints.length - 1].x), this.height - this.padding);
        ctx.lineTo(this.toCanvasX(sortedPoints[0].x), this.height - this.padding);
        ctx.closePath();
        ctx.fill();
    }
    
    drawPoints() {
        const ctx = this.ctx;
        
        this.points.forEach((point, index) => {
            const x = this.toCanvasX(point.x);
            const y = this.toCanvasY(point.y);
            
            // Point circle
            ctx.beginPath();
            ctx.arc(x, y, 8, 0, 2 * Math.PI);
            
            if (index === this.selectedPoint && this.isDragging) {
                ctx.fillStyle = "#ffaa00";
            } else if (index === this.hoverPoint) {
                ctx.fillStyle = "#ff6600";
            } else {
                ctx.fillStyle = "#ff3333";
            }
            ctx.fill();
            
            // Point border
            ctx.strokeStyle = "#fff";
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Point label
            ctx.fillStyle = "#fff";
            ctx.font = "10px monospace";
            ctx.fillText(`P${index + 1}`, x + 12, y - 8);
            ctx.fillStyle = "#aaa";
            ctx.fillText(`(${point.x.toFixed(2)}, ${point.y.toFixed(2)})`, x + 12, y + 4);
        });
    }
    
    drawLabels() {
        const ctx = this.ctx;
        ctx.fillStyle = "#888";
        ctx.font = "12px sans-serif";
        
        // X axis label
        ctx.fillText("Progress (0.0 - 1.0)", this.width / 2 - 50, this.height - 10);
        
        // Y axis label
        ctx.save();
        ctx.translate(15, this.height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText("Strength (0.0 - 2.0)", -50, 0);
        ctx.restore();
        
        // Point count
        ctx.fillStyle = "#aaa";
        ctx.font = "11px monospace";
        ctx.fillText(`Points: ${this.points.length}`, this.width - 80, 20);
    }
    
    sortPoints() {
        this.points.sort((a, b) => a.x - b.x);
        this.updateNodePoints();
        this.draw();
    }
    
    clearPoints() {
        this.points = [{ x: 0, y: 0 }, { x: 1, y: 1 }];
        this.updateNodePoints();
        this.draw();
    }
    
    resetDefault() {
        this.points = [
            { x: 0, y: 1 },
            { x: 0.25, y: 0.75 },
            { x: 0.5, y: 0.5 },
            { x: 0.75, y: 0.25 },
            { x: 1, y: 0 }
        ];
        this.updateNodePoints();
        this.draw();
    }
    
    addPoint() {
        // Add point in the middle
        const newX = 0.5;
        const newY = 0.5;
        this.points.push({ x: newX, y: newY });
        this.sortPoints();
    }
    
    makeSymmetric() {
        // Mirror points around x=0.5
        const leftPoints = this.points.filter(p => p.x <= 0.5);
        const newPoints = [...leftPoints];
        
        leftPoints.forEach(point => {
            if (point.x < 0.5) {
                newPoints.push({ x: 1 - point.x, y: point.y });
            }
        });
        
        this.points = newPoints;
        this.sortPoints();
    }
    
    invertY() {
        // Find max Y
        const maxY = Math.max(...this.points.map(p => p.y), 1);
        this.points.forEach(point => {
            point.y = maxY - point.y;
        });
        this.updateNodePoints();
        this.draw();
    }
    
    updateNodePoints() {
        // Send points to node
        if (this.node && this.node.widgets) {
            const pointsData = JSON.stringify(this.points);
            
            // Find or create the points_data widget
            let pointsWidget = this.node.widgets.find(w => w.name === "points_data");
            if (pointsWidget) {
                pointsWidget.value = pointsData;
            }
        }
    }
    
    getElement() {
        const container = document.createElement("div");
        container.style.cssText = "width: 100%; display: flex; flex-direction: column; align-items: center; padding: 10px; background: #2a2a2a; border-radius: 8px;";
        
        const canvasWrapper = document.createElement("div");
        canvasWrapper.style.cssText = "width: 100%; max-width: 700px; display: flex; justify-content: center;";
        canvasWrapper.appendChild(this.canvas);
        
        container.appendChild(canvasWrapper);
        container.appendChild(this.buttonContainer);
        return container;
    }
}

// Register the custom widget
app.registerExtension({
    name: "comfyui.InteractiveCurveDesigner",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "InteractiveCurveDesigner") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);
                
                // Create canvas widget
                const canvasWidget = new CanvasCurveWidget(this, "canvas", {}, app);
                
                // Add to node
                const widget = this.addDOMWidget("canvas", "CANVAS", canvasWidget.getElement());
                widget.computeSize = function(width) {
                    return [Math.max(700, width), 550]; // Fixed height to prevent squishing
                };
                
                return result;
            };
        }
    }
});

console.log("✅ Interactive Curve Designer widget loaded!");