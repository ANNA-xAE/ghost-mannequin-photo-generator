from pathlib import Path


def _resolve_resolution(config: dict) -> int:
    value = config.get("resolution") if isinstance(config, dict) else None
    if value is None:
        raise ValueError("Configuration missing required key: resolution")
    try:
        resolution = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid resolution value: {value}")
    if resolution <= 0:
        raise ValueError(f"Resolution must be positive: {resolution}")
    return resolution


def generate(image_path, prompt, config, output_path):
    # prompt is accepted for future use; unused in placeholder implementation
    _ = prompt

    from PIL import Image

    resolution = _resolve_resolution(config)
    img_path = Path(image_path)
    if not img_path.is_file():
        raise FileNotFoundError(f"Input image not found: {img_path}")

    with Image.open(img_path) as img:
        img.load()
        scale = min(resolution / img.width, resolution / img.height, 1)
        new_size = (int(img.width * scale), int(img.height * scale))
        resized = img.convert("RGBA")
        if scale < 1:
            resized = resized.resize(new_size, Image.LANCZOS)

        canvas = Image.new("RGBA", (resolution, resolution), "white")
        offset = (
            (resolution - resized.width) // 2,
            (resolution - resized.height) // 2,
        )
        canvas.paste(resized, offset, resized)
        output_path = Path(output_path)
        canvas.convert("RGB").save(output_path, format="PNG")
        return output_path
