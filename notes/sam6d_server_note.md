# SAM-6D Project Overview & Inference Pipeline

This document explains the architecture, data flow, and output formats of the SAM-6D deployment.

## 1. API Wrapper (`server.py`)
The `server.py` file implements a Flask web server that provides an interface for remote inference.
- **Input**: Expects a `POST` request to `/predict_pose` containing:
    - `rgb`: The RGB image of the scene.
    - `depth`: The depth map corresponding to the RGB image.
    - `camera`: A JSON file containing camera intrinsics (fx, fy, cx, cy).
- **Workflow**:
    1. Saves incoming files to `SAM-6D/Data/Input`.
    2. Sets environment variables (`CAD_PATH`, `RGB_PATH`, etc.) for the pipeline.
    3. Triggers `bash SAM-6D/demo.sh` using a subprocess.
    4. Reads the final pose from `SAM-6D/Data/Output/sam6d_results/detection_pem.json`.
    5. Returns the JSON prediction to the client.

## 2. The SAM-6D Pipeline (`demo.sh`)
The pipeline follows a three-stage approach:

### Stage A: Template Rendering (Render/)
Uses `blenderproc` to render synthetic views of the target CAD model (`CAD_PATH`). These renders serve as a reference for the subsequent stages.

### Stage B: Instance Segmentation (Instance_Segmentation_Model/)
Uses models like **Segment Anything (SAM)** or **FastSAM** to detect and mask potential object instances in the input RGB image.
- **Output**: `detection_ism.json`.

### Stage $\text{C}$: Pose Estimation (Pose_Estimation_Model/)
Refines the segmentation from Stage B into a 6D pose (Rotation + Translation). It uses point-based matching or feature-based methods to align the rendered templates with the observed image features.
- **Output**: `detection_pem.json`.

## 3. Data Analysis & Formats

### `detection_ism.json` (Instance Segmentation Output)
Contains detected object instances in a format similar to COCO:
- `bbox`: Bounding box coordinates.
- `score`: Confidence of the detection.
- `segmentation`: The mask represented in **COCO RLE (Run-Length Encoding)** format (`counts`).

### `detection_pem.json` (Pose Estimation Output)
The final result of the pipeline:
- Contains the estimated 6D pose (typically rotation vector/matrix and translation vector).
- Provides a confidence score for the predicted pose.

### `detection_ism.npz` (Segmented Data)
A NumPy compressed file containing processed segmentation data, likely masks or feature descriptors extracted from the segmented regions to facilitate fast processing in the Pose Estimation stage.

## 4. Suitability for ICP (Iterative Closest Point)
**Yes, the output is highly suitable for ICP refinement.**

Since the pipeline provides:
1. **Input Depth/RGB**: Allowing you to reconstruct a partial point cloud from the scene.
2. **Segmented Masks**: Allowing you to isolate the points belonging to the target object.
3. **Initial Pose**: `detection_pem.json` provides an excellent initial guess.

**Proposed Workflow for Refinement:**
1. Use the `segmentation` data from `detection_ism.json` to mask the input depth map.
2. Convert the masked depth pixels into a 3D point cloud.
3. Generate a reference point cloud from the rendered CAD template (using the same camera intrinsics).
4. Run **ICP** using the pose from `detection_pem.json` as the starting transformation to minimize the distance between the observed and template point clouds.
