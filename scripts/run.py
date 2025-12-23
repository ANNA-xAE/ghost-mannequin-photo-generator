import argparse
from pathlib import Path
import sys


def load_prompt(view: str) -> str:
    root = Path(__file__).resolve().parent.parent
    prompt_path = root / "prompts" / f"{view}.md"
    if not prompt_path.is_file():
        sys.exit(f"Prompt file not found for view '{view}': {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


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

    print(f"Input: {args.input_path}")
    print(f"View: {args.view}")
    print("Prompt:")
    print(prompt_text)


if __name__ == "__main__":
    main()
