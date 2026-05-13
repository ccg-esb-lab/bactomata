"""
Bactomata parser v0.1

Core tasks:
1. Parse BioTek plate-reader exports into a clean long-format dataframe.
2. Load media and bacteria layouts plus key dictionaries.
3. Annotate each measurement with media_key and bacteria_key.
4. Export a flexible experiment object as PKL.

This version uses the standard names:
- expeID
- media_layout
- bacteria_layout
- key_dict_media
- key_dict_bacteria
"""

from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import pandas as pd


ROW_LABELS_96 = list("ABCDEFGH")
ROW_LABELS_384 = list("ABCDEFGHIJKLMNOP")
WELL_RE = re.compile(r"^[A-P](?:[1-9]|1[0-9]|2[0-4])$")


def read_text_file(path: str | Path) -> str:
    """Read a text file using common encodings used by plate-reader exports."""
    path = Path(path)
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    # Last resort. This should almost never be needed.
    return path.read_text(encoding="latin-1", errors="replace")


def hhmmss_to_hours(value: str) -> float:
    """Convert H:MM:SS or HH:MM:SS to decimal hours."""
    if value is None or pd.isna(value):
        return np.nan
    value = str(value).strip()
    parts = value.split(":")
    if len(parts) != 3:
        return np.nan
    try:
        h, m, s = [float(x) for x in parts]
        return h + m / 60.0 + s / 3600.0
    except ValueError:
        return np.nan


def infer_plate_format_from_wells(wells: List[str]) -> int:
    """Infer plate format from well names."""
    max_row = max(w[0] for w in wells)
    max_col = max(int(w[1:]) for w in wells)
    if max_row <= "H" and max_col <= 12:
        return 96
    if max_row <= "P" and max_col <= 24:
        return 384
    raise ValueError("Could not infer plate format from well names.")


def normalize_signal(raw_label: str) -> str:
    """
    Convert BioTek signal labels into simple names when possible.

    Examples:
    - 'T° Read 2:630' -> 'OD630'
    - 'Read 1:630' -> 'OD630'

    For unknown labels, returns a sanitized version of the raw label.
    """
    raw = str(raw_label).strip()
    # Common BioTek absorbance label: Read 2:630
    match = re.search(r":\s*(\d{3,4})\b", raw)
    if match:
        wl = match.group(1)
        # In the current workflow, 630 is OD/absorbance.
        if wl == "630":
            return "OD630"
        return f"Signal{wl}"
    return re.sub(r"\s+", "_", raw)


def _is_time_header(parts: List[str]) -> bool:
    if len(parts) < 5:
        return False
    if parts[0].strip().lower() != "time":
        return False
    return any(WELL_RE.match(p.strip()) for p in parts[1:])


