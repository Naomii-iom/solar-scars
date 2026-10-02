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
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Ellipse

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

def circular_smooth(values, radius):
    """Smooth a circular list without creating a seam between December and January."""
    smoothed = []
    for index in range(len(values)):
        total = 0
        weight_total = 0
        for offset in range(-radius, radius + 1):
            weight = radius + 1 - abs(offset)
            total += values[(index + offset) % len(values)] * weight
            weight_total += weight
        smoothed.append(total / weight_total)
    return smoothed


def draw_seasonal_background(ax, values):
    """Add the reference poster's very pale 30-day seasonal heat layer."""
    minimum = min(values)
    maximum = max(values)
    normalized = [(value - minimum) / (maximum - minimum) for value in values]
    seasonal = circular_smooth(normalized, 30)

    for index in range(0, len(values), 3):
        heat = seasonal[index]
        angle = math.pi / 2 - 2 * math.pi * index / len(values)
        radius = 1.22 + 2.05 * heat ** 1.12
        centre = (math.cos(angle) * radius, math.sin(angle) * radius)
        haze = Ellipse(
            centre,
            width=1.08 + 0.62 * heat,
            height=1.48 + 0.82 * heat,
            angle=math.degrees(angle) + 90,
            facecolor="#F5A38F",
            edgecolor="none",
            alpha=0.016,
            zorder=1,
        )
        ax.add_patch(haze)


def draw_solar_scar(ax, values):
    """Build one annual scar from four to seven translucent layers per day."""
    minimum = min(values)
    maximum = max(values)
    normalized = [(value - minimum) / (maximum - minimum) for value in values]
    seasonal_trend = circular_smooth(normalized, 10)
    colours = LinearSegmentedColormap.from_list(
        "solar_burn",
        [
            (0.00, "#F8CDBB"),
            (0.25, "#F5A38F"),
            (0.45, "#ED776C"),
            (0.62, "#D94E56"),
            (0.80, "#8F2E48"),
            (1.00, "#651A38"),
        ],
    )

    stains = []
    for index, (daily_heat, trend_heat) in enumerate(
            zip(normalized, seasonal_trend)):
        angle = math.pi / 2 - 2 * math.pi * index / len(values)

        # The smoothed trend keeps the annual path continuous; the real daily
        # reading still controls every stain's size, opacity, colour and layers.
        position_heat = 0.86 * trend_heat + 0.14 * daily_heat
        radius = 1.22 + 2.05 * position_heat ** 1.12
        daily_radial_offset = 0.018 * math.sin(index * 1.71)
        daily_tangent_offset = 0.020 * math.sin(index * 2.37 + 0.8)

        layer_count = 4 + round(3 * daily_heat)
        tangent_size = 0.20 + 0.55 * daily_heat ** 1.15
        radial_size = 0.16 + 1.35 * daily_heat ** 1.20
        base_opacity = min(
            0.080,
            0.0015
            + 0.110 * daily_heat ** 2.60 * (0.45 + 0.55 * trend_heat),
        )

        for layer_index in range(layer_count):
            depth = layer_index / (layer_count - 1)
            phase = index * 1.37 + layer_index * 2.11

            # Outer layers create a pale haze; inner layers are smaller and
            # slightly deeper. All offsets remain tiny compared with the data.
            scale = 1.40 - 0.50 * depth
            width_variation = 1 + 0.17 * math.sin(phase + 0.4)
            height_variation = 1 + 0.17 * math.sin(phase * 1.19 + 1.2)
            layer_radial_offset = (
                daily_radial_offset
                + (0.035 + 0.055 * daily_heat) * math.sin(phase)
            )
            layer_tangent_offset = (
                daily_tangent_offset
                + (0.040 + 0.060 * daily_heat) * math.sin(phase * 0.91 + 0.7)
            )
            centre_x = (
                math.cos(angle) * (radius + layer_radial_offset)
                - math.sin(angle) * layer_tangent_offset
            )
            centre_y = (
                math.sin(angle) * (radius + layer_radial_offset)
                + math.cos(angle) * layer_tangent_offset
            )

            alpha_weight = 0.48 + 0.52 * depth
            opacity = base_opacity * alpha_weight
            colour_heat = min(
                1,
                daily_heat ** 1.20 * (0.72 + 0.28 * depth) + 0.010,
            )
            rotation_variation = (
                8 + 7 * daily_heat
            ) * math.sin(phase * 0.83 + 0.5)

            stain = Ellipse(
                (centre_x, centre_y),
                width=tangent_size * scale * width_variation,
                height=radial_size * scale * height_variation,
                angle=math.degrees(angle) + 90 + rotation_variation,
                facecolor=colours(colour_heat),
                edgecolor="none",
                alpha=opacity,
                antialiased=True,
                zorder=2,
            )
            stains.append((depth, stain))

    # Keep each day's pale halo and deeper centre together. Neighbouring days
    # still overlap heavily, but their layered watercolour structure remains
    # visible at close range, as in the visual reference.
    for _, stain in stains:
        ax.add_patch(stain)


