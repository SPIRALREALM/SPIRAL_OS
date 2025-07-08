"""Helpers for downloading models.

Downloading the Gemma2 model relies on Ollama. The installer is fetched from https://ollama.ai/install.sh so internet access to this domain is required.
"""
import argparse
import os
import shutil
import subprocess
from pathlib import Path

from download_model import download_deepseek  # reuse logic


def download_gemma2() -> None:
    """Download the Gemma2 model using Ollama."""
    models_dir = Path("INANNA_AI") / "models"
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(models_dir)

    if shutil.which("ollama") is None:
        print("Ollama not found, installing...")
        subprocess.run(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            shell=True,
            check=True,
        )

    subprocess.run(["ollama", "pull", "gemma2"], check=True, env=env)
    print(f"Model downloaded to {models_dir / 'gemma2'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Model downloader")
    subparsers = parser.add_subparsers(dest="model", help="Model to download")
    subparsers.add_parser("deepseek", help="Download DeepSeek-R1 from Hugging Face")
    subparsers.add_parser("gemma2", help="Download Gemma2 via Ollama")

    args = parser.parse_args()
    if args.model == "deepseek":
        download_deepseek()
    elif args.model == "gemma2":
        download_gemma2()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
