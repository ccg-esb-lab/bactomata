"""
DataLoader.py

Robust and backward-compatible utilities for 96/384-well plate layouts,
BioTek/OpenTrons plate-reader files, and the historical DATA structure used by
DataAnalysis.py and DataPlotter.py.

The main compatibility target is the DATA list-of-dicts format:

DATA = [
    {
        'KEY': media_or_treatment_key,
        'reps': [1, 2, ...],
        'B': inoculation_keys,
        'time': [time_array_rep1, time_array_rep2, ...],
        'temp': [temp_array_rep1, temp_array_rep2, ...],
        'ODs': [od_array_rep1, od_array_rep2, ...],
        'pos': [[row_index, col_index], ...]
    },
    ...
]
"""

import os
import re
import random
import pickle
import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np

try:
    import pandas as pd
except ImportError:  # pandas is only needed for some import/export helpers
    pd = None

try:
    from OTScriptGenerator import *  # noqa: F401,F403
except ImportError:
    # This lets the plate-reader utilities work even when the robot-script
    # generator is not available in the current notebook/session.
    pass


# -----------------------------------------------------------------------------
# Basic utilities
# -----------------------------------------------------------------------------

ROW_LABELS_96 = list("ABCDEFGH")
ROW_LABELS_384 = list("ABCDEFGHIJKLMNOP")


def shuffle2d(arr2d, rand=random):
    """Shuffle entries of a 2D array while preserving its shape."""
    reshape = []
    data = []
    iend = 0
    for row in arr2d:
        data.extend(row)
        istart, iend = iend, iend + len(row)
        reshape.append((istart, iend))
    rand.shuffle(data)
    return [data[istart:iend] for (istart, iend) in reshape]


def show(arr2d):
    """Print rows of a matrix as tab-separated rows."""
    print("\n".join("\t".join(map(str, row)) for row in arr2d))


def toString(arr2d):
    """Return rows of a matrix as tab-separated rows."""
    return "\n".join("\t".join(map(str, row)) for row in arr2d)


def unique2d(arr2d, rand=random):
    """Return sorted unique entries from a 2D array/list."""
    vals = []
    for row in arr2d:
        vals.extend(row)
    return sorted(set(vals))


def m_array_index(arr, searchItem):
    """Return all [row, col] positions where arr[row][col] == searchItem."""
    ij = []
    for i, x in enumerate(arr):
        for j, y in enumerate(x):
            if y == searchItem:
                ij.append([i, j])
    return ij


def save_obj(obj, name):
    with open(name, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name, "rb") as f:
        return pickle.load(f)


def _as_file_list(fileDataNames):
    if fileDataNames is None:
        return []
    if isinstance(fileDataNames, (str, os.PathLike)):
        return [str(fileDataNames)]
    return [str(x) for x in fileDataNames]


def get_plate_shape(params: Optional[Dict[str, Any]] = None,
                    num_rows: Optional[int] = None,
                    num_cols: Optional[int] = None) -> Tuple[int, int]:
    """Infer plate dimensions from params or explicit values."""
    if params is None:
        params = {}
    rows = int(num_rows if num_rows is not None else params.get("rows", 8))
    cols = int(num_cols if num_cols is not None else params.get("cols", 12))
    return rows, cols


def _row_labels(num_rows: int) -> List[str]:
    if num_rows <= 8:
        return ROW_LABELS_96[:num_rows]
    if num_rows <= 16:
        return ROW_LABELS_384[:num_rows]
    return [chr(ord("A") + i) for i in range(num_rows)]


# -----------------------------------------------------------------------------
# Well-label utilities
# -----------------------------------------------------------------------------