def draw_reference_structure(ax, values):
    """Add quiet chart cues behind the artwork without competing with it."""
    guide_colour = "#9a7563"
    minimum = min(values)
    maximum = max(values)
    label_angle = math.radians(103)
    for uv_value in (3, 6, 9, 12):
        heat = max(0, min(1, (uv_value - minimum) / (maximum - minimum)))
        radius = 1.75 + 1.65 * heat ** 1.12
        circle = plt.Circle(
            (0, 0), radius, fill=False, color=guide_colour,
            linewidth=0.45, alpha=0.11, linestyle=(0, (2.5, 2.5)),
        )
        ax.add_patch(circle)
        ax.text(
            math.cos(label_angle) * radius + 0.035,
            math.sin(label_angle) * radius + 0.035,
            f"UV {uv_value}",
            fontsize=5.2,
            color=guide_colour,
            alpha=0.58,
            ha="left",
            va="bottom",
            rotation=math.degrees(label_angle) - 90,
            zorder=1,
        )

    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_offset = 0
    for month_length in month_lengths:
        angle = math.pi / 2 - 2 * math.pi * day_offset / len(values)
        ax.plot(
            [math.cos(angle) * 1.05, math.cos(angle) * 3.65],
            [math.sin(angle) * 1.05, math.sin(angle) * 3.65],
            color=guide_colour, linewidth=0.55, alpha=0.14, zorder=0,
        )
        day_offset += month_length


def draw_precise_data_layer(ax, values, dates):
    """Overlay the raw daily scar line and automatically label its extremes."""
    minimum = min(values)
    maximum = max(values)
    normalized = [(value - minimum) / (maximum - minimum) for value in values]
    points = []

    for index, heat in enumerate(normalized):
        angle = math.pi / 2 - 2 * math.pi * index / len(values)
        radius = 1.65 + 1.45 * heat ** 1.12
        points.append((math.cos(angle) * radius, math.sin(angle) * radius))

    x_values = [point[0] for point in points] + [points[0][0]]
    y_values = [point[1] for point in points] + [points[0][1]]
    ax.plot(
        x_values,
        y_values,
        color="#641733",
        linewidth=0.45,
        alpha=0.38,
        solid_capstyle="round",
        solid_joinstyle="round",
        zorder=4,
    )

    extrema = [
        ("MIN", min(range(len(values)), key=values.__getitem__), (30, 24)),
        ("MAX", max(range(len(values)), key=values.__getitem__), (-48, -12)),
    ]
    for label, index, text_offset in extrema:
        x_value, y_value = points[index]
        ax.scatter(
            [x_value], [y_value], s=18,
            facecolors="none" if label == "MAX" else "#4d1328",
            edgecolors="#4d1328", linewidths=0.65, alpha=0.88, zorder=5,
        )
        ax.annotate(
            f"{label}  {dates[index]}\nUV {values[index]:.1f}",
            xy=(x_value, y_value),
            xytext=text_offset,
            textcoords="offset points",
            fontsize=6.0,
            color="#5b2931",
            alpha=0.88,
            ha="left" if text_offset[0] > 0 else "right",
            va="bottom" if text_offset[1] > 0 else "top",
            arrowprops={
                "arrowstyle": "-",
                "color": "#6d4640",
                "linewidth": 0.55,
                "alpha": 0.72,
                "shrinkA": 2,
                "shrinkB": 2,
            },
            zorder=5,
        )


