import os
from pathlib import Path
from huggingface_hub import snapshot_download


def main() -> None:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN environment variable not set")

    target_dir = Path(__file__).resolve().parents[1] / "models" / "DeepSeek-R1"
    snapshot_download(
        repo_id="deepseek-ai/DeepSeek-R1",
        token=token,
        local_dir=str(target_dir),
        local_dir_use_symlinks=False,
    )
    print(f"Model downloaded to {target_dir}")


if __name__ == "__main__":
    main()
