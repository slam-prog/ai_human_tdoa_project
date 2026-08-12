"""
قراءة نتائج اختبار التحمل من CSV
وإعادة إنشاء الرسومات البيانية.

تشغيل الملف:

    python -m src.plot_results
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


RESULTS_DIRECTORY = Path("results")

CSV_PATH = (
    RESULTS_DIRECTORY
    / "robustness_sweep.csv"
)


def load_results(
    csv_path: Path,
) -> list[dict[str, float]]:
    """قراءة ملف CSV وتحويل القيم إلى أرقام."""

    if not csv_path.exists():
        raise FileNotFoundError(
            f"لم يتم العثور على الملف: {csv_path}"
        )

    rows: list[dict[str, float]] = []

    with csv_path.open(
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for raw_row in reader:
            row = {
                key: float(value)
                for key, value in raw_row.items()
                if key is not None
                and value is not None
            }

            rows.append(row)

    if not rows:
        raise ValueError(
            "ملف CSV فارغ ولا يحتوي على نتائج"
        )

    return rows


def get_axis_values(
    rows: list[dict[str, float]],
) -> tuple[np.ndarray, np.ndarray]:
    """استخراج قيم الكسب والضوضاء."""

    gains = sorted(
        {
            row["channel_2_gain"]
            for row in rows
        }
    )

    noises = sorted(
        {
            row["noise_std"]
            for row in rows
        }
    )

    return (
        np.asarray(gains, dtype=np.float64),
        np.asarray(noises, dtype=np.float64),
    )


def create_grid(
    rows: list[dict[str, float]],
    gains: np.ndarray,
    noises: np.ndarray,
    column_name: str,
) -> np.ndarray:
    """تحويل نتائج CSV إلى مصفوفة للرسم."""

    grid = np.full(
        shape=(len(noises), len(gains)),
        fill_value=np.nan,
        dtype=np.float64,
    )

    gain_indices = {
        value: index
        for index, value in enumerate(gains)
    }

    noise_indices = {
        value: index
        for index, value in enumerate(noises)
    }

    for row in rows:
        gain = row["channel_2_gain"]
        noise = row["noise_std"]

        gain_index = gain_indices[gain]
        noise_index = noise_indices[noise]

        grid[
            noise_index,
            gain_index,
        ] = row[column_name]

    return grid


def save_heatmap(
    values: np.ndarray,
    gains: np.ndarray,
    noises: np.ndarray,
    title: str,
    colorbar_label: str,
    output_path: Path,
    cmap: str,
) -> None:
    """حفظ خريطة حرارية."""

    figure, axis = plt.subplots(
        figsize=(10, 7)
    )

    mesh = axis.pcolormesh(
        gains,
        noises,
        values,
        shading="auto",
        cmap=cmap,
    )

    colorbar = figure.colorbar(
        mesh,
        ax=axis,
    )

    colorbar.set_label(
        colorbar_label
    )

    axis.set_title(title)
    axis.set_xlabel(
        "Channel 2 Gain"
    )
    axis.set_ylabel(
        "Noise Standard Deviation"
    )

    axis.set_xticks(gains)
    axis.set_yticks(noises)

    axis.grid(
        visible=True,
        alpha=0.25,
    )

    figure.tight_layout()

    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)


def save_error_curves(
    values: np.ndarray,
    gains: np.ndarray,
    noises: np.ndarray,
    title: str,
    y_label: str,
    output_path: Path,
) -> None:
    """حفظ منحنيات الخطأ مقابل الكسب."""

    figure, axis = plt.subplots(
        figsize=(10, 7)
    )

    for noise_index, noise in enumerate(
        noises
    ):
        axis.plot(
            gains,
            values[noise_index],
            marker="o",
            linewidth=2,
            label=f"noise={noise:g}",
        )

    axis.axhline(
        y=1.0,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label="1 mm limit",
    )

    axis.set_title(title)
    axis.set_xlabel(
        "Channel 2 Gain"
    )
    axis.set_ylabel(y_label)

    axis.grid(
        visible=True,
        alpha=0.3,
    )

    axis.legend()

    figure.tight_layout()

    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figure)


def print_best_and_worst(
    rows: list[dict[str, float]],
) -> None:
    """طباعة أفضل وأسوأ حالة."""

    best_row = min(
        rows,
        key=lambda row: row[
            "mean_distance_error_mm"
        ],
    )

    worst_row = max(
        rows,
        key=lambda row: row[
            "mean_distance_error_mm"
        ],
    )

    print("\n" + "=" * 72)
    print("Best and Worst Cases")
    print("=" * 72)

    print("أفضل حالة:")
    print(
        f"  gain={best_row['channel_2_gain']:.3f}, "
        f"noise={best_row['noise_std']:.3f}"
    )
    print(
        "  متوسط الخطأ: "
        f"{best_row['mean_distance_error_mm']:.6f} mm"
    )
    print(
        "  نسبة الفشل: "
        f"{best_row['failure_rate_above_1mm_percent']:.2f}%"
    )

    print("\nأسوأ حالة:")
    print(
        f"  gain={worst_row['channel_2_gain']:.3f}, "
        f"noise={worst_row['noise_std']:.3f}"
    )
    print(
        "  متوسط الخطأ: "
        f"{worst_row['mean_distance_error_mm']:.6f} mm"
    )
    print(
        "  نسبة الفشل: "
        f"{worst_row['failure_rate_above_1mm_percent']:.2f}%"
    )


def main() -> None:
    """تنفيذ قراءة النتائج وإعادة الرسم."""

    rows = load_results(CSV_PATH)

    gains, noises = get_axis_values(rows)

    mean_error_grid = create_grid(
        rows=rows,
        gains=gains,
        noises=noises,
        column_name=(
            "mean_distance_error_mm"
        ),
    )

    failure_rate_grid = create_grid(
        rows=rows,
        gains=gains,
        noises=noises,
        column_name=(
            "failure_rate_above_1mm_percent"
        ),
    )

    percentile_95_grid = create_grid(
        rows=rows,
        gains=gains,
        noises=noises,
        column_name=(
            "percentile_95_distance_error_mm"
        ),
    )

    RESULTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_heatmap(
        values=mean_error_grid,
        gains=gains,
        noises=noises,
        title="Mean Distance Error",
        colorbar_label="Mean Error (mm)",
        output_path=(
            RESULTS_DIRECTORY
            / "mean_error_heatmap_rebuilt.png"
        ),
        cmap="viridis",
    )

    save_heatmap(
        values=failure_rate_grid,
        gains=gains,
        noises=noises,
        title="Failure Rate Above 1 mm",
        colorbar_label="Failure Rate (%)",
        output_path=(
            RESULTS_DIRECTORY
            / "failure_rate_heatmap_rebuilt.png"
        ),
        cmap="magma",
    )

    save_heatmap(
        values=percentile_95_grid,
        gains=gains,
        noises=noises,
        title="95th Percentile Distance Error",
        colorbar_label="95th Percentile Error (mm)",
        output_path=(
            RESULTS_DIRECTORY
            / "percentile_95_heatmap.png"
        ),
        cmap="plasma",
    )

    save_error_curves(
        values=mean_error_grid,
        gains=gains,
        noises=noises,
        title=(
            "Mean Distance Error "
            "vs Channel 2 Gain"
        ),
        y_label="Mean Distance Error (mm)",
        output_path=(
            RESULTS_DIRECTORY
            / "mean_error_curves_rebuilt.png"
        ),
    )

    print_best_and_worst(rows)

    print("\n" + "=" * 72)
    print("تم إنشاء الرسومات بنجاح")
    print("=" * 72)

    print(
        "عدد الصفوف المقروءة: "
        f"{len(rows)}"
    )

    print(
        "مجلد النتائج: "
        f"{RESULTS_DIRECTORY.resolve()}"
    )


if __name__ == "__main__":
    main()