def add_uv_legend(fig, background):
    """Place the compact UV colour key in the shared right-hand column."""
    legend = fig.add_axes([0.825, 0.515, 0.150, 0.235], facecolor=background)
    legend.set_xlim(0, 1)
    legend.set_ylim(0, 1)
    legend.axis("off")
    legend.text(
        0.00, 0.98, "Daily Maximum\nUV Index",
        va="top", fontsize=7.1, color="#68443c", linespacing=1.15,
    )
    entries = [
        ("12+", "#7A173A"),
        ("9 – 12", "#AF2947"),
        ("6 – 9", "#D6535B"),
        ("3 – 6", "#ED806E"),
        ("1 – 3", "#F3A58E"),
        ("< 1", "#F7C9B6"),
    ]
    for position, (label, colour) in enumerate(entries):
        y_value = 0.75 - position * 0.125
        legend.scatter(
            [0.13], [y_value], s=330, color=colour,
            edgecolors="none", alpha=0.96,
        )
        legend.text(
            0.32, y_value, label, va="center",
            fontsize=6.6, color="#76564d",
        )


def add_method_legend(fig, background):
    """Explain the three visible layers in one quiet, aligned footer strip."""
    method = fig.add_axes([0.040, 0.052, 0.750, 0.070], facecolor=background)
    method.set_xlim(0, 1)
    method.set_ylim(0, 1)
    method.axis("off")

    for size, alpha in ((760, 0.025), (460, 0.040), (220, 0.055)):
        method.scatter([0.025], [0.56], s=size, color="#ED776C",
                       alpha=alpha, edgecolors="none")
    method.text(0.075, 0.73, "Background layer", fontsize=5.9,
                fontweight="bold", color="#68443c")
    method.text(0.075, 0.49, "30-day moving average\n(seasonal trend)",
                fontsize=5.4, color="#886a60", va="top", linespacing=1.25)

    for offset, colour, alpha in (
            ((-0.014, 0.00), "#F5A38F", 0.15),
            ((0.010, 0.018), "#ED776C", 0.15),
            ((0.022, -0.012), "#D94E56", 0.12)):
        method.scatter([0.357 + offset[0]], [0.56 + offset[1]], s=470,
                       color=colour, alpha=alpha, edgecolors="none")
    method.text(0.405, 0.73, "Daily solar stains", fontsize=5.9,
                fontweight="bold", color="#68443c")
    method.text(0.405, 0.49,
                "Each day = 4–7 translucent\nellipses (size, opacity and\ncolour from UV value)",
                fontsize=5.4, color="#886a60", va="top", linespacing=1.2)

    line_x = [0.680, 0.695, 0.710, 0.725, 0.740]
    line_y = [0.54, 0.61, 0.59, 0.50, 0.56]
    method.plot(line_x, line_y, color="#641733", linewidth=0.6, alpha=0.72)
    method.text(0.765, 0.73, "UV scar line", fontsize=5.9,
                fontweight="bold", color="#68443c")
    method.text(0.765, 0.49, "Daily maximum UV index\n(365 days)",
                fontsize=5.4, color="#886a60", va="top", linespacing=1.25)


