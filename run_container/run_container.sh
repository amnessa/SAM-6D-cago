#!/bin/bash

# 1. Enable local GUI forwarding for X11 (Open3D, RealSense viewer, etc.)
echo "Enabling X11 forwarding for Docker..."
xhost +local:docker

# 2. Get the current working directory to mount as the workspace
WORKSPACE_DIR="$(pwd)"

# 3. Spin up the modern NVIDIA PyTorch container
echo "Launching SAM-6D Docker environment..."
docker run -it --rm \
  --name sam6d_env \
  --network host \
  --privileged \
  --gpus all \
  -v /dev:/dev \
  -v /dev/bus/usb:/dev/bus/usb \
  -v /run/udev:/run/udev:ro \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v ~/.Xauthority:/root/.Xauthority:rw \
  -v "$WORKSPACE_DIR:/workspace" \
  -e DISPLAY=$DISPLAY \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute,display \
  -e QT_X11_NO_MITSHM=1 \
  -w /workspace \
  lihualiu/sam-6d:1.0 bash