def getLabelFromPos(which_well, num_rows: int = 8, num_cols: int = 12):
    """
    Convert [row, col] zero-based position or one-based well number to label.

    Examples
    --------
    getLabelFromPos([0, 0]) -> 'A1'
    getLabelFromPos(1) -> 'A1'
    """
    rows = _row_labels(num_rows)
    cols = [str(i + 1) for i in range(num_cols)]

    if isinstance(which_well, (list, tuple, np.ndarray)):
        irow, icol = int(which_well[0]), int(which_well[1])
        return f"{rows[irow]}{cols[icol]}"

    well_number = int(which_well)
    if well_number < 1 or well_number > num_rows * num_cols:
        raise ValueError(f"well number must be between 1 and {num_rows * num_cols}")
    zero_index = well_number - 1
    irow = zero_index // num_cols
    icol = zero_index % num_cols
    return f"{rows[irow]}{cols[icol]}"


def getLabelWell96(which_well):
    """Backward-compatible 96-well label helper."""
    return getLabelFromPos(which_well, num_rows=8, num_cols=12)


def getLabelWell(which_well, num_rows: int = 8, num_cols: int = 12):
    """Generic label helper kept for old code that used getLabelWell()."""
    return getLabelFromPos(which_well, num_rows=num_rows, num_cols=num_cols)


def getPosWell(well_label, num_rows: int = 8, num_cols: int = 12):
    """Convert a well label like 'A1' or 'H12' to [row, col] zero-based indices."""
    if well_label is None:
        raise ValueError("well_label cannot be None")
    well_label = str(well_label).strip().upper()
    match = re.fullmatch(r"([A-Z]+)(\d+)", well_label)
    if match is None:
        raise ValueError(f"Invalid well label: {well_label}")

    row_label, col_label = match.groups()
    rows = _row_labels(num_rows)
    if row_label not in rows:
        raise ValueError(f"Invalid row '{row_label}' for a {num_rows}-row plate")
    irow = rows.index(row_label)
    icol = int(col_label) - 1
    if icol < 0 or icol >= num_cols:
        raise ValueError(f"Invalid column '{col_label}' for a {num_cols}-column plate")
    return [irow, icol]


def getNumWell(well_label, num_rows: int = 8, num_cols: int = 12):
    """
    Return zero-based well index in row-major order.

    This preserves the behavior of the previous function where A1 returned 0.
    """
    irow, icol = getPosWell(well_label, num_rows=num_rows, num_cols=num_cols)
    return num_cols * irow + icol


def getWellIndex(pos, num_rows: int = 8, num_cols: int = 12):
    """Return zero-based well index in row-major order from [row, col]."""
    irow, icol = int(pos[0]), int(pos[1])
    if 0 <= irow < num_rows and 0 <= icol < num_cols:
        return icol + num_cols * irow
    return None


def get_well_label(well_index, num_rows, num_cols, zero_based: bool = True):
    """
    Convert well index to label.

    By default, well_index is zero-based because most plate-reader exports use
    zero-based well_id. Use zero_based=False for one-based indices.
    """
    idx = int(well_index)
    if not zero_based:
        idx -= 1
    if idx < 0 or idx >= int(num_rows) * int(num_cols):
        raise ValueError(f"well_index {well_index} is outside the plate")
    irow = idx // int(num_cols)
    icol = idx % int(num_cols)
    return getLabelFromPos([irow, icol], num_rows=int(num_rows), num_cols=int(num_cols))


# -----------------------------------------------------------------------------
# Params
# -----------------------------------------------------------------------------


def getParams(fileLayoutName='', fileDictName='', fileTroughName='',
              fileInoculationName='', fileRobotName='', max_vol=200,
              num_rows=8, num_cols=12, num_plates=1, sample_vol=20):
    params = dict()
    params['fileLayoutName'] = fileLayoutName
    params['fileDictName'] = fileDictName
    params['fileTroughName'] = fileTroughName
    params['fileRobotName'] = fileRobotName
    params['fileInoculationName'] = fileInoculationName

    params['pipette_channels'] = 1
    params['pipette_axis'] = 'b'
    params['trough_type'] = 'tube-rack-15_50ml'

    params['max_vol_tip'] = max_vol
    params['min_vol_tip'] = 1
    params['dispense_top'] = -2
    params['min_vol_trough'] = 5000.0
    params['max_vol_trough'] = [15000, 45000]

    params['pos_plates'] = ['D1'] * int(num_plates)
    params['pos_trough'] = 'A2'
    params['pos_tiprack'] = 'A1'
    params['pos_trash'] = 'B2'

    params['plate_type'] = '96-PCR-flat'
    params['rows'] = int(num_rows)
    params['cols'] = int(num_cols)
    params['sample_vol'] = sample_vol

    params['randomize'] = False
    params['verbose'] = False
    params['exportOTScript'] = True

    return params


