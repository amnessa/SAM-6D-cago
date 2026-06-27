import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

#Paths
BASE_DIR = "/workspace/SAM-6D"
DATA_DIR = os.path.join(BASE_DIR, "Data/Input")
OUTPUT_DIR = os.path.join(BASE_DIR, "Data/Output")

@app.route('/predict_pose', methods=['POST'])
def predict_pose():
    try:
        # Receive the input data
        rgb_input = request.files['rgb']
        depth_input = request.files['depth']
        camera_intrinsics = request.files['camera']

        # Overwrite the input files
        rgb_input.save(os.path.join(DATA_DIR, "rgb.png"))
        depth_input.save(os.path.join(DATA_DIR, "depth.png"))
        camera_intrinsics.save(os.path.join(DATA_DIR, "camera.json"))

        print("Input files received and saved.")

        # Trigger SAM-6D inference
        # we will do it similar to running demo.sh through terminal

        env = os.environ.copy()
        env["CAD_PATH"] = "Data/Input/Object.ply"
        env["RGB_PATH"] = os.path.join(DATA_DIR, "rgb.png")
        env["DEPTH_PATH"] = os.path.join(DATA_DIR, "depth.png")
        env["CAMERA_PATH"] = os.path.join(DATA_DIR, "camera.json")
        env["OUTPUT_PATH"] = OUTPUT_DIR

        process = subprocess.run(
            ["python", "run_inference_custom.py"],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True
        )

        if process.returncode != 0:
            print("Error during inference:")
            print(process.stderr)
            return jsonify({"error": "Inference failed", "details": process.stderr}), 500

        output_file = os.path.join(OUTPUT_DIR, "prediction.json")

        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                prediction = json.load(f)
            return jsonify({"status": "success", "pose": prediction})
        else:
            return jsonify({
                "status": "error",
                "message": "Prediction file not found. Inference may have failed.",
                "raw_log": process.stdout[-500:]  # Return the last 500 characters of the log for debugging
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
