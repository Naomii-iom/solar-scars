# Process

## Tools and assistance

I used the Hong Kong Observatory open-data source, VS Code, Python, Git, and
GitHub. I also used ChatGPT / AI assistance to understand the assignment,
debug the CSV parsing, iterate Python visualization ideas, and refine the final
visual hierarchy. I reviewed every generated image and decided which direction
to keep.

## Technical correction

The original assignment template plotted temperature and used the row number
from the whole historical file. I adapted it to the six-column Hong Kong
Observatory UV dataset: year, month, day, maximum UV value, recorded time, and
data completeness. I then filtered the rows to 2025 and corrected the day
indexing so the selected observations form a valid sequence from day 1 to day
365.

## Kept

I kept translucent overlapping shapes driven by UV intensity. This made the
invisible exposure feel cumulative while keeping every mark connected to a
real measurement. I also kept the thin raw-data line because it preserves the
daily rises and falls inside the softer seasonal image.

## Rejected

I rejected the first orange line chart because it was only a standard graph.
The early 12 × 31 “sun calendar” looked too much like an infographic or icon
set. A spiky scar version became decorative and made the data harder to read.
I also rejected an irregular donut/blob version because random deformation
obscured the annual UV pattern. In each case, the visual effect began to
overpower the real data. The final circular version uses controlled overlap and
a moving-average haze, while retaining the raw 365-day scar line.