# -----------------------------------------------------------------------------
# Layout importers
# -----------------------------------------------------------------------------


def _read_layout_file(thisFileLayoutName):
    with open(thisFileLayoutName, 'r') as f:
        return f.readlines()


def importPlateLayoutGeneric(thisFileLayoutName, params=None, num_rows=None, num_cols=None):
    """
    Import a tab/space-separated plate layout.

    Blank lines separate plates. Values are stored as strings.
    """
    if params is None:
        params = {}
    rows, cols = get_plate_shape(params, num_rows, num_cols)
    numPlates = len(params.get('pos_plates', ['D1']))

    M = [['x' for _ in range(cols)] for _ in range(rows * numPlates)]
    dataLayout = _read_layout_file(thisFileLayoutName)

    plate = 0
    row = 0
    for raw_line in dataLayout:
        line = raw_line.strip()
        if not line:
            if row > 0:
                plate += 1
                row = 0
            continue

        values = line.split()
        if row >= rows:
            plate += 1
            row = 0
        if plate >= numPlates:
            # Expand if file contains more plates than params expected.
            M.extend([['x' for _ in range(cols)] for _ in range(rows)])
            numPlates += 1
        for col, value in enumerate(values[:cols]):
            M[rows * plate + row][col] = value
        row += 1

    return M


def importPlateLayout96(thisFileLayoutName, params=None):
    return importPlateLayoutGeneric(thisFileLayoutName, params=params, num_rows=8, num_cols=12)


def importPlateLayout384(thisFileLayoutName, params=None):
    return importPlateLayoutGeneric(thisFileLayoutName, params=params, num_rows=16, num_cols=24)


def importPlateLayout(thisFileLayoutName, params=None):
    rows, cols = get_plate_shape(params)
    return importPlateLayoutGeneric(thisFileLayoutName, params=params, num_rows=rows, num_cols=cols)


def importInoculationLayout96(params):
    return importPlateLayoutGeneric(params['fileInoculationName'], params=params, num_rows=8, num_cols=12)


def importInoculationLayout384(params):
    return importPlateLayoutGeneric(params['fileInoculationName'], params=params, num_rows=16, num_cols=24)


def importInoculationLayout(params):
    rows, cols = get_plate_shape(params)
    return importPlateLayoutGeneric(params['fileInoculationName'], params=params, num_rows=rows, num_cols=cols)


# -----------------------------------------------------------------------------
# DATA access helpers
# -----------------------------------------------------------------------------


def getNumReps(DATA):
    if not DATA:
        return 0
    return len(DATA[0].get('reps', []))


def _get_time_for_rep(thisDATA, pos_index):
    time_value = thisDATA.get('time', [])
    if isinstance(time_value, np.ndarray):
        return time_value
    if isinstance(time_value, list):
        if len(time_value) == 0:
            return []
        if len(time_value) == len(thisDATA.get('ODs', [])):
            return time_value[pos_index]
        return time_value
    return time_value


def _get_temp_for_rep(thisDATA, pos_index):
    temp_value = thisDATA.get('temp', [])
    if isinstance(temp_value, np.ndarray):
        return temp_value
    if isinstance(temp_value, list):
        if len(temp_value) == 0:
            return []
        if len(temp_value) == len(thisDATA.get('ODs', [])):
            return temp_value[pos_index]
        return temp_value
    return temp_value


