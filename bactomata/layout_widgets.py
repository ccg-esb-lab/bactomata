"""
layout_widgets.py

Reusable helper functions extracted from the Bactomata layout-generator notebook.

The notebook should still define the workflow step by step. This file contains
the widget, file I/O, color-map, and layout-plotting helpers needed by that
workflow.

This module is self-contained and does not import from DataLoader.py or
OTScriptGenerator.py.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import os
import random
from pathlib import Path

import ipywidgets as widgets
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from IPython.display import display
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch


# -----------------------------------------------------------------------------
# Basic layout file helpers
# -----------------------------------------------------------------------------

def load_matrix_from_file(file_path):
    """
    Load a whitespace-separated layout matrix from file.
    """

    matrix = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()

            if line:
                matrix.append(line.split())

    return matrix


def save_matrix_to_file(matrix, file_path):
    """
    Save a 2D matrix as a whitespace-separated text file.
    """

    with open(file_path, "w") as file:
        for row in matrix:
            file.write(" ".join(map(str, row)) + "\n")


def get_matrix_data(matrix_inputs):
    """
    Extract a matrix from a grid of text widgets.
    Empty cells are converted to '0'.
    """

    matrix = []

    for row in matrix_inputs:
        row_values = []

        for widget in row:
            value = widget.value.strip()
            row_values.append(value if value else "0")

        matrix.append(row_values)

    return matrix



def importPlateLayoutGeneric(thisFileLayoutName, params=None, num_rows=None, num_cols=None):
    """
    Compatibility wrapper replacing the old DataLoader importPlateLayoutGeneric().

    This self-contained version loads a whitespace-separated layout matrix.
    The params, num_rows, and num_cols arguments are accepted for compatibility.
    """

    matrix = load_matrix_from_file(thisFileLayoutName)

    if num_rows is not None and num_cols is not None:
        nrows = int(num_rows)
        ncols = int(num_cols)

        padded = []

        for i in range(nrows):
            if i < len(matrix):
                row = list(matrix[i][:ncols])
            else:
                row = []

            if len(row) < ncols:
                row = row + ["0"] * (ncols - len(row))

            padded.append(row)

        matrix = padded

    return matrix


def importPlateLayout96(thisFileLayoutName, params=None):
    """
    Compatibility wrapper for a 96-well layout.
    """

    return importPlateLayoutGeneric(
        thisFileLayoutName,
        params=params,
        num_rows=8,
        num_cols=12,
    )


def importPlateLayout384(thisFileLayoutName, params=None):
    """
    Compatibility wrapper for a 384-well layout.
    """

    return importPlateLayoutGeneric(
        thisFileLayoutName,
        params=params,
        num_rows=16,
        num_cols=24,
    )


def importPlateLayout(thisFileLayoutName, params=None):
    """
    Compatibility wrapper using params['rows'] and params['cols'] when available.
    """

    if params is None:
        return load_matrix_from_file(thisFileLayoutName)

    return importPlateLayoutGeneric(
        thisFileLayoutName,
        params=params,
        num_rows=params.get("rows", None),
        num_cols=params.get("cols", None),
    )


def loadTreatmentDict(params):
    """
    Compatibility wrapper for loading the media key dictionary.

    New code should use load_key_dict_from_file(params["fileMediaKeyDictName"]).
    This function uses params["fileMediaKeyDictName"] when available and falls
    back to params["fileDictName"] for older notebooks.
    """

    if "fileMediaKeyDictName" in params:
        file_path = params["fileMediaKeyDictName"]
    else:
        file_path = params["fileDictName"]

    return load_key_dict_from_file(file_path)

def get_M_data(matrix_inputs):
    """
    Backward-compatible alias for get_matrix_data().
    """

    return get_matrix_data(matrix_inputs)


def get_unique_keys(matrix_inputs):
    """
    Return unique keys from a matrix widget.
    """

    matrix_data = get_matrix_data(matrix_inputs)
    all_keys = [key for row in matrix_data for key in row]

    return set(all_keys)


def load_trough_layout_from_file(file_path):
    """
    Load a trough layout from a whitespace-separated text file.
    """

    return load_matrix_from_file(file_path)


def save_trough_layout_to_file(trough_layout_string, file_path):
    """
    Save a trough layout string to file.
    """

    with open(file_path, "w") as file:
        file.write(trough_layout_string)


def load_trough_layout(params):
    """
    Load trough layout using params['fileTroughName'].

    Returns a tuple compatible with the old loadTroughLayout() output:
    (trough_layout, trough_layout_vol).
    """

    raw_layout = load_trough_layout_from_file(params["fileTroughName"])

    num_rows = int(params.get("rows", 8))
    num_cols = int(params.get("cols", 12))
    num_wells = num_rows * num_cols

    trough_well = [x for x in range(num_wells)]
    trough_key = ["0" for _ in range(num_wells)]
    trough_vol = [0 for _ in range(num_wells)]

    r = 1
    c = 1

    for line_cols in raw_layout:
        for this_key in line_cols:
            well = r + (c - 1) * 8 - 1

            if 0 <= well < num_wells:
                trough_key[well] = this_key

                if this_key != "0":
                    if params.get("trough_type") == "tube-rack-15_50ml":
                        this_label = getLabelWell(well, params, trough=1)

                        if this_label in ["A3", "A4", "B3", "B4"]:
                            vol_trough = params["max_vol_trough"][1]
                        else:
                            vol_trough = params["max_vol_trough"][0]
                    else:
                        vol_trough = params["max_vol_trough"][0]

                    trough_vol[well] = vol_trough

            c += 1

        r += 1
        c = 1

    trough_layout = dict(zip(trough_well, trough_key))
    trough_layout_vol = dict(zip(trough_well, trough_vol))

    return trough_layout, trough_layout_vol


def loadTroughLayout(params):
    """
    Backward-compatible alias for load_trough_layout().
    """

    return load_trough_layout(params)


def get_inoculation_layout_data(layout_inputs):
    """
    Extract bacteria/inoculation layout data from widget inputs.

    Kept under this name because some current functions still call it.
    """

    return get_matrix_data(layout_inputs)


def create_inoculation_layout_input(default_matrix=None):
    """
    Create a compact bacteria/inoculation layout input grid.

    Backward-compatible helper.
    """

    return create_matrix_input(
        default_matrix=default_matrix,
        nrows=8,
        ncols=12,
        title="Bacteria layout",
    )


def toString(arr2d):
    """
    Return rows of a matrix as tab-separated rows.
    """

    return "\n".join("\t".join(map(str, row)) for row in arr2d)


def toFile(fileName, strOut):
    """
    Write a string to a file.
    """

    with open(fileName, "w") as file_:
        file_.write(strOut)


# -----------------------------------------------------------------------------
# Params
# -----------------------------------------------------------------------------

def getParams(
    fileLayoutName="",
    fileDictName="",
    fileTroughName="",
    fileInoculationName="",
    fileRobotName="",
    max_vol=200,
    num_rows=8,
    num_cols=12,
    num_plates=1,
    sample_vol=20,
):
    """
    Create a parameter dictionary used by the layout-generator workflow.
    """

    params = dict()
    params["fileLayoutName"] = fileLayoutName
    params["fileDictName"] = fileDictName
    params["fileTroughName"] = fileTroughName
    params["fileRobotName"] = fileRobotName
    params["fileInoculationName"] = fileInoculationName

    params["pipette_channels"] = 1
    params["pipette_axis"] = "b"
    params["trough_type"] = "tube-rack-15_50ml"

    params["max_vol_tip"] = max_vol
    params["min_vol_tip"] = 1
    params["dispense_top"] = -2
    params["min_vol_trough"] = 5000.0
    params["max_vol_trough"] = [15000, 45000]

    params["pos_plates"] = ["D1"] * int(num_plates)
    params["pos_trough"] = "A2"
    params["pos_tiprack"] = "A1"
    params["pos_trash"] = "B2"

    params["plate_type"] = "96-PCR-flat"
    params["rows"] = int(num_rows)
    params["cols"] = int(num_cols)
    params["sample_vol"] = sample_vol

    params["randomize"] = False
    params["verbose"] = False
    params["exportOTScript"] = True

    return params


# -----------------------------------------------------------------------------
# Well-label helpers
# -----------------------------------------------------------------------------

def getLabelWell(i, params, trough=0):
    """
    Convert a zero-based well index to an OpenTrons-style well label.
    """

    if trough == 1:
        plate_type = params["trough_type"]
    else:
        plate_type = params["plate_type"]

    label = ""

    if plate_type == "tube-rack-15_50ml":
        if i == 0:
            label = "A1"
        elif i == 1:
            label = "B1"
        elif i == 2:
            label = "C1"
        elif i == 8:
            label = "A2"
        elif i == 9:
            label = "B2"
        elif i == 10:
            label = "C2"
        elif i == 16:
            label = "A3"
        elif i == 17:
            label = "B3"
        elif i == 24:
            label = "A4"
        elif i == 25:
            label = "B4"

    elif plate_type == "384-plate":
        rows = list("ABCDEFGHIJKLMNOP")
        cols = [str(i) for i in range(1, 25)]

        ic = int(i / 16)
        ir = int(i % 16)
        label = "%s%s" % (rows[ir], cols[ic])

    else:
        rows = list("ABCDEFGH")
        cols = [str(i) for i in range(1, 13)]

        ic = int(i / 8)
        ir = int(i % 8)
        label = "%s%s" % (rows[ir], cols[ic])

    return label


# -----------------------------------------------------------------------------
# Key-dictionary widget helpers
# -----------------------------------------------------------------------------

def get_key_data_from_widgets(key_input_widgets, source_keys):
    """
    Extract key-dictionary data from compact input widgets.
    """

    source_keys = list(source_keys)
    key_data = []

    for row in key_input_widgets:
        row_data = {}

        children = list(row.children)

        key_label = children[0]
        input_widgets = children[1:]

        row_data["KEY"] = key_label.value

        for source_key, widget in zip(source_keys, input_widgets):
            row_data[source_key] = widget.value

        key_data.append(row_data)

    return key_data


def create_input_fields_for_keys(
    unique_keys,
    predefined_data=None,
    source_keys=None,
    key_width="90px",
    cell_width="70px",
):
    """
    Create compact key-dictionary input widgets.

    Rows are condition keys from a plate layout. Columns are source keys,
    such as media stocks or bacteria/OV sources.
    """

    input_widgets = []

    if source_keys is None:
        source_keys = ["M"]

    source_keys = list(source_keys)
    unique_keys = sorted(list(unique_keys))

    grid_columns = f"{key_width} " + " ".join([cell_width] * len(source_keys))

    rows = []

    header_widgets = [widgets.HTML("<b>KEY</b>")]
    header_widgets += [
        widgets.HTML(
            f"<b>{source_key}</b>",
            layout=widgets.Layout(width=cell_width),
        )
        for source_key in source_keys
    ]

    header = widgets.GridBox(
        header_widgets,
        layout=widgets.Layout(
            grid_template_columns=grid_columns,
            grid_gap="3px 5px",
            align_items="center",
        ),
    )

    rows.append(header)

    for key in unique_keys:
        key_label = widgets.Label(
            value=str(key),
            layout=widgets.Layout(width=key_width),
        )

        row_widgets = [key_label]
        row_input_widgets = []

        for source_key in source_keys:
            source_value = 0

            if (
                predefined_data
                and key in predefined_data
                and source_key in predefined_data[key]
            ):
                source_value = predefined_data[key][source_key]

            input_widget = widgets.IntText(
                value=int(source_value),
                description="",
                layout=widgets.Layout(width=cell_width),
            )

            row_widgets.append(input_widget)
            row_input_widgets.append(input_widget)

        row = widgets.GridBox(
            row_widgets,
            layout=widgets.Layout(
                grid_template_columns=grid_columns,
                grid_gap="3px 5px",
                align_items="center",
            ),
        )

        rows.append(row)

        input_widgets.append(
            widgets.HBox(
                [widgets.Label(value=str(key))] + row_input_widgets
            )
        )

    table = widgets.VBox(
        rows,
        layout=widgets.Layout(
            border="1px solid #ddd",
            padding="8px",
            width="fit-content",
        ),
    )

    display(table)

    return input_widgets


def load_key_data(file_path):
    """
    Load a tab-separated key dictionary as a dict keyed by KEY.
    """

    key_data = {}

    with open(file_path, "r") as file:
        header = next(file).strip().split("\t")
        source_keys = header[1:]

        for line in file:
            parts = line.strip().split("\t")

            if len(parts) == len(header):
                key = parts[0]
                values = parts[1:]
                key_data[key] = {
                    source_key: int(value)
                    for source_key, value in zip(source_keys, values)
                }

    return key_data


def load_key_dict_from_file(file_path):
    """
    Load a tab-separated key dictionary as a list of dictionaries.
    """

    key_data = []

    with open(file_path, "r") as file:
        lines = [line.strip() for line in file if line.strip()]

    headers = lines[0].split()

    for line in lines[1:]:
        values = line.split()
        item = dict(zip(headers, values))

        for key, value in item.items():
            if key == "KEY":
                continue
            try:
                item[key] = int(value)
            except ValueError:
                try:
                    item[key] = float(value)
                except ValueError:
                    pass

        key_data.append(item)

    return key_data


def setup_key_dict_inputs(
    layout_matrix,
    source_keys,
    key_dict_file,
):
    """
    Create key-dictionary input widgets for the keys present in a layout.
    """

    layout_unique_keys = get_unique_keys_from_nested_list(layout_matrix)

    if os.path.exists(key_dict_file):
        predefined_key_data = load_key_data(key_dict_file)

        key_input_widgets = create_input_fields_for_keys(
            unique_keys=layout_unique_keys,
            predefined_data=predefined_key_data,
            source_keys=source_keys,
        )

    else:
        key_input_widgets = create_input_fields_for_keys(
            unique_keys=layout_unique_keys,
            predefined_data=None,
            source_keys=source_keys,
        )

    return layout_unique_keys, key_input_widgets


def save_key_data_to_file(key_data, file_path):
    """
    Save key-dictionary data to a tab-separated text file.
    """

    if len(key_data) == 0:
        raise ValueError("key_data is empty. Nothing to save.")

    with open(file_path, "w") as file:
        headers = list(key_data[0].keys())

        file.write("\t".join(headers) + "\n")

        for item in key_data:
            line_values = [str(item.get(header, "")) for header in headers]
            line = "\t".join(line_values) + "\n"
            file.write(line)


def save_key_dict_from_widgets(
    key_input_widgets,
    file_path,
    source_keys,
    verbose=True,
):
    """
    Extract key-dictionary data from widgets and save it to file.
    """

    key_data = get_key_data_from_widgets(
        key_input_widgets,
        source_keys=source_keys,
    )

    if verbose:
        print(key_data)
        print(f"\n> Exporting {file_path}")

    save_key_data_to_file(
        key_data,
        file_path,
    )

    return key_data


# -----------------------------------------------------------------------------
# Trough layout widgets
# -----------------------------------------------------------------------------

def create_trough_layout_input(
    default_data=None,
    nrows=3,
    ncols=4,
    title="Trough layout",
    cell_width="75px",
    row_label_width="28px",
):
    """
    Create a compact trough-layout input grid.
    """

    if title is not None:
        display(widgets.HTML(f"<b>{title}</b>"))

    input_fields = []

    row_labels = [chr(ord("A") + i) for i in range(nrows)]
    col_labels = [str(j + 1) for j in range(ncols)]

    grid_items = []

    grid_items.append(
        widgets.HTML(
            "",
            layout=widgets.Layout(width=row_label_width),
        )
    )

    for col_label in col_labels:
        grid_items.append(
            widgets.HTML(
                f"<div style='text-align:center; font-weight:bold;'>{col_label}</div>",
                layout=widgets.Layout(width=cell_width),
            )
        )

    for i in range(nrows):
        row = []

        grid_items.append(
            widgets.HTML(
                f"<div style='text-align:center; font-weight:bold;'>{row_labels[i]}</div>",
                layout=widgets.Layout(width=row_label_width),
            )
        )

        for j in range(ncols):
            default_value = (
                default_data[i][j]
                if default_data is not None
                and i < len(default_data)
                and j < len(default_data[i])
                else ""
            )

            text = widgets.Text(
                value=str(default_value),
                placeholder="SRC",
                description="",
                disabled=False,
                layout=widgets.Layout(
                    width=cell_width,
                    height="30px",
                ),
            )

            row.append(text)
            grid_items.append(text)

        input_fields.append(row)

    grid_template_columns = f"{row_label_width} " + " ".join(
        [cell_width] * ncols
    )

    grid_layout = widgets.GridBox(
        grid_items,
        layout=widgets.Layout(
            grid_template_columns=grid_template_columns,
            grid_gap="2px 3px",
            align_items="center",
            border="1px solid #ddd",
            padding="8px",
            width="fit-content",
        ),
    )

    display(grid_layout)

    return input_fields


def get_trough_layout_data(trough_layout_inputs):
    """
    Extract trough layout data from trough-layout widgets.
    """

    rows = []

    for row in trough_layout_inputs:
        row_values = []

        for widget in row:
            value = widget.value.strip()
            row_values.append(value if value else "0")

        rows.append(" ".join(row_values))

    trough_layout_string = "\n".join(rows)

    return trough_layout_string


def setup_trough_layout_inputs(params, nrows=3, ncols=4):
    """
    Load an existing trough layout if it exists; otherwise create empty inputs.
    """

    fileTroughName = params["fileTroughName"]

    if os.path.exists(fileTroughName):
        predefined_data = load_trough_layout_from_file(fileTroughName)
    else:
        predefined_data = None

    trough_layout_inputs = create_trough_layout_input(
        default_data=predefined_data,
        nrows=nrows,
        ncols=ncols,
        title="Trough layout",
    )

    return trough_layout_inputs


def save_and_load_trough_layout(params, trough_layout_inputs):
    """
    Save the trough layout and reload it.
    """

    trough_layout_string = get_trough_layout_data(trough_layout_inputs)

    trough_unique_keys = get_unique_keys_from_string(trough_layout_string)

    save_trough_layout_to_file(
        trough_layout_string,
        params["fileTroughName"],
    )

    trough_layout = load_trough_layout(params)

    return trough_layout_string, trough_unique_keys, trough_layout


# -----------------------------------------------------------------------------
# Plate layout widgets
# -----------------------------------------------------------------------------

def create_matrix_input(
    default_matrix=None,
    nrows=8,
    ncols=12,
    title=None,
    cell_width="55px",
    row_label_width="28px",
):
    """
    Create a compact plate-layout input grid.
    """

    if title is not None:
        display(widgets.HTML(f"<b>{title}</b>"))

    input_fields = []

    row_labels = [chr(ord("A") + i) for i in range(nrows)]
    col_labels = [str(j + 1) for j in range(ncols)]

    grid_items = []

    grid_items.append(
        widgets.HTML(
            "",
            layout=widgets.Layout(width=row_label_width),
        )
    )

    for col_label in col_labels:
        grid_items.append(
            widgets.HTML(
                f"<div style='text-align:center; font-weight:bold;'>{col_label}</div>",
                layout=widgets.Layout(width=cell_width),
            )
        )

    for i in range(nrows):
        row = []

        grid_items.append(
            widgets.HTML(
                f"<div style='text-align:center; font-weight:bold;'>{row_labels[i]}</div>",
                layout=widgets.Layout(width=row_label_width),
            )
        )

        for j in range(ncols):
            default_value = (
                default_matrix[i][j]
                if default_matrix is not None
                and i < len(default_matrix)
                and j < len(default_matrix[i])
                else ""
            )

            text = widgets.Text(
                value=str(default_value),
                placeholder="KEY",
                description="",
                disabled=False,
                layout=widgets.Layout(
                    width=cell_width,
                    height="30px",
                ),
            )

            row.append(text)
            grid_items.append(text)

        input_fields.append(row)

    grid_template_columns = f"{row_label_width} " + " ".join(
        [cell_width] * ncols
    )

    grid_layout = widgets.GridBox(
        grid_items,
        layout=widgets.Layout(
            grid_template_columns=grid_template_columns,
            grid_gap="2px 3px",
            align_items="center",
            border="1px solid #ddd",
            padding="8px",
            width="fit-content",
        ),
    )

    display(grid_layout)

    return input_fields


def setup_plate_layout_inputs(params, nrows=8, ncols=12):
    """
    Load an existing plate media layout if it exists; otherwise create inputs.
    """

    print("Plate layout")

    fileLayoutName = params["fileLayoutName"]

    if os.path.exists(fileLayoutName):
        Mpre = load_matrix_from_file(fileLayoutName)

        matrix_inputs = create_matrix_input(
            default_matrix=Mpre,
            nrows=nrows,
            ncols=ncols,
        )

    else:
        matrix_inputs = create_matrix_input(
            default_matrix=None,
            nrows=nrows,
            ncols=ncols,
        )

    return matrix_inputs


def get_unique_keys_from_nested_list(M, empty_key="0"):
    """
    Return sorted unique non-empty keys from a nested list.
    """

    unique_keys = set()

    for sublist in M:
        for item in sublist:
            if item != empty_key:
                unique_keys.add(item)

    return sorted(unique_keys)


def get_unique_keys_from_string(layout_string):
    """
    Return unique non-zero keys from a whitespace-separated layout string.
    """

    unique_keys = set()

    for line in layout_string.split("\n"):
        for key in line.split():
            if key != "0":
                unique_keys.add(key)

    return unique_keys


# -----------------------------------------------------------------------------
# Media color-map helpers
# -----------------------------------------------------------------------------

def calculate_color_from_media_legacy(media_values, media_order, max_value=None):
    """
    Legacy media color helper retained from the notebook.
    """

    values = []

    for media in media_order:
        try:
            value = float(media_values.get(media, 0))
        except (TypeError, ValueError):
            value = 0

        values.append(value)

    if max_value is None:
        max_value = max(values) if max(values) > 0 else 1

    values = [int(255 * value / max_value) for value in values]

    r, g, b = 0, 0, 0

    if len(values) > 0:
        b = values[0]
    if len(values) > 1:
        r = values[1]
    if len(values) > 2:
        g = values[2]

    for value in values[3:]:
        r = min(255, r + value // 3)
        g = min(255, g + value // 3)
        b = min(255, b + value // 3)

    return f"#{r:02x}{g:02x}{b:02x}"


def get_source_keys_from_key_dict(key_dict):
    """
    Infer source columns from a key dictionary.
    """

    if len(key_dict) == 0:
        return []

    return [k for k in key_dict[0].keys() if k != "KEY"]


def blend_with_white(color, intensity):
    """
    Blend white with a color.
    """

    intensity = max(0, min(1, float(intensity)))

    r, g, b = to_rgb(color)

    blended = (
        1 - intensity * (1 - r),
        1 - intensity * (1 - g),
        1 - intensity * (1 - b),
    )

    return blended


def make_source_base_colors(source_keys, cmap_name="tab10"):
    """
    Assign one distinct base color to each media source.
    """

    cmap = plt.get_cmap(cmap_name)

    source_colors = {}

    for i, source_key in enumerate(source_keys):
        source_colors[source_key] = cmap(i % cmap.N)

    return source_colors


def calculate_color_from_media(
    media_values,
    media_order,
    source_colors,
    max_value=None,
    empty_color="lightgray",
):
    """
    Calculate a media color from source values.
    """

    values = []

    for source_key in media_order:
        try:
            value = float(media_values.get(source_key, 0))
        except (TypeError, ValueError):
            value = 0

        values.append(value)

    total = sum(values)

    if total == 0:
        return empty_color

    if max_value is None:
        max_value = max(values) if max(values) > 0 else 1

    intensity = min(1, total / max_value)

    r, g, b = 0, 0, 0

    for source_key, value in zip(media_order, values):
        if value == 0:
            continue

        weight = value / total
        cr, cg, cb = to_rgb(source_colors[source_key])

        r += weight * cr
        g += weight * cg
        b += weight * cb

    mixed_color = (r, g, b)

    return blend_with_white(mixed_color, intensity)


def build_media_cmap(
    media_dict,
    empty_color="lightgray",
    cmap_name="tab10",
):
    """
    Build a color map for media keys from the media key dictionary.
    """

    media_source_keys = get_source_keys_from_key_dict(media_dict)

    source_colors = make_source_base_colors(
        media_source_keys,
        cmap_name=cmap_name,
    )

    all_totals = []

    for item in media_dict:
        total = 0

        for source_key in media_source_keys:
            try:
                total += float(item.get(source_key, 0))
            except (TypeError, ValueError):
                pass

        all_totals.append(total)

    max_total = (
        max(all_totals)
        if len(all_totals) > 0 and max(all_totals) > 0
        else 1
    )

    media_cmap = {}

    for item in media_dict:
        media_key = item["KEY"]

        media_values = {
            source_key: item.get(source_key, 0)
            for source_key in media_source_keys
        }

        media_cmap[media_key] = calculate_color_from_media(
            media_values=media_values,
            media_order=media_source_keys,
            source_colors=source_colors,
            max_value=max_total,
            empty_color=empty_color,
        )

    return media_cmap, media_source_keys, source_colors


# -----------------------------------------------------------------------------
# Layout heatmap plotting
# -----------------------------------------------------------------------------

def plotHeatmapFromLayout(params, M, color_map):
    """
    Plot a plate-layout heatmap using a categorical color map.
    """

    nrows = int(params["rows"])
    ncols = int(params["cols"])

    fig, axs = plt.subplots(nrows, ncols, figsize=(14, 8))
    plt.subplots_adjust(hspace=0.4, wspace=0.4)

    legend_handles = [
        Patch(facecolor=color, label=key)
        for key, color in color_map.items()
    ]

    row_labels = list("ABCDEFGHIJKLMNOP")[:nrows]

    for r in range(nrows):
        for c in range(ncols):
            ax = axs[r, c] if nrows > 1 and ncols > 1 else axs[max(r, c)]
            key = M[r][c]
            color = color_map.get(key, "lightgray")

            ax.set_facecolor(color)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)

            if r == nrows - 1:
                ax.set_xlabel(str(c + 1), fontsize=10)
            if c == 0:
                ax.set_ylabel(row_labels[r], fontsize=10)

    plt.figlegend(
        handles=legend_handles,
        loc="upper center",
        ncol=len(legend_handles),
        bbox_to_anchor=(0.5, 0.95),
    )

    plt.show()


# -----------------------------------------------------------------------------
# Bacteria layout helpers
# -----------------------------------------------------------------------------

def setup_bacteria_layout_inputs(params, nrows=8, ncols=12):
    """
    Load an existing bacteria layout if it exists; otherwise create inputs.
    """

    print("Bacteria layout")

    if os.path.exists(params["fileInoculationName"]):
        Bpre = load_matrix_from_file(params["fileInoculationName"])

        bacteria_layout_inputs = create_matrix_input(
            default_matrix=Bpre,
            nrows=nrows,
            ncols=ncols,
        )

    else:
        bacteria_layout_inputs = create_matrix_input(
            default_matrix=None,
            nrows=nrows,
            ncols=ncols,
        )

    return bacteria_layout_inputs


def save_bacteria_layout_from_inputs(params, bacteria_layout_inputs, verbose=True):
    """
    Extract bacteria layout data from widgets and save it.
    """

    B = get_inoculation_layout_data(bacteria_layout_inputs)

    save_matrix_to_file(
        B,
        params["fileInoculationName"],
    )

    if verbose:
        print(f"\n> Exporting {params['fileInoculationName']}")

    return B


def generate_bacteria_cmap(B, empty_key="0", empty_color="lightgray", seed=None):
    """
    Generate a categorical color map for bacteria layout keys.
    """

    rng = random.Random(seed)

    unique_values = sorted(set(val for row in B for val in row))

    bacteria_cmap = {}

    for value in unique_values:
        if value == empty_key:
            bacteria_cmap[value] = empty_color
        else:
            random_color = "#{:02x}{:02x}{:02x}".format(
                rng.randint(0, 255),
                rng.randint(0, 255),
                rng.randint(0, 255),
            )
            bacteria_cmap[value] = random_color

    return bacteria_cmap


def plotBacteriaHeatmap(params, B, color_map):
    """
    Plot a bacteria-layout heatmap using a categorical color map.
    """

    nrows = int(params["rows"])
    ncols = int(params["cols"])

    fig, axs = plt.subplots(nrows, ncols, figsize=(14, 8))
    plt.subplots_adjust(hspace=0.4, wspace=0.4)

    patches = [
        mpatches.Patch(color=color, label=key)
        for key, color in color_map.items()
    ]

    row_labels = list("ABCDEFGHIJKLMNOP")[:nrows]

    for r in range(nrows):
        for c in range(ncols):
            ax = axs[r, c] if nrows > 1 else axs[c]
            key = B[r][c]
            color = color_map.get(key, "lightgray")
            color_rgb = mcolors.to_rgba(color)

            ax.set_facecolor(color_rgb)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)

            if r == nrows - 1:
                ax.set_xlabel(str(c + 1), fontsize=10)
            if c == 0:
                ax.set_ylabel(row_labels[r], fontsize=10)

    fig.legend(
        handles=patches,
        loc="upper center",
        ncol=len(patches),
        bbox_to_anchor=(0.5, 1.05),
    )

    plt.show()
