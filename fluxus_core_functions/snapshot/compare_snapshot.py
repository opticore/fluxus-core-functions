import os
import json
import difflib

from filecmp import dircmp
from typing import Annotated

from fluxus_sdk.logger import logger
from fluxus_sdk.func import fluxus_func


@fluxus_func(
    name="compare_snapshots",
    description="Compare snapshots including detailed file content and structured object differences.",
    dir_path="snapshot/",
)
def compare_snapshots(
    snapshot_path_1: Annotated[str, "Path to the first snapshot."],
    snapshot_path_2: Annotated[str, "Path to the second snapshot."],
    show_all_object: Annotated[
        bool, "Show all JSON object comparisons, including unchanged ones."
    ] = False,
    show_all_file: Annotated[
        bool, "Show all file comparisons, including unchanged ones."
    ] = False,
) -> Annotated[dict, "Cleaned and structured differences between snapshots."]:
    """Compare snapshots including detailed file content and structured object differences.

    Args:
        snapshot_path_1 (str): Path to the first snapshot.
        snapshot_path_2 (str): Path to the second snapshot.
        show_all_object (bool): Show all JSON object comparisons, including unchanged ones.
        show_all_file (bool): Show all file comparisons, including unchanged ones.

    Returns:
        diff (dict): Cleaned and structured differences between snapshots.
    """
    if not snapshot_path_1 or not snapshot_path_2:
        logger.error("Both snapshot paths must be provided.")
        return {}

    if not os.path.isdir(snapshot_path_1) or not os.path.isdir(snapshot_path_2):
        logger.error("Both paths must be valid directories.")
        return {}

    diff = {"file_diffs": {}, "object_diffs": {}}

    def read_file_content(file_path):
        with open(file_path, "r", errors="ignore") as file:
            return file.readlines()

    def compare_text_files(file1, file2):
        content1 = read_file_content(file1)
        content2 = read_file_content(file2)
        if content1 == content2:
            return content1 if show_all_file else None
        diff_result = list(difflib.ndiff(content1, content2))
        return [
            line.strip()
            for line in diff_result
            if line.startswith("- ") or line.startswith("+ ")
        ]

    def compare_json_files(file1, file2):
        with open(file1, "r", errors="ignore") as f1:
            try:
                data1 = json.load(f1)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from {file1}: {e}")
                return None

        with open(file2, "r", errors="ignore") as f2:
            try:
                data2 = json.load(f2)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from {file2}: {e}")
                return None

        def remove_private_keys(data):
            if isinstance(data, dict):
                return {
                    k: remove_private_keys(v)
                    for k, v in data.items()
                    if not k.startswith("__")
                }
            elif isinstance(data, list):
                return [remove_private_keys(item) for item in data]
            return data

        data1_clean = remove_private_keys(data1)
        data2_clean = remove_private_keys(data2)

        def generate_diff(d1, d2):
            if isinstance(d1, dict) and isinstance(d2, dict):
                diffs = {}
                for key in set(d1) | set(d2):
                    if key not in d2:
                        diffs[key] = {"status": "removed", "value": d1[key]}
                    elif key not in d1:
                        diffs[key] = {"status": "added", "value": d2[key]}
                    elif d1[key] != d2[key]:
                        diffs[key] = {
                            "status": "modified",
                            "value_1": d1[key],
                            "value_2": d2[key],
                        }
                    elif show_all_object:
                        diffs[key] = {"status": "unchanged", "value": d1[key]}
                return diffs
            elif isinstance(d1, list) and isinstance(d2, list):
                diffs = []
                max_len = max(len(d1), len(d2))
                for i in range(max_len):
                    if i >= len(d1):
                        diffs.append({"status": "added", "value": d2[i]})
                    elif i >= len(d2):
                        diffs.append({"status": "removed", "value": d1[i]})
                    elif d1[i] != d2[i]:
                        diffs.append(
                            {"status": "modified", "value_1": d1[i], "value_2": d2[i]}
                        )
                    elif show_all_object:
                        diffs.append({"status": "unchanged", "value": d1[i]})
                return diffs
            elif d1 != d2:
                return {"status": "modified", "value_1": d1, "value_2": d2}
            elif show_all_object:
                return {"status": "unchanged", "value": d1}
            return None

        return generate_diff(data1_clean, data2_clean)

    def compare_files(file1, file2):
        ext1 = os.path.splitext(file1)[1]
        ext2 = os.path.splitext(file2)[1]
        if ext1 == ".json" and ext2 == ".json":
            return compare_json_files(file1, file2)
        return compare_text_files(file1, file2)

    def compare_directories(dir1, dir2):
        comparison = dircmp(dir1, dir2)

        comparison.left_only = [
            f for f in comparison.left_only if not f.startswith("__")
        ]
        comparison.right_only = [
            f for f in comparison.right_only if not f.startswith("__")
        ]
        comparison.common_files = [
            f for f in comparison.common_files if not f.startswith("__")
        ]
        comparison.common_dirs = [
            d for d in comparison.common_dirs if not d.startswith("__")
        ]

        if comparison.left_only:
            diff.setdefault(f"{dir1} only", []).extend(comparison.left_only)
        if comparison.right_only:
            diff.setdefault(f"{dir2} only", []).extend(comparison.right_only)

        files1 = set(
            f
            for f in os.listdir(dir1)
            if os.path.isfile(os.path.join(dir1, f)) and not f.startswith("__")
        )
        files2 = set(
            f
            for f in os.listdir(dir2)
            if os.path.isfile(os.path.join(dir2, f)) and not f.startswith("__")
        )

        base_to_exts1 = {}
        for filename in files1:
            base, ext = os.path.splitext(filename)
            base_to_exts1.setdefault(base, set()).add(ext)

        base_to_exts2 = {}
        for filename in files2:
            base, ext = os.path.splitext(filename)
            base_to_exts2.setdefault(base, set()).add(ext)

        all_bases = set(base_to_exts1) | set(base_to_exts2)

        for base in all_bases:
            if base.startswith("__"):
                continue

            file_rel_key = os.path.relpath(os.path.join(dir1, base), snapshot_path_1)

            if ".json" in base_to_exts1.get(
                base, set()
            ) and ".json" in base_to_exts2.get(base, set()):
                file1 = os.path.join(dir1, base + ".json")
                file2 = os.path.join(dir2, base + ".json")
                obj_diff = compare_files(file1, file2)
                if obj_diff:
                    diff["object_diffs"][file_rel_key + ".json"] = obj_diff

            elif ".output" in base_to_exts1.get(
                base, set()
            ) and ".output" in base_to_exts2.get(base, set()):
                if ".json" not in base_to_exts1.get(
                    base, set()
                ) and ".json" not in base_to_exts2.get(base, set()):
                    file1 = os.path.join(dir1, base + ".output")
                    file2 = os.path.join(dir2, base + ".output")
                    file_diff = compare_files(file1, file2)
                    if file_diff:
                        diff["file_diffs"][file_rel_key + ".output"] = file_diff

            elif ".cfg" in base_to_exts1.get(
                base, set()
            ) and ".cfg" in base_to_exts2.get(base, set()):
                if ".json" not in base_to_exts1.get(
                    base, set()
                ) and ".json" not in base_to_exts2.get(base, set()):
                    file1 = os.path.join(dir1, base + ".cfg")
                    file2 = os.path.join(dir2, base + ".cfg")
                    file_diff = compare_files(file1, file2)
                    if file_diff:
                        diff["file_diffs"][file_rel_key + ".cfg"] = file_diff

            else:
                if base in base_to_exts1 and base not in base_to_exts2:
                    for ext in base_to_exts1[base]:
                        diff.setdefault(f"{dir1} only", []).append(base + ext)
                if base in base_to_exts2 and base not in base_to_exts1:
                    for ext in base_to_exts2[base]:
                        diff.setdefault(f"{dir2} only", []).append(base + ext)

        for sub_dir in comparison.common_dirs:
            if sub_dir.startswith("__"):
                continue
            compare_directories(
                os.path.join(dir1, sub_dir), os.path.join(dir2, sub_dir)
            )

    compare_directories(snapshot_path_1, snapshot_path_2)

    logger.info("Snapshots compared.")
    if not diff["file_diffs"] and not diff["object_diffs"]:
        logger.info("No differences found between the snapshots.")
        return {}
    logger.info("Differences found between the snapshots.")
    logger.debug(f"File differences: {diff['file_diffs']}")
    logger.debug(f"Object differences: {diff['object_diffs']}")
    return diff