def getInfoWell(DATA, well_label):
    """Return metadata and measurements for a given well label."""
    thisPos = getPosWell(well_label)
    for thisDATA in DATA:
        for j, pos in enumerate(thisDATA.get('pos', [])):
            if pos == thisPos:
                return {
                    'KEY': thisDATA.get('KEY'),
                    'B': thisDATA.get('B', [None])[j],
                    'pos': pos,
                    'rep': thisDATA.get('reps', [None])[j],
                    'ODs': thisDATA.get('ODs', [None])[j],
                    'time': _get_time_for_rep(thisDATA, j),
                    'temp': _get_temp_for_rep(thisDATA, j),
                }
    return {}


def getDataWell(DATA, well_label):
    """Return ODs/time/temp for a given well label."""
    info = getInfoWell(DATA, well_label)
    if not info:
        return {}
    return {'ODs': info.get('ODs', []), 'time': info.get('time', []), 'temp': info.get('temp', [])}


def getDataFromPos(DATA, well_label):
    """Backward-compatible alias for getDataWell()."""
    return getDataWell(DATA, well_label)


def getODs(DATA, KEY, B):
    """Return OD series for a treatment KEY and inoculum/community key B."""
    for thisDATA in DATA:
        if thisDATA.get('KEY') == KEY:
            for od, b in zip(thisDATA.get('ODs', []), thisDATA.get('B', [])):
                if b == B:
                    return od
    return []


def getTimes(DATA, KEY, B):
    """Return time series for a treatment KEY and inoculum/community key B."""
    for thisDATA in DATA:
        if thisDATA.get('KEY') == KEY:
            for j, b in enumerate(thisDATA.get('B', [])):
                if b == B:
                    return _get_time_for_rep(thisDATA, j)
    return []


# -----------------------------------------------------------------------------
# OpenTrons / generic time-series importer
# -----------------------------------------------------------------------------


def importODTime(params, fileDataNames):
    """
    Import a tab-separated time-series file with columns well_id, Timestamp, OD.

    Returns a dict keyed by well labels, e.g. {'A1': {'ODs': array, 'time': array}}.
    """
    if pd is None:
        raise ImportError("pandas is required for importODTime()")

    well_data = {}
    num_rows, num_cols = get_plate_shape(params)
    verbose = bool(params.get('verbose', False))

    for thisDataFile in _as_file_list(fileDataNames):
        data_df = pd.read_csv(thisDataFile, sep='\t')
        required = {'well_id', 'Timestamp', 'OD'}
        missing = required.difference(data_df.columns)
        if missing:
            raise ValueError(f"Missing required columns in {thisDataFile}: {missing}")

        data_df['Timestamp'] = pd.to_datetime(data_df['Timestamp'])
        for well_id, group in data_df.groupby('well_id'):
            well_label = get_well_label(well_id, num_rows, num_cols, zero_based=True)
            group = group.sort_values('Timestamp')
            ODs = group['OD'].astype(float).values
            start_time = group['Timestamp'].iloc[0]
            time_in_minutes = (group['Timestamp'] - start_time).dt.total_seconds().values / 60

            if verbose:
                print(well_id, well_label)

            well_data[well_label] = {
                'ODs': np.around(ODs, decimals=3),
                'time': np.asarray(time_in_minutes, dtype=float)
            }

    return well_data


def compileDataTime(M, B, well_data, include_empty_keys: bool = False):
    """Compile well_data into the historical DATA structure."""
    DATA = []
    keys = unique2d(M)

    for k in keys:
        reps, repODs, repTimes, repTemps, Bs, pos = [], [], [], [], [], []
        for row_index, row in enumerate(M):
            for col_index, key in enumerate(row):
                if key != k:
                    continue
                well_label = getLabelFromPos([row_index % len(B), col_index])
                if well_label not in well_data:
                    continue
                this_data = well_data[well_label]
                thisB = B[row_index][col_index] if row_index < len(B) and col_index < len(B[row_index]) else None

                reps.append(len(repODs) + 1)
                repODs.append(np.asarray(this_data.get('ODs', []), dtype=float))
                repTimes.append(np.asarray(this_data.get('time', []), dtype=float))
                repTemps.append(np.asarray(this_data.get('temp', [])))
                Bs.append(thisB)
                pos.append([row_index, col_index])

        if repODs or include_empty_keys:
            DATA.append({'KEY': k, 'reps': reps, 'B': Bs, 'time': repTimes,
                         'temp': repTemps, 'ODs': repODs, 'pos': pos})

    return DATA


