#!/bin/bash
set -e

echo "=========================================="
echo "Setting up SAM-6D & RealSense D435i Environment"
echo "=========================================="

# 1. Install essential tools and USB utilities
echo "Installing base tools..."
apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git \
    curl \
    wget \
    nano \
    usbutils \
    software-properties-common \
    lsb-release \
    gnupg2

# 2. Mark the workspace as safe for git
git config --global --add safe.directory /workspaces/*

# 3. Add Intel RealSense repository and install SDK tools
echo "Installing Intel RealSense SDK..."
mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.intel.com/Debian/apt-repo/keys.asc | tee /etc/apt/keyrings/realsense.asc > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/realsense.asc] https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/realsense.list

apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    librealsense2-dkms \
    librealsense2-utils \
    librealsense2-dev

# 4. Install the Python wrapper for RealSense
echo "Installing pyrealsense2..."
pip install pyrealsense2

echo "=========================================="
echo "Setup complete!"
echo "Run 'realsense-viewer' in the terminal to verify the D435i connection."
echo "=========================================="