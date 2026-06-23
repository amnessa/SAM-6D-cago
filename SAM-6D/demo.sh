ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

resolve_path() {
	case "$1" in
		/*) printf '%s\n' "$1" ;;
		*) printf '%s/%s\n' "$ROOT_DIR" "$1" ;;
	esac
}

CAD_PATH=$(resolve_path "$CAD_PATH")
RGB_PATH=$(resolve_path "$RGB_PATH")
DEPTH_PATH=$(resolve_path "$DEPTH_PATH")
CAMERA_PATH=$(resolve_path "$CAMERA_PATH")
OUTPUT_DIR=$(resolve_path "$OUTPUT_DIR")

mkdir -p "$OUTPUT_DIR"

# Render CAD templates
cd "$ROOT_DIR/Render"
blenderproc run render_custom_templates.py --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" #--colorize True


# Run instance segmentation model
export SEGMENTOR_MODEL=sam

cd "$ROOT_DIR/Instance_Segmentation_Model"
python run_inference_custom.py --segmentor_model "$SEGMENTOR_MODEL" --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" --rgb_path "$RGB_PATH" --depth_path "$DEPTH_PATH" --cam_path "$CAMERA_PATH"


# Run pose estimation model
export SEG_PATH="$OUTPUT_DIR/sam6d_results/detection_ism.json"

cd "$ROOT_DIR/Pose_Estimation_Model"
python run_inference_custom.py --output_dir "$OUTPUT_DIR" --cad_path "$CAD_PATH" --rgb_path "$RGB_PATH" --depth_path "$DEPTH_PATH" --cam_path "$CAMERA_PATH" --seg_path "$SEG_PATH"

