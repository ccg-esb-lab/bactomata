"""
Bactomata plotting helpers.

These functions operate on a parsed Bactomata experiment object and helper
outputs from bactomata.processing.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

from .processing import (
    get_endpoint_values_per_well,
    get_growth_data,
    get_well_data,
    get_wells_for_condition,
    infer_plate_dimensions,
    list_conditions,
    summarize_growth_data,
)


def plot_replicate_curves(
    growth,
    signal: str = "OD630",
    ax=None,
    title: str | None = None,
    xlabel: str = "Time (h)",
    ylabel: str | None = None,
    alpha: float = 0.8,
    linewidth: float = 1.5,
    show_legend: bool = True,
):
    """
    Plot individual replicate curves from a growth dataframe.
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    if ylabel is None:
        ylabel = signal

    for well, df_well in growth.groupby("well"):
        df_well = df_well.sort_values("time")
        ax.plot(
            df_well["time"],
            df_well[signal],
            label=well,
            alpha=alpha,
            linewidth=linewidth,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)

    if show_legend:
        ax.legend(title="Well", bbox_to_anchor=(1.02, 1), loc="upper left")

    return ax


def plot_summary_curve(
    summary,
    signal: str = "OD630",
    ax=None,
    title: str | None = None,
    xlabel: str = "Time (h)",
    ylabel: str | None = None,
    mean_col: str = "mean",
    std_col: str = "std",
    linewidth: float = 2,
    alpha: float = 0.25,
    label: str | None = None,
    show_std: bool = True,
):
    """
    Plot mean curve with optional standard deviation shading.
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    if ylabel is None:
        ylabel = signal

    summary = summary.sort_values("time")

    x = summary["time"]
    y = summary[mean_col]

    ax.plot(
        x,
        y,
        linewidth=linewidth,
        label=label,
    )

    if show_std and std_col in summary.columns:
        yerr = summary[std_col].fillna(0)
        ax.fill_between(
            x,
            y - yerr,
            y + yerr,
            alpha=alpha,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)

    if label is not None:
        ax.legend()

    return ax


def plot_growth_condition(
    experiment: dict,
    media_key: str,
    bacteria_key: str,
    signal: str = "OD630",
    title: str | None = None,
    show_replicates: bool = True,
    show_mean: bool = True,
    show_std: bool = True,
    ax=None,
):
    """
    Plot replicate curves and/or mean ± std for one media + bacteria condition.
    """

    growth = get_growth_data(
        experiment=experiment,
        media_key=media_key,
        bacteria_key=bacteria_key,
        signal=signal,
    )

    summary = summarize_growth_data(
        experiment=experiment,
        media_key=media_key,
        bacteria_key=bacteria_key,
        signal=signal,
    )

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    if title is None:
        title = f"{media_key} + {bacteria_key}"

    if show_replicates:
        plot_replicate_curves(
            growth,
            signal=signal,
            ax=ax,
            title=None,
            alpha=0.35,
            linewidth=1,
            show_legend=False,
        )

    if show_mean:
        plot_summary_curve(
            summary,
            signal=signal,
            ax=ax,
            title=None,
            linewidth=2.5,
            label="mean",
            show_std=show_std,
        )

    ax.set_title(title)

    return ax


def plot_bacteria_comparison(
    experiment: dict,
    media_key: str,
    bacteria_keys: Sequence[str],
    signal: str = "OD630",
    title: str | None = None,
    show_std: bool = True,
    ax=None,
):
    """
    Plot mean ± std curves for several bacteria keys in the same medium.
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    for bacteria_key in bacteria_keys:
        summary = summarize_growth_data(
            experiment=experiment,
            media_key=media_key,
            bacteria_key=bacteria_key,
            signal=signal,
        )

        plot_summary_curve(
            summary,
            signal=signal,
            ax=ax,
            label=bacteria_key,
            show_std=show_std,
        )

    if title is None:
        title = f"{media_key}: bacteria comparison"

    ax.set_title(title)
    ax.legend(title="Bacteria")

    return ax


