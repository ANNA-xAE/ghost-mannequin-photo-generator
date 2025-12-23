import argparse
from pathlib import Path
import sys

DEFAULT_MODE = "preview"
ROOT = Path(__file__).resolve().parent.parent

try:
    from PIL import Image
except ImportError:
    sys.exit(
        "Missing dependency: Pillow is required to load input images. "
        "Install it (e.g., `pip install pillow`) and re-run."
    )


def load_prompt(view: str) -> str:
    prompt_path = ROOT / "prompts" / f"{view}.md"
    if not prompt_path.is_file():
        sys.exit(f"Prompt file not found for view '{view}': {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def load_config() -> dict:
    config_path = ROOT / "configs" / "defaults.yaml"
    if not config_path.is_file():
        sys.exit(f"Configuration file missing: {config_path}")
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        sys.exit(
            "Missing dependency: PyYAML is required to load configs/defaults.yaml. "
            "Install it (e.g., `pip install pyyaml`) and re-run."
        )

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        sys.exit(f"Unexpected configuration format in {config_path}")
    return data


def resolve_resolution(config: dict) -> int:
    value = config.get("resolution") if isinstance(config, dict) else None
    if value is None:
        sys.exit("Configuration missing required key: resolution")
    try:
        resolution = int(value)
    except (TypeError, ValueError):
        sys.exit(f"Invalid resolution value: {value}")
    if resolution <= 0:
        sys.exit(f"Resolution must be positive: {resolution}")
    return resolution


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost mannequin prompt viewer")
    parser.add_argument("--input", required=True, dest="input_path", help="Path to source image")
    parser.add_argument(
        "--view",
        required=True,
        choices=["front", "back", "side"],
        help="Desired catalog view",
    )
    args = parser.parse_args()

    prompt_text = load_prompt(args.view)
    config = load_config()

    mode = config.get("mode", DEFAULT_MODE) if isinstance(config, dict) else DEFAULT_MODE
    if mode not in {"preview", "generate"}:
        sys.exit(f"Unsupported execution mode: {mode}")
    resolution = resolve_resolution(config)

    image_path = Path(args.input_path)
    if not image_path.is_file():
        sys.exit(f"Input image not found: {image_path}")
    try:
        with Image.open(image_path) as img:
            img.load()
            image_info = {
                "filename": image_path.name,
                "format": img.format,
                "mode": img.mode,
                "size": f"{img.width} x {img.height}",
            }
    except OSError as exc:
        sys.exit(f"Failed to open image '{image_path}': {exc}")

    print(f"Input: {args.input_path}")
    print(f"View: {args.view}")
    print("Prompt:")
    print(prompt_text)
    print("Configuration:")
    print(config)
    print(f"Mode: {mode}")
    print("Image:")
    for key, value in image_info.items():
        print(f"  {key}: {value}")

    if mode == "preview":
        print(f"Preview mode: would create {resolution}x{resolution} canvas and write output.png.")
    else:
        output_dir = ROOT / "data" / "output" / image_path.stem / args.view
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {output_dir}")
        try:
            with Image.open(image_path) as img:
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
                output_path = output_dir / "output.png"
                canvas.convert("RGB").save(output_path, format="PNG")
                print(f"Saved: {output_path}")
        except OSError as exc:
            sys.exit(f"Failed to generate output: {exc}")


if __name__ == "__main__":
    main()