def parse_biotek_file(path: str | Path, expeID: str, plate_id: str = "Plate1") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Parse a BioTek export file into long format.

    Output dataframe columns:
    expeID, plate_id, time_hhmmss, time, temperature, well, signal, value

    The function prioritizes kinetic/time-series tables. If no kinetic table is
    found, it falls back to endpoint grid tables under the Results section.
    """
    path = Path(path)
    text = read_text_file(path)
    lines = text.splitlines()

    records: List[Dict[str, Any]] = []
    detected_signals: List[str] = []

    # ---- Kinetic/time-series blocks ----
    i = 0
    while i < len(lines):
        parts = lines[i].split("\t")
        if _is_time_header(parts):
            header = [p.strip() for p in parts]
            well_cols = [c for c in header if WELL_RE.match(c)]
            well_indices = [header.index(c) for c in well_cols]

            # The temperature/signal column is usually the second column:
            # 'T° Read 2:630'.
            temp_col_idx: Optional[int] = None
            signal_raw = "signal"
            for idx, col in enumerate(header):
                if "T" in col and "Read" in col:
                    temp_col_idx = idx
                    signal_raw = col
                    break
            if temp_col_idx is None and len(header) > 1:
                temp_col_idx = 1
                signal_raw = header[1]

            signal = normalize_signal(signal_raw)
            detected_signals.append(signal)

            j = i + 1
            while j < len(lines):
                row = lines[j].strip("\n")
                if not row.strip():
                    break
                row_parts = row.split("\t")
                if len(row_parts) < max(well_indices) + 1:
                    break
                if not re.match(r"^\d{1,3}:\d{2}:\d{2}$", row_parts[0].strip()):
                    break

                time_hhmmss = row_parts[0].strip()
                time_h = hhmmss_to_hours(time_hhmmss)
                temperature = np.nan
                if temp_col_idx is not None and temp_col_idx < len(row_parts):
                    try:
                        temperature = float(row_parts[temp_col_idx])
                    except ValueError:
                        temperature = np.nan

                for well, idx_well in zip(well_cols, well_indices):
                    try:
                        value = float(row_parts[idx_well])
                    except ValueError:
                        value = np.nan
                    records.append({
                        "expeID": expeID,
                        "plate_id": plate_id,
                        "time_hhmmss": time_hhmmss,
                        "time": time_h,
                        "temperature": temperature,
                        "well": well,
                        "signal": signal,
                        "value": value,
                    })
                j += 1
            i = j
        else:
            i += 1

    # ---- Endpoint fallback ----
    # If no kinetic table was found, parse endpoint grids of the form:
    # <tab>1<tab>2...<tab>12
    # A<tab>values...<tab>Read 1:630
    if not records:
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split("\t")]
            if len(parts) >= 13 and parts[0] == "" and parts[1:13] == [str(x) for x in range(1, 13)]:
                j = i + 1
                while j < len(lines):
                    row_parts = [p.strip() for p in lines[j].split("\t")]
                    if len(row_parts) < 14 or row_parts[0] not in ROW_LABELS_96:
                        break
                    row_label = row_parts[0]
                    signal = normalize_signal(row_parts[13] if len(row_parts) > 13 else "endpoint")
                    detected_signals.append(signal)
                    for col_idx in range(1, 13):
                        well = f"{row_label}{col_idx}"
                        try:
                            value = float(row_parts[col_idx])
                        except ValueError:
                            value = np.nan
                        records.append({
                            "expeID": expeID,
                            "plate_id": plate_id,
                            "time_hhmmss": "endpoint",
                            "time": np.nan,
                            "temperature": np.nan,
                            "well": well,
                            "signal": signal,
                            "value": value,
                        })
                    j += 1
                break

    data = pd.DataFrame.from_records(records)
    if data.empty:
        raise ValueError(f"No plate-reader data could be parsed from {path}")

    data["row"] = data["well"].str.extract(r"^([A-P])", expand=False)
    data["column"] = data["well"].str.extract(r"^(?:[A-P])(\d+)", expand=False).astype(int)

    metadata = {
        "source_file": path.name,
        "source_path": str(path),
        "plate_format": infer_plate_format_from_wells(sorted(data["well"].unique())),
        "signals": sorted(set(detected_signals)),
        "is_kinetic": bool(data["time"].notna().any() and data["time"].nunique(dropna=True) > 1),
        "has_temperature": bool(data["temperature"].notna().any()),
        "n_timepoints": int(data["time_hhmmss"].nunique()),
        "n_wells": int(data["well"].nunique()),
    }

    return data[[
        "expeID", "plate_id", "time_hhmmss", "time", "temperature",
        "well", "row", "column", "signal", "value"
    ]], metadata


def plate_shape(plate_format: int) -> Tuple[List[str], List[int]]:
    if plate_format == 96:
        return ROW_LABELS_96, list(range(1, 13))
    if plate_format == 384:
        return ROW_LABELS_384, list(range(1, 25))
    raise ValueError("plate_format must be 96 or 384")


def load_layout(path: str | Path, expeID: str, value_name: str, plate_format: int = 96) -> pd.DataFrame:
    """
    Load a whitespace-delimited plate layout into long format.

    value_name should be 'media_key' or 'bacteria_key'.
    """
    path = Path(path)
    rows_expected, cols_expected = plate_shape(plate_format)
    text = read_text_file(path)
    matrix = [line.split() for line in text.splitlines() if line.strip()]

    if len(matrix) != len(rows_expected):
        raise ValueError(f"{path.name}: expected {len(rows_expected)} rows, found {len(matrix)}")
    for idx, row in enumerate(matrix):
        if len(row) != len(cols_expected):
            raise ValueError(f"{path.name}: row {idx + 1} expected {len(cols_expected)} columns, found {len(row)}")

    records = []
    for r_idx, row_label in enumerate(rows_expected):
        for c_idx, col in enumerate(cols_expected):
            records.append({
                "expeID": expeID,
                "well": f"{row_label}{col}",
                "row": row_label,
                "column": col,
                value_name: matrix[r_idx][c_idx],
            })
    return pd.DataFrame.from_records(records)


def load_key_dict(path: str | Path) -> pd.DataFrame:
    """Load a tab- or whitespace-delimited key dictionary."""
    path = Path(path)
    text = read_text_file(path)
    # pandas can infer tab/whitespace if sep is regex whitespace.
    df = pd.read_csv(pd.io.common.StringIO(text), sep=r"\s+", engine="python")
    if "KEY" not in df.columns:
        raise ValueError(f"{path.name}: key dictionary must contain a KEY column")
    return df


def key_dict_to_nested_dict(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Convert a KEY-column dataframe into a nested dictionary."""
    out: Dict[str, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        key = str(row["KEY"])
        out[key] = {col: row[col] for col in df.columns if col != "KEY"}
    return out


def build_well_annotations(
    expeID: str,
    media_layout_path: str | Path,
    bacteria_layout_path: str | Path,
    media_key_dict_path: str | Path,
    bacteria_key_dict_path: str | Path,
    plate_format: int = 96,
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame], List[str]]:
    """Load layouts/key dictionaries and create one annotation row per well."""
    media_layout = load_layout(media_layout_path, expeID, "media_key", plate_format)
    bacteria_layout = load_layout(bacteria_layout_path, expeID, "bacteria_key", plate_format)

    key_dict_media_df = load_key_dict(media_key_dict_path)
    key_dict_bacteria_df = load_key_dict(bacteria_key_dict_path)

    annotations = media_layout.merge(
        bacteria_layout[["expeID", "well", "bacteria_key"]],
        on=["expeID", "well"],
        how="inner",
    )

    annotations["has_media"] = ~annotations["media_key"].isin(["0", "Blank", "blank", "BLANK"])
    annotations["has_bacteria"] = ~annotations["bacteria_key"].isin(["0", "Blank", "blank", "BLANK"])
    annotations["is_blank"] = (~annotations["has_media"]) & (~annotations["has_bacteria"])
    annotations["is_empty"] = annotations["is_blank"]

    warnings: List[str] = []
    media_keys_layout = set(annotations["media_key"].astype(str).unique())
    media_keys_dict = set(key_dict_media_df["KEY"].astype(str).unique())
    missing_media = sorted(media_keys_layout - media_keys_dict)
    if missing_media:
        warnings.append(f"Media keys present in layout but missing from media key dict: {missing_media}")

    bacteria_keys_layout = set(annotations["bacteria_key"].astype(str).unique())
    bacteria_keys_dict = set(key_dict_bacteria_df["KEY"].astype(str).unique())
    missing_bacteria = sorted(bacteria_keys_layout - bacteria_keys_dict)
    if missing_bacteria:
        warnings.append(f"Bacteria keys present in layout but missing from bacteria key dict: {missing_bacteria}")

    return annotations[[
        "expeID", "well", "row", "column", "media_key", "bacteria_key",
        "has_media", "has_bacteria", "is_blank", "is_empty"
    ]], {
        "media": key_dict_media_df,
        "bacteria": key_dict_bacteria_df,
    }, warnings


