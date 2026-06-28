import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data", "Input")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data", "Output")

# CAD model is fixed per deployed object (client only sends rgb/depth/camera).
# Override with the CAD_PATH env var if needed.
CAD_PATH = os.environ.get("CAD_PATH", os.path.join(DATA_DIR, "plate.ply"))

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route('/predict_pose', methods=['POST'])
def predict_pose():
    try:
        # Receive the input data
        rgb_input = request.files['rgb']
        depth_input = request.files['depth']
        camera_intrinsics = request.files['camera']

        # Overwrite the input files
        rgb_path = os.path.join(DATA_DIR, "rgb.png")
        depth_path = os.path.join(DATA_DIR, "depth.png")
        camera_path = os.path.join(DATA_DIR, "camera.json")

        rgb_input.save(rgb_path)
        depth_input.save(depth_path)
        camera_intrinsics.save(camera_path)

        print("Input files received and saved.")

        # Trigger the full SAM-6D pipeline via demo.sh
        # (render templates -> instance segmentation -> pose estimation)
        env = os.environ.copy()
        env["CAD_PATH"] = CAD_PATH
        env["RGB_PATH"] = rgb_path
        env["DEPTH_PATH"] = depth_path
        env["CAMERA_PATH"] = camera_path
        env["OUTPUT_DIR"] = OUTPUT_DIR

        process = subprocess.run(
            ["bash", "demo.sh"],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            print("Error during inference:")
            print(process.stderr)
            return jsonify({"error": "Inference failed", "details": process.stderr[-2000:]}), 500

        # Pose estimation writes its result here
        output_file = os.path.join(OUTPUT_DIR, "sam6d_results", "detection_pem.json")

        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                prediction = json.load(f)
            return jsonify({"status": "success", "pose": prediction})
        else:
            return jsonify({
                "status": "error",
                "message": "Prediction file not found. Inference may have failed.",
                "raw_log": process.stdout[-2000:]
            }), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