def plot_media_comparison(
    experiment: dict,
    media_keys: Sequence[str],
    bacteria_key: str,
    signal: str = "OD630",
    title: str | None = None,
    show_std: bool = True,
    ax=None,
):
    """
    Plot mean ± std curves for the same bacteria key in several media.
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    for media_key in media_keys:
        summary = summarize_growth_data(
            experiment=experiment,
            media_key=media_key,
            bacteria_key=bacteria_key,
            signal=signal,
        )

        plot_summary_curve(
            summary,
            signal=signal,
            ax=ax,
            label=media_key,
            show_std=show_std,
        )

    if title is None:
        title = f"{bacteria_key}: media comparison"

    ax.set_title(title)
    ax.legend(title="Media")

    return ax


def make_condition_color_map(
    experiment: dict,
    exclude_empty: bool = False,
    cmap_name: str = "tab20",
) -> dict[tuple[str, str], object]:
    """
    Create a dictionary mapping (media_key, bacteria_key) to a color.
    """

    well_annotations = experiment["well_annotations"].copy()

    conditions = (
        well_annotations[["media_key", "bacteria_key", "is_empty"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if exclude_empty:
        conditions = conditions[~conditions["is_empty"]].copy()

    condition_tuples = [
        (row["media_key"], row["bacteria_key"])
        for _, row in conditions.iterrows()
    ]

    n = len(condition_tuples)

    if n == 0:
        return {}

    if n <= 20:
        cmap = plt.get_cmap(cmap_name)
        colors = [cmap(i) for i in range(n)]
    else:
        cmap = plt.get_cmap("hsv")
        colors = [cmap(i / n) for i in range(n)]

    condition_color_map = {
        cond: color for cond, color in zip(condition_tuples, colors)
    }

    return condition_color_map


def blend_with_white(color, intensity: float):
    """
    Blend a color with white.

    intensity should be between 0 and 1.
    0 = white, 1 = full color.
    """

    intensity = max(0, min(1, intensity))
    r, g, b = to_rgb(color)

    blended = (
        1 - intensity * (1 - r),
        1 - intensity * (1 - g),
        1 - intensity * (1 - b),
    )

    return blended


def plot_plate_overview(
    experiment: dict,
    signal: str = "OD630",
    mode: str = "auto",
    endpoint_time: str = "last",
    value_col: str = "value",
    condition_color_map: dict | None = None,
    empty_facecolor: str = "whitesmoke",
    linewidth: float = 1.0,
    show_well_labels: bool = True,
    show_values: bool = False,
    show_condition_legend: bool = True,
    cell_size: float = 1.4,
    title: str | None = None,
):
    """
    Plot a full plate overview.

    Modes:
    - "time_series": each well is a small filled growth curve.
    - "endpoint": each well is a box with color intensity based on value.
    - "auto": choose time_series if there are multiple time points, otherwise endpoint.
    """

    data = experiment["data"].copy()
    well_annotations = experiment["well_annotations"].copy()

    data = data[data["signal"] == signal].copy()

    if data.empty:
        raise ValueError(f"No data found for signal={signal}")

    n_timepoints = data["time_hhmmss"].nunique()

    if mode == "auto":
        if n_timepoints > 1:
            mode = "time_series"
        else:
            mode = "endpoint"

    if mode not in {"time_series", "endpoint"}:
        raise ValueError("mode must be 'auto', 'time_series', or 'endpoint'")

    row_labels, n_rows, n_cols = infer_plate_dimensions(experiment)

    if condition_color_map is None:
        condition_color_map = make_condition_color_map(experiment)

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(cell_size * n_cols, cell_size * n_rows),
        squeeze=False,
    )

    # Global ranges for consistent scaling.
    if mode == "time_series":
        x_min = data["time"].min()
        x_max = data["time"].max()
        y_min = min(0, data[value_col].min())
        y_max = data[value_col].max()
        if y_max == y_min:
            y_max = y_min + 1

    elif mode == "endpoint":
        endpoint_df = get_endpoint_values_per_well(
            experiment,
            signal=signal,
            endpoint_time=endpoint_time,
            value_col=value_col,
        )

        vmin = endpoint_df["endpoint_value"].min()
        vmax = endpoint_df["endpoint_value"].max()
        if vmax == vmin:
            vmax = vmin + 1

    # Build quick lookup tables.
    well_ann = well_annotations.set_index("well")
    grouped = {well: df for well, df in data.groupby("well")}

    if mode == "endpoint":
        endpoint_lookup = endpoint_df.set_index("well")["endpoint_value"].to_dict()

    # Plot each well.
    for i, row_label in enumerate(row_labels):
        for j in range(n_cols):
            col_num = j + 1
            well = f"{row_label}{col_num}"
            ax = axes[i, j]

            ax.set_xticks([])
            ax.set_yticks([])

            if well not in well_ann.index:
                ax.set_facecolor(empty_facecolor)
                continue

            ann = well_ann.loc[well]
            media_key = ann["media_key"]
            bacteria_key = ann["bacteria_key"]
            is_empty = bool(ann["is_empty"])

            base_color = condition_color_map.get(
                (media_key, bacteria_key),
                "lightgray",
            )

            if is_empty:
                ax.set_facecolor(empty_facecolor)

            if mode == "time_series":
                if well in grouped:
                    df_well = grouped[well].sort_values("time")

                    x = df_well["time"].values
                    y = df_well[value_col].values

                    ax.fill_between(
                        x,
                        y,
                        0,
                        color=base_color,
                        alpha=0.8,
                    )
                    ax.plot(
                        x,
                        y,
                        color=base_color,
                        linewidth=linewidth,
                    )

                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max * 1.05)

            elif mode == "endpoint":
                value = endpoint_lookup.get(well, np.nan)

                if np.isnan(value):
                    ax.set_facecolor(empty_facecolor)
                else:
                    intensity = (value - vmin) / (vmax - vmin)
                    fill_color = blend_with_white(base_color, intensity)
                    ax.set_facecolor(fill_color)

                    if show_values:
                        ax.text(
                            0.5,
                            0.5,
                            f"{value:.2f}",
                            ha="center",
                            va="center",
                            fontsize=7,
                            transform=ax.transAxes,
                        )

            # Well label.
            if show_well_labels:
                ax.text(
                    0.03,
                    0.95,
                    well,
                    ha="left",
                    va="top",
                    fontsize=6,
                    transform=ax.transAxes,
                )

            # Column labels on top row.
            if i == 0:
                ax.set_title(str(col_num), fontsize=9, pad=4)

            # Row labels on leftmost column.
            if j == 0:
                ax.set_ylabel(
                    row_label,
                    rotation=0,
                    fontsize=9,
                    labelpad=10,
                    va="center",
                )

    # Figure title.
    if title is None:
        if mode == "time_series":
            title = f"Plate overview: {signal} time series"
        else:
            title = f"Plate overview: {signal} endpoint ({endpoint_time})"

    fig.suptitle(title, y=1.02)

    # Optional legend.
    if show_condition_legend:
        unique_conditions = (
            well_annotations[["media_key", "bacteria_key"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        legend_handles = []
        for _, row in unique_conditions.iterrows():
            cond = (row["media_key"], row["bacteria_key"])
            color = condition_color_map.get(cond, "lightgray")
            label = f"{row['media_key']} | {row['bacteria_key']}"
            legend_handles.append(
                Patch(facecolor=color, edgecolor="black", label=label)
            )

        fig.legend(
            handles=legend_handles,
            loc="center left",
            bbox_to_anchor=(1.01, 0.5),
            frameon=False,
            title="Media | Bacteria",
            fontsize=8,
            title_fontsize=9,
        )

    plt.tight_layout()

    return fig, axes


def plot_well_data(
    experiment: dict,
    well: str,
    signal: str = "OD630",
    value_col: str = "value",
    fill_area: bool = True,
    ax=None,
    title: str | None = None,
    xlabel: str = "Time (h)",
    ylabel: str | None = None,
    linewidth: float = 2,
    alpha_fill: float = 0.3,
    show_metadata: bool = True,
):
    """
    Plot data from a single well for inspection.
    """

    df = get_well_data(
        experiment=experiment,
        well=well,
        signal=signal,
        value_col=value_col,
    )

    well_annotations = experiment["well_annotations"].copy()
    ann = well_annotations[well_annotations["well"] == well]

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))

    if ylabel is None:
        ylabel = signal

    n_timepoints = df["time_hhmmss"].nunique()

    # Kinetic data.
    if n_timepoints > 1:
        x = df["time"]
        y = df[value_col]

        ax.plot(x, y, linewidth=linewidth)

        if fill_area:
            ax.fill_between(x, y, 0, alpha=alpha_fill)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    # Endpoint data.
    else:
        y = df[value_col].iloc[0]
        ax.scatter([0], [y], s=60)
        ax.set_xlim(-0.5, 0.5)
        ax.set_xticks([0])
        ax.set_xticklabels(["endpoint"])
        ax.set_ylabel(ylabel)

    # Title.
    if title is None:
        if len(ann) == 1:
            media_key = ann["media_key"].iloc[0]
            bacteria_key = ann["bacteria_key"].iloc[0]
            title = f"{well} | {media_key} | {bacteria_key}"
        else:
            title = f"{well} | {signal}"

    ax.set_title(title)

    # Optional text box with metadata.
    if show_metadata and len(ann) == 1:
        media_key = ann["media_key"].iloc[0]
        bacteria_key = ann["bacteria_key"].iloc[0]

        text = (
            f"well: {well}\n"
            f"media: {media_key}\n"
            f"bacteria: {bacteria_key}\n"
            f"signal: {signal}"
        )
        ax.text(
            1.02,
            0.98,
            text,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    return ax


def plot_wells(
    experiment: dict,
    wells: Sequence[str],
    signal: str = "OD630",
    value_col: str = "value",
    fill_area: bool = False,
    ax=None,
    title: str | None = None,
    xlabel: str = "Time (h)",
    ylabel: str | None = None,
    linewidth: float = 2,
    alpha: float = 0.8,
    show_legend: bool = True,
    show_metadata_in_label: bool = True,
):
    """
    Plot several selected wells together.
    """

    data = experiment["data"].copy()
    well_annotations = experiment["well_annotations"].copy()

    if ylabel is None:
        ylabel = signal

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    ann_lookup = well_annotations.set_index("well")

    for well in wells:
        df_well = data[
            (data["well"] == well)
            & (data["signal"] == signal)
        ].copy()

        if df_well.empty:
            print(f"Warning: no data found for well={well}, signal={signal}")
            continue

        df_well = df_well.sort_values("time")

        if show_metadata_in_label and well in ann_lookup.index:
            media_key = ann_lookup.loc[well, "media_key"]
            bacteria_key = ann_lookup.loc[well, "bacteria_key"]
            label = f"{well} | {media_key} | {bacteria_key}"
        else:
            label = well

        n_timepoints = df_well["time_hhmmss"].nunique()

        if n_timepoints > 1:
            x = df_well["time"]
            y = df_well[value_col]

            ax.plot(
                x,
                y,
                linewidth=linewidth,
                alpha=alpha,
                label=label,
            )

            if fill_area:
                ax.fill_between(
                    x,
                    y,
                    0,
                    alpha=0.15,
                )

        else:
            y = df_well[value_col].iloc[0]
            ax.scatter(
                [well],
                [y],
                s=60,
                label=label,
            )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is None:
        title = f"Selected wells | {signal}"

    ax.set_title(title)

    if show_legend:
        ax.legend(
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            fontsize=8,
        )

    return ax


def compare_two_wells(
    experiment: dict,
    well1: str,
    well2: str,
    signal: str = "OD630",
    fill_area: bool = False,
):
    """
    Compare two wells in the same plot.
    """

    ax = plot_wells(
        experiment=experiment,
        wells=[well1, well2],
        signal=signal,
        fill_area=fill_area,
        title=f"Compare wells: {well1} vs {well2}",
    )

    return ax


def plot_condition_wells(
    experiment: dict,
    media_key: str,
    bacteria_key: str,
    signal: str = "OD630",
    fill_area: bool = False,
    ax=None,
):
    """
    Plot all replicate wells for one media + bacteria condition.
    """

    wells = get_wells_for_condition(
        experiment,
        media_key=media_key,
        bacteria_key=bacteria_key,
    )

    if len(wells) == 0:
        raise ValueError(
            f"No wells found for media_key={media_key}, bacteria_key={bacteria_key}"
        )

    ax = plot_wells(
        experiment=experiment,
        wells=wells,
        signal=signal,
        fill_area=fill_area,
        ax=ax,
        title=f"{media_key} + {bacteria_key} | replicate wells",
    )

    return ax


def compare_two_media(
    experiment: dict,
    media1: str,
    media2: str,
    bacteria_key: str,
    signal: str = "OD630",
    show_std: bool = True,
):
    """
    Compare one bacteria key across two media conditions.
    """

    ax = plot_media_comparison(
        experiment=experiment,
        media_keys=[media1, media2],
        bacteria_key=bacteria_key,
        signal=signal,
        show_std=show_std,
        title=f"{bacteria_key}: {media1} vs {media2}",
    )

    return ax


def plot_all_bacteria_in_media(
    experiment: dict,
    media_key: str,
    signal: str = "OD630",
    exclude_bacteria_keys: Sequence[str] = ("0",),
    show_std: bool = True,
    ax=None,
):
    """
    Plot mean ± std curves for all bacteria keys present in one medium.
    """

    conditions = list_conditions(experiment)

    bacteria_keys = (
        conditions.loc[conditions["media_key"] == media_key, "bacteria_key"]
        .dropna()
        .unique()
        .tolist()
    )

    bacteria_keys = [b for b in bacteria_keys if b not in exclude_bacteria_keys]

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 4))

    for bacteria_key in bacteria_keys:
        summary = summarize_growth_data(
            experiment=experiment,
            media_key=media_key,
            bacteria_key=bacteria_key,
            signal=signal,
        )

        plot_summary_curve(
            summary,
            signal=signal,
            ax=ax,
            label=bacteria_key,
            show_std=show_std,
        )

    ax.set_title(f"{media_key}: all bacteria")
    ax.set_xlabel("Time (h)")
    ax.set_ylabel(signal)
    ax.legend(title="Bacteria", bbox_to_anchor=(1.02, 1), loc="upper left")

    return ax