def build_experiment_object(
    expeID: str,
    plate_reader_path: str | Path,
    media_layout_path: str | Path,
    bacteria_layout_path: str | Path,
    media_key_dict_path: str | Path,
    bacteria_key_dict_path: str | Path,
    trough_layout_path: Optional[str | Path] = None,
    plate_id: str = "Plate1",
    plate_format: Optional[int] = None,
) -> Dict[str, Any]:
    """Build the Bactomata experiment object."""
    measurement_data, reader_metadata = parse_biotek_file(plate_reader_path, expeID=expeID, plate_id=plate_id)
    if plate_format is None:
        plate_format = int(reader_metadata["plate_format"])

    well_annotations, key_dict_dfs, warnings = build_well_annotations(
        expeID=expeID,
        media_layout_path=media_layout_path,
        bacteria_layout_path=bacteria_layout_path,
        media_key_dict_path=media_key_dict_path,
        bacteria_key_dict_path=bacteria_key_dict_path,
        plate_format=plate_format,
    )

    annotated_data = measurement_data.merge(
        well_annotations.drop(columns=["row", "column"]),
        on=["expeID", "well"],
        how="left",
    )

    # Keep row/column from measurement_data; they should agree with annotations.
    missing_annotations = annotated_data["media_key"].isna().sum()
    if missing_annotations:
        warnings.append(f"Measurements missing well annotations: {missing_annotations} rows")

    layouts = {
        "media": load_layout(media_layout_path, expeID, "media_key", plate_format),
        "bacteria": load_layout(bacteria_layout_path, expeID, "bacteria_key", plate_format),
    }
    if trough_layout_path is not None:
        layouts["trough_raw"] = read_text_file(trough_layout_path)

    experiment = {
        "expeID": expeID,
        "plate_format": plate_format,
        "plate_id": plate_id,
        "data": annotated_data,
        "well_annotations": well_annotations,
        "layouts": layouts,
        "key_dicts": {
            "media": key_dict_to_nested_dict(key_dict_dfs["media"]),
            "bacteria": key_dict_to_nested_dict(key_dict_dfs["bacteria"]),
        },
        "key_dict_tables": key_dict_dfs,
        "metadata": {
            "plate_reader": reader_metadata,
        },
        "parser_info": {
            "plate_reader_parser": "biotek",
            "bactomata_version": "0.1.0",
        },
        "warnings": warnings,
        "extra": {},
    }
    return experiment