def add_linear_view(fig, values, background):
    """Add the small linear view at the foot of the shared right column."""
    mini = fig.add_axes([0.825, 0.295, 0.150, 0.115], facecolor=background)
    days = list(range(len(values)))
    mini.fill_between(days, values, color="#D94E56", alpha=0.18, linewidth=0)
    mini.plot(days, values, color="#A52342", linewidth=0.42, alpha=0.82)
    mini.set_xlim(0, len(values) - 1)
    mini.set_ylim(0, 15)
    mini.set_title("Daily UV Index (Linear View)", loc="left",
                   fontsize=6.3, color="#68443c", pad=4)

    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month_starts = []
    running_total = 0
    for month_length in month_lengths:
        month_starts.append(running_total)
        running_total += month_length
    mini.set_xticks(month_starts)
    mini.set_xticklabels(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        fontsize=4.8, color="#84675f",
    )
    mini.set_yticks([0, 5, 10, 15])
    mini.tick_params(axis="y", labelsize=4.8, colors="#84675f", length=0)
    mini.tick_params(axis="x", length=0)
    mini.grid(color="#9a7563", alpha=0.12, linewidth=0.4)
    for spine in mini.spines.values():
        spine.set_color("#9a7563")
        spine.set_alpha(0.20)
        spine.set_linewidth(0.5)


def main():
    table = rows(DATA)
    print(f"{DATA.name}: {len(table)} rows. The first one: {table[0]}")

    days, dates, values = [], [], []
    for i, (year, month, day, value, time_recorded, quality) in enumerate(table):
        if year != "2025":
            continue

        if value == "***":
            continue

        days.append(len(days) + 1)
        dates.append(f"{year}-{int(month):02d}-{int(day):02d}")
        values.append(float(value))

    print(f"{len(values)} values, from {min(values)} to {max(values)}")

    background = "#f3ead7"
    ink = "#4b2b22"
    fig = plt.figure(figsize=(11, 11), facecolor=background)
    ax = fig.add_axes([0.000, 0.120, 0.810, 0.810], facecolor=background)
    ax.set_facecolor(background)
    draw_reference_structure(ax, values)
    draw_seasonal_background(ax, values)
    draw_solar_scar(ax, values)
    draw_precise_data_layer(ax, values, dates)

    months = [
        "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
        "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
    ]
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_offset = 0
    label_radius = 3.55
    for month, month_length in zip(months, month_lengths):
        middle_day = day_offset + month_length / 2
        angle = math.pi / 2 - 2 * math.pi * middle_day / len(values)
        rotation = math.degrees(angle) - 90
        if rotation < -90:
            rotation += 180
        if rotation > 90:
            rotation -= 180
        ax.text(
            math.cos(angle) * label_radius,
            math.sin(angle) * label_radius,
            month,
            ha="center",
            va="center",
            rotation=rotation,
            fontsize=8.2,
            fontweight="bold",
            color="#765146",
            alpha=0.84,
        )
        day_offset += month_length

    ax.set_xlim(-3.78, 3.78)
    ax.set_ylim(-3.78, 3.78)
    ax.set_aspect("equal")
    ax.axis("off")

    fig.text(0.040, 0.976, "SOLAR SCAR", ha="left", va="top",
             fontsize=34, fontweight="bold", color=ink)
    fig.text(0.040, 0.927,
             "365 DAYS OF ULTRAVIOLET EXPOSURE  ·  KING'S PARK, HONG KONG  ·  2025",
             ha="left", fontsize=10.5, color="#6d3029")
    fig.text(
        0.825, 0.855,
        "Each trace represents one day’s\n"
        "maximum UV index. Distance, size\n"
        "and colour intensity correspond to\n"
        "the UV value. Overlapping translucent\n"
        "layers show accumulated solar\n"
        "exposure throughout the year.",
        ha="left", va="top", fontsize=6.4, color="#805f55", linespacing=1.38,
    )

    add_uv_legend(fig, background)
    add_method_legend(fig, background)
    add_linear_view(fig, values, background)

    fig.text(
        0.040, 0.026,
        "ANGLE = DAY OF YEAR   ·   DISTANCE FROM CENTRE = DAILY MAXIMUM UV INDEX",
        ha="left", fontsize=5.8, color="#8b6a58",
    )
    fig.text(
        0.040, 0.011,
        "DATA SOURCE: HONG KONG OBSERVATORY (HKO)   ·   DAILY MAXIMUM UV INDEX (KP)   ·   2025",
        ha="left", fontsize=5.5, color="#9a7b6c",
    )

    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / PICTURE, dpi=114)
    print(f"saved out/{PICTURE}")
    plt.show()


if __name__ == "__main__":
    main()