# -----------------------------------------------------------------------------
# BioTek importers
# -----------------------------------------------------------------------------


def _parse_time_to_minutes(value: str) -> float:
    value = str(value).strip()
    parts = value.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return datetime.timedelta(hours=int(hours), minutes=int(minutes),
                                  seconds=float(seconds)).total_seconds() / 60
    if len(parts) == 2:
        minutes, seconds = parts
        return datetime.timedelta(minutes=int(minutes), seconds=float(seconds)).total_seconds() / 60
    return float(value)


def _is_time_token(token: str) -> bool:
    return re.fullmatch(r"\d+(:\d+){1,2}(\.\d+)?", str(token).strip()) is not None


def _to_float_or_nan(x):
    try:
        return float(str(x).replace(',', '.'))
    except ValueError:
        return np.nan


def importDataOD_BioTeK(fileDataNames, params: Optional[Dict[str, Any]] = None):
    """
    Import a BioTek endpoint plate matrix.

    Expected section: rows beginning with A, B, ..., H for 96-well plates.
    Returns a 2D list of strings/floats with shape rows*num_plates by cols.
    """
    if params is None:
        params = {}
    rows, cols = get_plate_shape(params)
    row_labels = _row_labels(rows)
    files = _as_file_list(fileDataNames)

    DATA = []
    for thisDataFile in files:
        plate = [['x' for _ in range(cols)] for _ in range(rows)]
        with open(thisDataFile, 'r', errors='ignore') as fileData:
            for line in fileData:
                line_cols = line.strip().split()
                if not line_cols:
                    continue
                row_label = line_cols[0].upper()
                if row_label in row_labels:
                    r = row_labels.index(row_label)
                    values = line_cols[1:1 + cols]
                    for c, value in enumerate(values):
                        plate[r][c] = value
        DATA.extend(plate)

    return DATA


def importODTime_BioTeK(fileDataNames, params: Optional[Dict[str, Any]] = None,
                        num_rows: Optional[int] = None, num_cols: Optional[int] = None,
                        verbose: Optional[bool] = None):
    """
    Import BioTek kinetic OD exports.

    The parser looks for lines of the form:
        time<TAB>temperature<TAB>well1<TAB>well2...well96

    Returns
    -------
    [DATA_time, DATA_temp, DATA_OD]
        DATA_time : list of minutes
        DATA_temp : list of temperatures, as strings or floats when possible
        DATA_OD   : list of OD arrays, one array per well, row-major order.
                    With multiple files/plates, wells are appended plate by plate.
    """
    if params is None:
        params = {}
    rows, cols = get_plate_shape(params, num_rows, num_cols)
    expected_wells = rows * cols
    verbose = bool(params.get('verbose', False) if verbose is None else verbose)

    all_OD_by_well = []
    reference_time = None
    reference_temp = None

    for thisDataFile in _as_file_list(fileDataNames):
        ODs = []
        DATA_time = []
        DATA_temp = []

        with open(thisDataFile, 'r', errors='ignore') as fileData:
            for line in fileData:
                line_cols = line.strip().split()
                if len(line_cols) < 2 + expected_wells:
                    continue
                if not _is_time_token(line_cols[0]):
                    continue

                values = [_to_float_or_nan(x) for x in line_cols[2:2 + expected_wells]]
                if len(values) != expected_wells:
                    continue

                DATA_time.append(_parse_time_to_minutes(line_cols[0]))
                temp_value = _to_float_or_nan(line_cols[1])
                DATA_temp.append(temp_value if not np.isnan(temp_value) else line_cols[1])
                ODs.append(values)

        if not ODs:
            raise ValueError(f"No kinetic BioTek OD data found in {thisDataFile}")

        npODs = np.asarray(ODs, dtype=float)
        if reference_time is None:
            reference_time = DATA_time
            reference_temp = DATA_temp
        elif len(DATA_time) != len(reference_time) or not np.allclose(DATA_time, reference_time):
            if verbose:
                print(f"Warning: time vector differs in {thisDataFile}; using per-well OD arrays with reference time from first file.")

        if verbose:
            print(f"Loaded {thisDataFile}")
            print(f"Time points: {len(DATA_time)}")
            print(f"Wells: {expected_wells}")

        for iwell in range(expected_wells):
            all_OD_by_well.append(np.around(npODs[:, iwell], decimals=3))

    return [reference_time or [], reference_temp or [], all_OD_by_well]


