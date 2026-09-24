# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib"]
# ///

"""
Read the file in data/, make one picture, save it to out/.

    uv run plot.py

Three parts, and you will replace all three: rows() reads the file the way *your*
file needs reading, the loop in main() picks the numbers out of it, and the plot at
the bottom is the transformation you chose. Print before you plot.
"""

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

FILE = "daily_KP_MAXUV_ALL.csv" # CHANGE ME: the same name as in fetch.py
PICTURE = "plot.png"                           # what goes into out/, and into the README

HERE = Path(__file__).parent
DATA = HERE / "data" / FILE
OUT = HERE / "out"


def rows(path):
    """The file as a list of lists, one per line. The Observatory puts three lines
    of titles above the table and a legend below it, so keep only the lines that
    start with a year."""
    kept = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].isdigit():
                kept.append(line)
    return kept

def draw_scar(ax, x, y, uv, seed):
    """Draw one sunburn mark. Stronger UV makes a larger, darker scar."""
    intensity = min(uv / 13, 1)
    color = plt.get_cmap("YlOrRd")(0.25 + intensity * 0.7)
    radius = 0.08 + intensity * 0.14
    ray_count = 4 + int(uv)

    for ray in range(ray_count):
        angle = (2 * math.pi * ray / ray_count) + seed * 0.37
        ray_length = radius + 0.05 + intensity * 0.08
        x_end = x + math.cos(angle) * ray_length
        y_end = y + math.sin(angle) * ray_length
        ax.plot(
            [x, x_end],
            [y, y_end],
            color=color,
            linewidth=0.35 + intensity * 0.45,
            alpha=0.25 + intensity * 0.45,
        )

    scar = plt.Circle(
        (x, y),
        radius,
        facecolor=color,
        edgecolor=color,
        linewidth=0.5,
        alpha=0.35 + intensity * 0.45,
    )
    ax.add_patch(scar)


def main():
    table = rows(DATA)
    print(f"{DATA.name}: {len(table)} rows. The first one: {table[0]}")

    days, values = [], []
    for i, (year, month, day, value, time_recorded, quality) in enumerate(table):
        if year != "2025":
            continue

        if value == "***":
            continue

        days.append(len(days) + 1)
        values.append(float(value))

    print(f"{len(values)} values, from {min(values)} to {max(values)}")

    months = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
    ]
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    background = "#f3ead7"
    ink = "#4b2b22"
    fig, ax = plt.subplots(figsize=(16, 8), facecolor=background)
    ax.set_facecolor(background)

    value_index = 0
    for month_index, month_length in enumerate(month_lengths):
        y = 11 - month_index
        for day in range(1, month_length + 1):
            draw_scar(ax, day, y, values[value_index], value_index)
            value_index += 1

    for month_index, month_name in enumerate(months):
        y = 11 - month_index
        ax.text(-0.7, y, month_name, ha="right", va="center",
                fontsize=9, color=ink, fontweight="bold")

    for day in [1, 5, 10, 15, 20, 25, 31]:
        ax.text(day, 12.0, str(day), ha="center", va="center",
                fontsize=8, color="#8b6a58")

    ax.set_xlim(-2.3, 32)
    ax.set_ylim(-1.0, 12.6)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.suptitle("SOLAR SCARS", x=0.12, y=0.965, ha="left",
                 fontsize=28, fontweight="bold", color=ink)
    fig.text(0.12, 0.91,
             "365 DAYS OF ULTRAVIOLET EXPOSURE  ·  KING'S PARK, HONG KONG  ·  2025",
             ha="left", fontsize=10, color="#8b4a32")
    fig.text(0.12, 0.045,
             "ONE MARK = ONE DAY   ·   SIZE, DARKNESS AND RAYS INCREASE WITH UV INTENSITY",
             ha="left", fontsize=8, color="#8b6a58")
    fig.tight_layout(rect=(0.06, 0.07, 0.98, 0.9))

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=150)
    print(f"saved out/{PICTURE}")
    plt.show()


if __name__ == "__main__":
    main()
