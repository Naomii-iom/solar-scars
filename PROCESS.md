# Process

## Tools

I used the Hong Kong Observatory open-data portal to find and download the
King's Park daily maximum UV Index CSV. I used VS Code to edit and run the
Python files, Git and GitHub to save separate stages of the project, and
ChatGPT/Codex to explain errors, suggest code, and help develop the visual
transformation. I checked each generated image myself and asked for changes
when the output was still a normal chart or did not match the data-art idea.

The model initially worked from the assignment's temperature example, so I had
to make sure the real CSV columns were used: year, month, day, UV value, time
recorded, and data completeness. I also corrected the year filter to 2025 and
changed the day numbering so that it ran from 1 to 365 instead of continuing
the row numbers from the full historical file. Later, I noticed that `fetch.py`
still contained the template temperature URL, so it was replaced with the
official King's Park maximum UV CSV address.

## Kept

I kept the Solar Scars calendar concept because it turns an invisible hazard
into a visible physical trace. The twelve horizontal rows make the seasonal
pattern easy to compare, while each day remains separate. I also kept a simple
list-and-loop approach instead of adding pandas. The custom `draw_scar()`
function maps each UV value to the size, colour, darkness, and number of rays in
one mark. This satisfies the assignment's coding requirements and makes the
visual rule understandable from the code.

## Rejected

I rejected the first orange line chart. It proved that the 365 values had been
read correctly, but it looked like a standard scientific graph and did not
express the idea of accumulated sun damage. I also rejected the early test grid
of plain circles. Although circle size represented UV intensity, the result was
too clean and generic. Adding radial lines, warm colour variation, a paper-like
background, month labels, and irregular rotations made the final image feel
more like a collection of burns or scars while still being driven by the same
real measurements.