def compileDataTime_BioTeK(M, B, time, temp, OD, params: Optional[Dict[str, Any]] = None,
                           include_empty_keys: bool = False):
    """
    Compile BioTek kinetic data into the historical DATA structure.

    Fixes the old indexing bug. The correct row-major well index is:
        well_index = row * num_cols + col
    """
    rows, cols = get_plate_shape(params)
    DATA = []
    keys = unique2d(M)

    for k in keys:
        reps, repODs, repTimes, repTemps, Bs, pos = [], [], [], [], [], []
        for rep, ij in enumerate(m_array_index(M, k)):
            row_index, col_index = int(ij[0]), int(ij[1])
            well_index = row_index * cols + col_index
            if well_index < 0 or well_index >= len(OD):
                continue

            thisOD = np.asarray(OD[well_index], dtype=float)
            thisB = B[row_index][col_index] if row_index < len(B) and col_index < len(B[row_index]) else None

            reps.append(len(repODs) + 1)
            repODs.append(thisOD)
            repTimes.append(np.asarray(time, dtype=float))
            repTemps.append(np.asarray(temp))
            Bs.append(thisB)
            pos.append([row_index, col_index])

        if repODs or include_empty_keys:
            DATA.append({'KEY': k, 'reps': reps, 'B': Bs, 'time': repTimes,
                         'temp': repTemps, 'ODs': repODs, 'pos': pos})

    return DATA


def ignoreWells(OD, ignore_wells):
    """Mark selected wells in a 2D OD matrix as -1."""
    for this_well in ignore_wells:
        if len(str(this_well).strip()) > 0:
            well = str(this_well).strip()
            print(f"Ignoring well: {well}")
            irow, icol = getPosWell(well)
            OD[irow][icol] = '-1'
    return OD


# -----------------------------------------------------------------------------
# Endpoint OD compatibility helpers
# -----------------------------------------------------------------------------


def importData0(fileDataNames):
    """Backward-compatible alias for endpoint BioTek OD import."""
    return importDataOD_BioTeK(fileDataNames)


def importDataOD(fileDataNames, params: Optional[Dict[str, Any]] = None):
    """Backward-compatible endpoint OD import name."""
    return importDataOD_BioTeK(fileDataNames, params=params)


def compileData0(M, OD, B):
    DATA = []
    keys = unique2d(M)
    for k in keys:
        reps, ODs, Bs, pos = [], [], [], []
        for rep, ij in enumerate(m_array_index(M, k)):
            thisOD = float(OD[ij[0]][ij[1]])
            thisB = B[ij[0]][ij[1]]
            reps.append(rep + 1)
            ODs.append(thisOD)
            Bs.append(thisB)
            pos.append(ij)
        DATA.append({'KEY': k, 'reps': reps, 'B': Bs, 'ODs': ODs, 'pos': pos})
    return DATA


def compileData(M, OD, B):
    """Backward-compatible endpoint compiler."""
    return compileData0(M, OD, B)


# -----------------------------------------------------------------------------
# Tidy export helper
# -----------------------------------------------------------------------------


