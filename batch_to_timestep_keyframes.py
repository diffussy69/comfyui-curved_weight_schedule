# batch_to_timestep_keyframes.py
# Robust "Batch Images -> Timestep Keyframes" mapper, compatible across
# TimestepKeyframe signatures, and returns a container with the API that
# Advanced ControlNet expects (has_index, keyframes, etc).

import inspect
from typing import Any, Dict, List
import torch


def _import_timestep_keyframe():
    """Import TimestepKeyframe from our sibling module in a robust way."""
    try:
        from .advanced_curved_controlnet_scheduler import TimestepKeyframe  # type: ignore
        return TimestepKeyframe
    except Exception:
        from advanced_curved_controlnet_scheduler import TimestepKeyframe  # type: ignore
        return TimestepKeyframe


TimestepKeyframe = _import_timestep_keyframe()


class _KeyframeContainer:
    """
    Minimal container matching what downstream code expects:
      - .keyframes (list-like)
      - .has_index(i) -> bool
      - __getitem__(i) to access by index
      - optional .get(i) helper
    """
    def __init__(self, keyframes: List[Any]):
        self.keyframes = list(keyframes)

    def has_index(self, i: int) -> bool:
        try:
            return 0 <= int(i) < len(self.keyframes)
        except Exception:
            return False

    def __getitem__(self, i: int) -> Any:
        return self.keyframes[i]

    def get(self, i: int) -> Any:
        return self.keyframes[i]

    def __iter__(self):
        return iter(self.keyframes)

    def __len__(self):
        return len(self.keyframes)


def _get_keyframe_list(prev_timestep_kf: Any) -> List[Any]:
    """
    Normalize the previous keyframes container to a python list.
    Supports:
      - list of TimestepKeyframe
      - object with `.keyframes`
      - dict-like with 'keyframes'
      - tuple like ( [keyframes], ... )
    """
    if prev_timestep_kf is None:
        return []
    if isinstance(prev_timestep_kf, list):
        return prev_timestep_kf
    if isinstance(prev_timestep_kf, tuple) and prev_timestep_kf and isinstance(prev_timestep_kf[0], list):
        return prev_timestep_kf[0]
    if isinstance(prev_timestep_kf, dict) and "keyframes" in prev_timestep_kf:
        return prev_timestep_kf["keyframes"]
    if hasattr(prev_timestep_kf, "keyframes"):
        return list(getattr(prev_timestep_kf, "keyframes"))
    # last resort: treat as single keyframe
    return [prev_timestep_kf]


def _kf_to_kwargs(kf_obj: Any, accepted: set) -> Dict[str, Any]:
    """Copy fields from an existing keyframe, keeping only those accepted by the constructor."""
    src = {}
    try:
        src = dict(vars(kf_obj))
    except Exception:
        for name in dir(kf_obj):
            if not name.startswith("_"):
                try:
                    src[name] = getattr(kf_obj, name)
                except Exception:
                    pass
    return {k: v for k, v in src.items() if k in accepted}


def _attach_cn_extras(obj: Any, extras: Dict[str, Any]) -> None:
    """If constructor didn't accept cn_extras, attach it post-hoc."""
    try:
        setattr(obj, "cn_extras", extras)
    except Exception:
        pass


class Batch_Images_to_Timestep_Keyframes:
    """
    Maps a BATCH of images (K,H,W,C) to the K keyframes in prev_timestep_kf by index,
    storing the per-index image under keyframe.cn_extras['image'].

    Returns a container with a `.keyframes` attribute and `.has_index(i)` so
    downstream nodes (e.g. Apply Advanced ControlNet) can use it directly.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),                 # (K,H,W,C)
                "prev_timestep_kf": ("TIMESTEP_KEYFRAME",),
                "print_keyframes": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("TIMESTEP_KEYFRAME", "INFO",)
    RETURN_NAMES = ("timestep_kf", "info",)
    FUNCTION = "create_keyframes"
    CATEGORY = "ControlNet/Keyframing"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def create_keyframes(self, images, prev_timestep_kf, print_keyframes=False):
        prev_list = _get_keyframe_list(prev_timestep_kf) or []
        num_prev = len(prev_list)

        if images is None:
            raise ValueError("No images batch provided.")
        if images.dim() == 3:
            images = images.unsqueeze(0)  # (1,H,W,C)
        if images.dim() != 4:
            raise ValueError(f"Expected IMAGE tensor with shape (K,H,W,C); got {tuple(images.shape)}")

        k = images.shape[0]
        n = min(num_prev, k)
        
        # Check for mismatched counts
        # Off-by-one is expected (scheduler often creates N+1 keyframes for boundaries)
        # Only warn if mismatch is 2 or more
        mismatch = abs(k - num_prev)
        
        if mismatch >= 2:
            if k > num_prev:
                print(f"⚠️  [Batch to Timesteps] Warning: {k} images provided but only {num_prev} keyframes exist.")
                print(f"    Only the first {n} image(s) will be mapped.")
            elif k < num_prev:
                print(f"⚠️  [Batch to Timesteps] Warning: {num_prev} keyframes exist but only {k} images provided.")
                print(f"    Only the first {n} keyframe(s) will receive images.")
        elif mismatch == 1:
            # Off-by-one is normal (scheduler boundary behavior) - map silently
            if print_keyframes:
                print(f"[Batch to Timesteps] Note: {num_prev} keyframes, {k} images (off-by-one is normal for schedulers)")
        
        if n == 0:
            return (_KeyframeContainer(prev_list), "No keyframes or images to map.")

        # Which kwargs does the current constructor accept?
        sig = inspect.signature(TimestepKeyframe)
        accepted = set(sig.parameters.keys())
        accepts_cn_extras = "cn_extras" in accepted

        new_kf_list: List[Any] = []
        for i in range(n):
            src_kf = prev_list[i]
            per_k_extras = {"image": images[i]}

            base_kwargs = _kf_to_kwargs(src_kf, accepted)
            if accepts_cn_extras:
                base_kwargs["cn_extras"] = per_k_extras

            try:
                new_kf = TimestepKeyframe(**base_kwargs)
            except TypeError:
                base_kwargs.pop("cn_extras", None)
                new_kf = TimestepKeyframe(**base_kwargs)

            if not accepts_cn_extras:
                _attach_cn_extras(new_kf, per_k_extras)

            new_kf_list.append(new_kf)

        if print_keyframes:
            print("[Batch to Timesteps] index mapping:")
            for i in range(n):
                print(f"  keyframe[{i}] <- image[{i}]")

        info = f"Mapped {n} image(s) to {num_prev} keyframe(s)."
        return (_KeyframeContainer(new_kf_list), info)


NODE_CLASS_MAPPINGS = {
    "Batch_Images_to_Timestep_Keyframes": Batch_Images_to_Timestep_Keyframes,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Batch_Images_to_Timestep_Keyframes": "Batch Images to Timestep Keyframes",
}