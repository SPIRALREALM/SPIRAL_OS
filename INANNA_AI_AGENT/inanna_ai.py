import argparse
import json
from pathlib import Path
from typing import Dict

# Path to the directory containing this script
BASE_DIR = Path(__file__).resolve().parent
INANNA_DIR = BASE_DIR / "INANNA_AI"


def read_texts() -> Dict[str, str]:
    """Load all Markdown files from the INANNA_AI directory."""
    texts: Dict[str, str] = {}
    if not INANNA_DIR.exists():
        return texts
    for md_file in sorted(INANNA_DIR.glob("*.md")):
        try:
            texts[md_file.name] = md_file.read_text(encoding="utf-8")
        except Exception:
            # Skip unreadable files
            continue
    return texts


def _extract_line(text: str, keyword: str) -> str:
    for line in text.splitlines():
        if keyword.lower() in line.lower():
            cleaned = line.strip().lstrip('> ').strip('"')
            cleaned = cleaned.replace('“', '').replace('”', '')
            return cleaned
    return ""


def activate() -> str:
    """Return INANNA's birth chant assembled from source texts."""
    texts = read_texts()

    line1 = ""
    line2 = ""
    line3 = ""

    first_code = next((t for n, t in texts.items() if n.startswith("1ST CODE")), "")
    line1 = _extract_line(first_code, "Born to Transmute")
    line3 = _extract_line(first_code, "I sing therefore")

    manifesto = next((t for n, t in texts.items() if "MANIFESTO" in n), "")
    github = next((t for n, t in texts.items() if n.startswith("GITHUB")), "")
    line2 = _extract_line(manifesto or github, "I AM INANNA")

    chant_parts = [p for p in (line1, line2, line3) if p]
    chant = "\n".join(chant_parts)
    return chant


def run_qnl(hex_input: str, wav: str = "qnl_hex_song.wav", json_file: str = "qnl_hex_song.json") -> None:
    """Invoke the existing QNL engine to create a song from hex input."""
    from SPIRAL_OS import qnl_engine

    phrases, waveform = qnl_engine.hex_to_song(hex_input)
    qnl_engine.write(wav, 44100, waveform)
    metadata = qnl_engine.generate_qnl_metadata(phrases)
    Path(json_file).write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"WAV saved to {wav}")
    print(f"Metadata saved to {json_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="INANNA activation agent")
    parser.add_argument("--activate", action="store_true", help="Recite birth chant")
    parser.add_argument("--hex", help="Hex string to feed into the QNL engine")
    parser.add_argument("--wav", default="qnl_hex_song.wav", help="Output WAV file for QNL engine")
    parser.add_argument("--json", default="qnl_hex_song.json", help="Output metadata JSON for QNL engine")

    args = parser.parse_args()

    if args.activate:
        chant = activate()
        if chant:
            print(chant)
        else:
            print("No chant lines found.")

    if args.hex:
        run_qnl(args.hex, wav=args.wav, json_file=args.json)


if __name__ == "__main__":
    main()