def data_to_tidy(DATA, include_temp: bool = True):
    """
    Convert historical DATA structure to a tidy pandas DataFrame.

    Columns: KEY, B, rep, row, col, well, time_min, time_h, OD, temp.
    """
    if pd is None:
        raise ImportError("pandas is required for data_to_tidy()")

    records = []
    for thisDATA in DATA:
        key = thisDATA.get('KEY')
        for j, pos in enumerate(thisDATA.get('pos', [])):
            row, col = pos
            well = getLabelFromPos([row, col])
            B = thisDATA.get('B', [None] * len(thisDATA.get('pos', [])))[j]
            rep = thisDATA.get('reps', [j + 1] * len(thisDATA.get('pos', [])))[j]
            od_values = np.asarray(thisDATA.get('ODs', [])[j], dtype=float)
            time_values = np.asarray(_get_time_for_rep(thisDATA, j), dtype=float)
            temp_values = _get_temp_for_rep(thisDATA, j)

            if time_values.size == 0:
                time_values = np.arange(len(od_values), dtype=float)
            if len(time_values) != len(od_values):
                raise ValueError(f"Time and OD lengths differ for well {well}")

            if include_temp:
                temp_array = np.asarray(temp_values)
                if temp_array.size == 0:
                    temp_array = np.array([np.nan] * len(od_values))
                elif temp_array.size == 1:
                    temp_array = np.repeat(temp_array, len(od_values))
                elif temp_array.size != len(od_values):
                    temp_array = np.array([np.nan] * len(od_values))
            else:
                temp_array = np.array([np.nan] * len(od_values))

            for t, od, tmp in zip(time_values, od_values, temp_array):
                records.append({
                    'KEY': key,
                    'B': B,
                    'rep': rep,
                    'row': row,
                    'col': col,
                    'well': well,
                    'time_min': float(t),
                    'time_h': float(t) / 60,
                    'OD': float(od),
                    'temp': tmp,
                })

    return pd.DataFrame.from_records(records)


# -----------------------------------------------------------------------------
# Multi-channel endpoint readers, kept mostly compatible
# -----------------------------------------------------------------------------


def importDataMulti(fileDataNames, numChannels, params: Optional[Dict[str, Any]] = None):
    if params is None:
        params = {'rows': 16, 'cols': 24}
    rows, cols = get_plate_shape(params)
    numPlates = len(_as_file_list(fileDataNames))

    chLABEL = ['x'] * numChannels
    txtDATA = [[['x' for _ in range(cols)] for _ in range(rows * numPlates)] for _ in range(numChannels)]

    p = 0
    for thisDataFile in _as_file_list(fileDataNames):
        p += 1
        r = 0
        ch = 0
        rowDATA = np.zeros([numChannels, cols])
        reading = False
        last = False

        with open(thisDataFile, 'r', errors='ignore') as fileData:
            for line in fileData:
                if line.startswith('A\t') or reading:
                    reading = True
                    line_cols = line.split()
                    c = 0
                    for token in line_cols:
                        try:
                            value = float(token)
                            if c < cols:
                                rowDATA[ch][c] = value
                                c += 1
                        except ValueError:
                            if c > 0 and ch < numChannels:
                                chLABEL[ch] = token.split(':')[0]

                    txtDATA[ch][rows * (p - 1) + r] = [str(i) for i in rowDATA[ch]]
                    ch += 1
                    if ch == numChannels:
                        ch = 0
                        rowDATA = np.zeros([numChannels, cols])
                        r += 1
                        if last:
                            break
                if line.startswith(f'{_row_labels(rows)[-1]}\t'):
                    last = True

    return {'DATA': txtDATA, 'CHANNELS': chLABEL}


def importDataMulti96(fileDataNames, numChannels):
    return importDataMulti(fileDataNames, numChannels, params={'rows': 8, 'cols': 12})


