import argparse
from pathlib import Path
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit(
        "Missing dependency: Pillow is required to load input images. "
        "Install it (e.g., `pip install pillow`) and re-run."
    )


def load_prompt(view: str) -> str:
    root = Path(__file__).resolve().parent.parent
    prompt_path = root / "prompts" / f"{view}.md"
    if not prompt_path.is_file():
        sys.exit(f"Prompt file not found for view '{view}': {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def load_config() -> dict:
    root = Path(__file__).resolve().parent.parent
    config_path = root / "configs" / "defaults.yaml"
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
    print("Image:")
    for key, value in image_info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
