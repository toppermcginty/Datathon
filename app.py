import json
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder=".", static_url_path="")

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "src" / "inputs"
FORM_JSON_PATH = BASE_DIR / "form_data.json"
AI_OUTPUT_PATH = BASE_DIR / "ai_output.json"
MATCH_RESULTS_PATH = BASE_DIR / "match_results.json"

INPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_input_folder():
    for file in INPUT_DIR.iterdir():
        if file.is_file():
            file.unlink()


def map_form_to_shiftkey(form_data: dict) -> dict:
    age_map = {
        "A": "55",
        "B": "45",
        "C": "35",
    }

    margin_map = {
        "D": "not circumscribed",
        "E": "circumscribed",
    }

    shape_map = {
        "J": "oval",
        "K": "round",
        "L": "irregular",
        "M": "not applicable",
    }

    symptoms = []
    if form_data.get("family_history") in ["G", "H"]:
        symptoms.append("family history")
    if "bloody_discharge" in form_data.get("signs", []) or "milky_discharge" in form_data.get("signs", []):
        symptoms.append("nipple discharge")
    if "trauma" in form_data.get("signs", []):
        symptoms.append("breast injury")

    signs = []
    for item in form_data.get("skin_changes", []):
        if item == "warmth":
            signs.append("warmth")
        elif item == "redness":
            signs.append("redness")
        elif item == "peau_dorange":
            signs.append("orange peel")
        elif item == "skin_retraction":
            signs.append("skin retraction")

    if "nipple_retraction" in form_data.get("signs", []):
        signs.append("nipple retraction")

    skin_thickening = "yes" if "skin_thickening" in form_data.get("skin_changes", []) else "no"

    selected_signs = form_data.get("signs", [])
    if "shadowing" in selected_signs and "posterior_enhancement" in selected_signs:
        posterior_features = "combined"
    elif "shadowing" in selected_signs:
        posterior_features = "shadowing"
    elif "posterior_enhancement" in selected_signs:
        posterior_features = "enhancement"
    else:
        posterior_features = "not applicable"

    halo = "yes" if "halo" in selected_signs else "no"

    return {
        "margin": margin_map.get(form_data.get("tumour_edge"), ""),
        "shape": shape_map.get(form_data.get("shape"), ""),
        "echogenicity": "hypoechoic",
        "age": age_map.get(form_data.get("age"), ""),
        "symptoms": symptoms,
        "signs": signs,
        "skin_thickening": skin_thickening,
        "posterior_features": posterior_features,
        "halo": halo,
        "ai_json_path": str(AI_OUTPUT_PATH)
    }


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(".", path)


@app.route("/process-form", methods=["POST"])
def process_form():
    try:
        image = request.files.get("image")
        form_data_raw = request.form.get("form_data")

        if not image:
            return jsonify({"error": "No image uploaded"}), 400
        if not form_data_raw:
            return jsonify({"error": "No form data provided"}), 400

        form_data = json.loads(form_data_raw)

        clear_input_folder()

        filename = secure_filename(image.filename)
        saved_image_path = INPUT_DIR / filename
        image.save(saved_image_path)

        form_data["image_saved_path"] = str(saved_image_path)

        with open(FORM_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(form_data, f, indent=2)

        predict_cmd = [
            sys.executable,
            str(BASE_DIR / "src" / "predict.py"),
            "-i",
            str(INPUT_DIR)
        ]

        predict_result = subprocess.run(
            predict_cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if predict_result.returncode != 0:
            return jsonify({
                "error": "predict.py failed",
                "details": predict_result.stderr
            }), 500

        if not AI_OUTPUT_PATH.exists():
            return jsonify({
                "error": "AI output file was not created",
                "details": "Expected ai_output.json after running predict.py"
            }), 500

        shiftkey_input = map_form_to_shiftkey(form_data)

        logic_cmd = [sys.executable, str(BASE_DIR / "logic.py")]
        logic_result = subprocess.run(
            logic_cmd,
            cwd=BASE_DIR,
            input=json.dumps(shiftkey_input),
            capture_output=True,
            text=True
        )

        if logic_result.returncode != 0:
            return jsonify({
                "error": "logic.py failed",
                "details": logic_result.stderr
            }), 500

        if not MATCH_RESULTS_PATH.exists():
            return jsonify({
                "error": "match_results.json was not created"
            }), 500

        return jsonify({
            "message": "Processing complete",
            "form_data": str(FORM_JSON_PATH),
            "ai_output": str(AI_OUTPUT_PATH),
            "match_results": str(MATCH_RESULTS_PATH)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/results-data", methods=["GET"])
def results_data():
    try:
        data = {
            "form_data": {},
            "ai_output": {},
            "match_results": {}
        }

        if FORM_JSON_PATH.exists():
            with open(FORM_JSON_PATH, "r", encoding="utf-8") as f:
                data["form_data"] = json.load(f)

        if AI_OUTPUT_PATH.exists():
            with open(AI_OUTPUT_PATH, "r", encoding="utf-8") as f:
                data["ai_output"] = json.load(f)

        if MATCH_RESULTS_PATH.exists():
            with open(MATCH_RESULTS_PATH, "r", encoding="utf-8") as f:
                data["match_results"] = json.load(f)

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