def compileDataMulti(M, dataOD, dataGFP, dataRFP, dataYFP, dataCFP, B):
    DATA = []
    maxOD = maxGFP = maxRFP = maxYFP = maxCFP = 0
    minOD = minGFP = minRFP = minYFP = minCFP = float('Inf')

    keys = unique2d(M)
    for k in keys:
        reps, ODs, GFPs, RFPs, YFPs, CFPs, Bs, pos = [], [], [], [], [], [], [], []
        for rep, ij in enumerate(m_array_index(M, k)):
            if len(dataOD) > 0:
                thisOD = float(dataOD[ij[0]][ij[1]])
                ODs.append(thisOD)
                maxOD, minOD = max(maxOD, thisOD), min(minOD, thisOD)
            if len(dataGFP) > 0:
                thisGFP = float(dataGFP[ij[0]][ij[1]])
                GFPs.append(thisGFP)
                maxGFP, minGFP = max(maxGFP, thisGFP), min(minGFP, thisGFP)
            if len(dataRFP) > 0:
                thisRFP = float(dataRFP[ij[0]][ij[1]])
                RFPs.append(thisRFP)
                maxRFP, minRFP = max(maxRFP, thisRFP), min(minRFP, thisRFP)
            if len(dataYFP) > 0:
                thisYFP = float(dataYFP[ij[0]][ij[1]])
                YFPs.append(thisYFP)
                maxYFP, minYFP = max(maxYFP, thisYFP), min(minYFP, thisYFP)
            if len(dataCFP) > 0:
                thisCFP = float(dataCFP[ij[0]][ij[1]])
                CFPs.append(thisCFP)
                maxCFP, minCFP = max(maxCFP, thisCFP), min(minCFP, thisCFP)

            reps.append(rep + 1)
            Bs.append(B[ij[0]][ij[1]])
            pos.append(ij)

        DATA.append({'KEY': k, 'reps': reps, 'B': Bs, 'ODs': ODs,
                     'GFPs': GFPs, 'RFPs': RFPs, 'YFPs': YFPs,
                     'CFPs': CFPs, 'pos': pos})

    return DATA, [minOD, minGFP, minRFP, minYFP, minCFP], [maxOD, maxGFP, maxRFP, maxYFP, maxCFP]


# -----------------------------------------------------------------------------
# High-level loaders
# -----------------------------------------------------------------------------


def loadData384(params):
    M = importPlateLayout(params['fileLayoutName'], params)
    if params.get('verbose', False):
        print('\n\n**** LAYOUT:\n')
        show(M)

    B = importInoculationLayout(params)
    if params.get('verbose', False):
        print('\n\n**** Inoculation:\n')
        show(B)

    fileDataNames = params['fileDataNames']
    OD = importDataOD(fileDataNames, params=params)
    if params.get('verbose', False):
        print('\n\n**** OD600:\n')
        show(OD)

    return compileData(M, OD, B)


def loadData(params):
    """Load multi-channel endpoint data using the historical return format."""
    M = importPlateLayout(params['fileLayoutName'], params)
    if params.get('verbose', False):
        print('\n\n**** LAYOUT:\n')
        show(M)

    B = importInoculationLayout(params)
    if params.get('verbose', False):
        print('\n\n**** Inoculation:\n')
        show(B)

    fileDataNames = params['fileDataNames']
    print('Loading ', fileDataNames)

    numChannels = int(params.get('numChannels', 4))
    MULTI = importDataMulti(fileDataNames, numChannels, params=params)
    channel_labels = MULTI['CHANNELS']
    rawDATA = MULTI['DATA']

    dataOD, dataGFP, dataRFP, dataYFP, dataCFP = [], [], [], [], []
    for ich in range(numChannels):
        if params.get('verbose', False):
            print('\n\n**** %s:\n' % (channel_labels[ich]))

        label = channel_labels[ich]
        if 'mCerulean' in label or 'CFP' in label:
            dataCFP = rawDATA[ich]
        elif 'GFP' in label:
            dataGFP = rawDATA[ich]
        elif 'RFP' in label:
            dataRFP = rawDATA[ich]
        elif 'YFP' in label:
            dataYFP = rawDATA[ich]
        elif 'OD' in label:
            dataOD = rawDATA[ich]
        else:
            print('Channel not found: ', label)

    DATA, minVals, maxVals = compileDataMulti(M, dataOD, dataGFP, dataRFP, dataYFP, dataCFP, B)
    return DATA, maxVals, minVals
