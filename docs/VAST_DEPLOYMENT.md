# Vast.ai Deployment

This guide explains how to run the SPIRAL_OS tools on a Vast.ai server.

## Select a PyTorch template

1. Log in to [Vast.ai](https://vast.ai) and create a new rental.
2. Choose a GPU offer that lists the **PyTorch** template. This image ships with CUDA and Python preinstalled.
3. Launch the instance and connect via SSH once it is ready.

## Clone the repository and install requirements

After connecting to the server run:

```bash
# clone the project
git clone https://github.com/your-user/SPIRAL_OS.git
cd SPIRAL_OS

# install Python packages
pip install -r requirements.txt
```

Optionally install the test requirements with:

```bash
pip install -r tests/requirements.txt
```

## GPU setup and model downloads (optional)

If your instance provides a GPU you can pull model weights. The helper script
below creates directories and fetches models for you:

```bash
bash scripts/setup_vast_ai.sh
```

The script installs dependencies, prepares the `INANNA_AI/models` folder and can
invoke `download_models.py` to pull large checkpoints. Edit the script to suit
your needs.