def save_experiment_pkl(experiment: Dict[str, Any], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        pickle.dump(experiment, f)


def load_experiment_pkl(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("rb") as f:
        return pickle.load(f)


def export_experiment_tables(experiment: Dict[str, Any], output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    expeID = experiment["expeID"]
    experiment["data"].to_csv(output_dir / f"Bactomata_{expeID}_annotated_data.csv", index=False)
    experiment["well_annotations"].to_csv(output_dir / f"Bactomata_{expeID}_well_annotations.csv", index=False)


if __name__ == "__main__":
    # Example run using the uploaded files.
    base = Path("/mnt/data")
    expeID = "BioMe_pilot1"
    experiment = build_experiment_object(
        expeID=expeID,
        plate_reader_path=base / "DO_kinetic_48h_rhizobia_SynComs_9_strains_3_replicates_25042026.txt",
        media_layout_path=base / f"Bactomata_{expeID}_media_layout.txt",
        bacteria_layout_path=base / f"Bactomata_{expeID}_bacteria_layout.txt",
        media_key_dict_path=base / f"Bactomata_{expeID}_media_key_dict.txt",
        bacteria_key_dict_path=base / f"Bactomata_{expeID}_bacteria_key_dict.txt",
        trough_layout_path=base / f"Bactomata_{expeID}_trough_layout.txt",
    )
    save_experiment_pkl(experiment, base / f"Bactomata_{expeID}_parsed.pkl")
    export_experiment_tables(experiment, base)
    print("Parsed rows:", len(experiment["data"]))
    print("Wells:", experiment["data"]["well"].nunique())
    print("Timepoints:", experiment["data"]["time_hhmmss"].nunique())
    print("Signals:", experiment["metadata"]["plate_reader"]["signals"])
    print("Warnings:", experiment["warnings"])
