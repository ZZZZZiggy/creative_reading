import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from llm import enrich_with_llm
# Load environment variables
load_dotenv()

# Always write to repo-root data/ (not backend/data/, and not dependent on cwd)
BASE_DIR = Path(__file__).resolve().parent.parent / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
ARTIFACT_DIR = BASE_DIR / "artifacts"

from schemas import DocumentResponse, Block, BlockAnnotations, BilingualAnchor, DocumentMeta


def run_marker_cli(input_pdf: Path, output_folder: Path):
    """
    use marker cli to convert pdf to json
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    cmd = [
        "marker_single",
        str(input_pdf.absolute()),
        "--output_dir", str(output_folder.absolute()),
        "--output_format", "json",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False

def fix_image_paths(data):
    """
    recursively fix image paths in json
    marker output image paths are usually "image.png"
    we need to change them to "images/image.png"
    """
    if isinstance(data, dict):
        if "image" in data and isinstance(data["image"], str):
            # if path does not contain directory prefix, manually add images/
            if not data["image"].startswith("images/"):
                data["image"] = f"images/{data['image']}"
        for k, v in data.items():
            fix_image_paths(v)
    elif isinstance(data, list):
        for item in data:
            fix_image_paths(item)
    return data



def process_pdf(input_pdf: Path, doc_id: str):
    """
    process pdf and return document response
    """
    import shutil

    input_path = Path(input_pdf)
    output_root = ARTIFACT_DIR

    success = run_marker_cli(input_path, output_root)

    if not success:
        return

    # Marker creates a directory with input filename (without extension)
    input_stem = input_path.stem
    marker_output_dir = output_root / input_stem

    # Find the generated JSON file (exclude _meta.json)
    json_file = None
    if marker_output_dir.exists():
        json_files = [f for f in marker_output_dir.glob("*.json") if not f.name.endswith("_meta.json")]
        if json_files:
            json_file = json_files[0]

    if not json_file or not json_file.exists():
        print(f"[Pipeline] Expected JSON not found in {marker_output_dir}")
        return

    # Create target directory for UUID
    target_dir = ARTIFACT_DIR / doc_id
    target_dir.mkdir(parents=True, exist_ok=True)

    # Move JSON file to UUID directory and rename (skip if same path)
    raw_json_path = target_dir / f"{doc_id}.json"
    if json_file.resolve() != raw_json_path.resolve():
        shutil.copy2(json_file, raw_json_path)

    # Move images directory if it exists (skip if same directory)
    images_dir = marker_output_dir / "images"
    target_images_dir = target_dir / "images"
    if images_dir.exists() and images_dir.is_dir() and images_dir.resolve() != target_images_dir.resolve():
        if target_images_dir.exists():
            shutil.rmtree(target_images_dir)
        shutil.move(str(images_dir), str(target_images_dir))

    # read and clean data
    with open(raw_json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # fix image paths (Marker CLI automatically decompresses images to target_dir/images/ but the JSON may not have the prefix)
    final_data = fix_image_paths(raw_data)

    # (optional) insert LLM Enrich logic
    ai_processed_data = enrich_with_llm(final_data, doc_id, input_path.stem)

    # save final data for frontend use
    final_json_path = target_dir / "content.json"
    with open(final_json_path, "w", encoding="utf-8") as f:
        # Convert Pydantic model to dict for JSON serialization
        json.dump(ai_processed_data.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"[Pipeline] Pipeline finished. Ready at: {final_json_path}")

    return
