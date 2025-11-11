# curved_tile_preprocessor.py
# Self-contained curved blur batch preprocessor for ComfyUI
# No relative imports; works inside any custom_nodes package.

import io
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn.functional as F

# Use non-interactive backend for headless environments
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _calc_curve(t, curve_type: str, curve_param: float):
    # t in [0,1], vectorized (numpy)
    p = max(float(curve_param), 1e-6)
    if curve_type == "linear":
        return t
    if curve_type == "ease_in":
        return t ** p
    if curve_type == "ease_out":
        return 1.0 - (1.0 - t) ** p
    if curve_type == "ease_in_out":
        left = (2.0 ** (p - 1.0)) * (t ** p)
        right = 1.0 - ((-2.0 * t + 2.0) ** p) / 2.0
        return np.where(t < 0.5, left, right)
    if curve_type == "exponential":
        p = min(max(p, 1e-6), 10.0)
        denom = np.exp(p) - 1.0
        return (np.exp(p * t) - 1.0) / (denom if denom > 1e-12 else 1.0)
    # default
    return t


def _plot_curve(xs, ys, title):
    try:
        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
        ax.plot(xs * 100.0, ys, linewidth=2.5, label="Blur sigma")
        ax.scatter(xs * 100.0, ys, s=36)
        ax.set_xlabel("Generation Progress (%)")
        ax.set_ylabel("Gaussian Sigma (s)")
        ax.set_title(title)
        ax.grid(True, alpha=0.3, linestyle="--")
        ax.legend(loc="best")
        fig.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        im = Image.open(buf).convert("RGBA")
        arr = np.array(im).astype(np.float32) / 255.0
        return torch.from_numpy(arr)[None, :, :, :3]  # drop alpha, keep RGB
    except Exception as e:
        print(f"⚠️  [Curved Blur] Graph generation failed: {e}")
        # Create a simple error message image
        try:
            img = Image.new('RGB', (400, 100), color=(40, 40, 40))
            draw = ImageDraw.Draw(img)
            # Try to use a basic font, fall back to default if needed
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font = ImageFont.load_default()
            draw.text((10, 40), "Graph generation failed", fill=(200, 200, 200), font=font)
            arr = np.array(img).astype(np.float32) / 255.0
            return torch.from_numpy(arr)[None, :, :, :]
        except:
            # Ultimate fallback: blank image
            return torch.zeros((1, 64, 64, 3), dtype=torch.float32)


def _gaussian_kernel1d(sigma: float):
    # Create a 1D kernel length based on sigma (3-sigma rule)
    sigma = max(float(sigma), 1e-6)
    half = max(int(math.ceil(3.0 * sigma)), 1)
    size = 2 * half + 1
    x = torch.arange(-half, half + 1, dtype=torch.float32)
    kernel = torch.exp(-0.5 * (x / sigma) ** 2)
    kernel /= kernel.sum()
    return kernel.view(1, 1, -1)  # (1,1,k)


def _gaussian_blur_tensor(img: torch.Tensor, sigma: float) -> torch.Tensor:
    """
    img: (H,W,C) or (1,H,W,C) float32 in [0,1].
    Returns same shape.
    """
    # Handle sigma = 0 case (no blur)
    if sigma < 0.01:
        return img.clamp(0.0, 1.0)
    
    squeeze = False
    if img.dim() == 3:
        img = img.unsqueeze(0)  # (1,H,W,C)
        squeeze = True

    b, h, w, c = img.shape
    x = img.permute(0, 3, 1, 2).contiguous()  # (B,C,H,W)

    k1d = _gaussian_kernel1d(sigma).to(x.device)
    # Depthwise conv: horizontal then vertical
    # Pad reflect to avoid edge darkening
    pad = k1d.shape[-1] // 2
    # Horizontal
    x = F.pad(x, (pad, pad, 0, 0), mode="reflect")
    x = F.conv2d(x, k1d.expand(c, 1, 1, -1), groups=c)
    # Vertical
    x = F.pad(x, (0, 0, pad, pad), mode="reflect")
    x = F.conv2d(x, k1d.transpose(1, 2).expand(c, 1, -1, 1), groups=c)

    x = x.permute(0, 2, 3, 1).contiguous()
    x = x.clamp(0.0, 1.0)
    if squeeze:
        x = x.squeeze(0)
    return x


class Curved_Blur_Batch_Preprocessor:
    """
    Produces a BATCH of images blurred with increasing (or custom-curved) Gaussian sigma.
    Pair this with a scheduler or batch-to-keyframe mapper so frame i is used at keyframe i.
    
    Note: Sigma values below 0.5 produce minimal blur. Values above 12.0 produce heavy blur.
    Sigma of 0.0 produces no blur (identity).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "num_keyframes": ("INT", {"default": 10, "min": 2, "max": 200, "step": 1}),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "end_percent":   ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                # Blur is expressed as Gaussian sigma (s). Rough rule: radius approx 3*sigma.
                # Recommended: start_sigma 0.5-2.0 (minimal blur), end_sigma 6.0-12.0 (heavy blur)
                "start_sigma":   ("FLOAT", {"default": 0.5, "min": 0.0, "max": 32.0, "step": 0.01}),
                "end_sigma":     ("FLOAT", {"default": 6.0, "min": 0.0, "max": 32.0, "step": 0.01}),
                "curve_type": ([
                    "linear",
                    "ease_in", "ease_out", "ease_in_out",
                    "exponential",
                ], {"default": "linear"}),
                "curve_param": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 10.0, "step": 0.1}),
                "show_graph": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING",)
    RETURN_NAMES = ("batch_images", "curve_graph", "stats",)
    FUNCTION = "execute"
    CATEGORY = "ControlNet Preprocessors/tile"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always recompute when any input changes
        return float("nan")

    def execute(
        self,
        image,
        num_keyframes,
        start_percent,
        end_percent,
        start_sigma,
        end_sigma,
        curve_type,
        curve_param,
        show_graph=True,
    ):
        # Sanity on percents
        start_percent = max(0.0, min(1.0, float(start_percent)))
        end_percent = max(0.0, min(1.0, float(end_percent)))
        if not (start_percent < end_percent):
            end_percent = min(1.0, start_percent + 1e-3)

        # Curve samples
        t = np.linspace(0.0, 1.0, int(num_keyframes))
        curve = np.clip(_calc_curve(t, curve_type, curve_param), 0.0, 1.0)
        sigmas = start_sigma + (end_sigma - start_sigma) * curve
        sigmas = np.clip(sigmas, 0.0, 1e6)

        # Build batch
        frames = []
        for s in sigmas:
            frames.append(_gaussian_blur_tensor(image, float(s)).unsqueeze(0) if image.dim() == 3
                          else _gaussian_blur_tensor(image[0], float(s)).unsqueeze(0))
        batch = torch.cat(frames, dim=0)  # (K,H,W,C)

        # Graph
        xs = np.linspace(start_percent, end_percent, int(num_keyframes))
        graph = _plot_curve(xs, sigmas, f"Blur Curve: {curve_type} (param={curve_param:.2f})") if show_graph \
                else torch.zeros((1, 64, 64, 3), dtype=torch.float32)

        # Stats
        stats = (
            f"Curved Blur Schedule\n"
            f"Keyframes: {num_keyframes}\n"
            f"Percent Range: {start_percent:.3f} -> {end_percent:.3f}\n"
            f"Sigma Range: {float(sigmas.min()):.3f} -> {float(sigmas.max()):.3f}\n"
            f"Curve: {curve_type} (param={curve_param:.2f})\n"
        )

        return (batch, graph, stats)


NODE_CLASS_MAPPINGS = {
    "Curved_Blur_Batch_Preprocessor": Curved_Blur_Batch_Preprocessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Curved_Blur_Batch_Preprocessor": "Curved Blur (Batch)",
}