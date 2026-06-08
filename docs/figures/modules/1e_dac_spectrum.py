"""
1e_dac_spectrum.py - Figure 1E-3: DAC output spectrum + reconstruction filter

Shows what comes out of the AD9742 as a frequency-domain plot, before and
after the 5th-order Butterworth reconstruction filter. Demonstrates the
images at multiples of f_sample, the ZOH sinc envelope, and the role of the
reconstruction filter in attenuating those images.

Parameters baked in (worst-case 10 MHz output at 50 MSPS):
  f_signal = 10 MHz   (baseband tone)
  f_sample = 50 MSPS  (Pico-limited DAC update rate)
  f_cutoff = 12 MHz   (5th-order Butterworth lowpass)

Output: 1e_dac_spectrum.svg + 1e_dac_spectrum.png in the same directory.

Run:  python3 1e_dac_spectrum.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# PMVB FMCW dark-theme palette (matches pmvb-figures.sty)
PMVB_BG = "#1a1a2e"
PMVB_PANEL = "#16213e"
PMVB_FG = "#f0f0f0"
PMVB_MUTED = "#888"
PMVB_GRID = "#2d3a55"
PMVB_BLUE = "#60a5fa"
PMVB_AMBER = "#fbbf24"
PMVB_RED = "#f87171"
PMVB_GREEN = "#4ade80"

# Parameters
f_signal = 10e6
f_sample = 50e6
f_cutoff = 12e6
order = 5

# Frequency axis (Hz) from 0.1 MHz to 3 * f_sample
f = np.linspace(0.1e6, 3 * f_sample, 8000)
f_mhz = f / 1e6

# Sample-and-hold (ZOH) envelope = |sinc(f / f_sample)|
sinc_env = np.abs(np.sinc(f / f_sample))
sinc_db = 20 * np.log10(sinc_env + 1e-12)

# Butterworth filter response (in dB)
butter_db = -10 * np.log10(1 + (f / f_cutoff) ** (2 * order))

# Combined (after filter) spectrum envelope
combined_db = sinc_db + butter_db

# Image frequencies and their kinds
images = [
    (f_signal,             "baseband", PMVB_BLUE),
    (f_sample - f_signal,  "image 1",  PMVB_RED),
    (f_sample + f_signal,  "image 2",  PMVB_RED),
    (2 * f_sample - f_signal, "image 3", PMVB_RED),
    (2 * f_sample + f_signal, "image 4", PMVB_RED),
]

# Plot
fig, ax = plt.subplots(figsize=(12.5, 6.2), facecolor=PMVB_BG)
ax.set_facecolor(PMVB_PANEL)

# Sinc envelope (dashed grey)
ax.plot(f_mhz, sinc_db, "--", color=PMVB_MUTED, lw=1.2,
        label="ZOH sinc envelope (sample-and-hold)")

# Butterworth filter response (amber, solid)
ax.plot(f_mhz, butter_db, "-", color=PMVB_AMBER, lw=2.2,
        label=f"{order}th-order Butterworth recon filter @ {f_cutoff/1e6:.0f} MHz")

# Combined (after-filter) envelope (green, dotted)
ax.plot(f_mhz, combined_db, ":", color=PMVB_GREEN, lw=1.6,
        label="Filtered spectrum envelope (sinc + filter)")

# Plot the spectral lines (baseband + images)
for freq, kind, color in images:
    f_mhz_pt = freq / 1e6
    pre_db = 20 * np.log10(np.abs(np.sinc(freq / f_sample)) + 1e-12)
    butter_at_f = -10 * np.log10(1 + (freq / f_cutoff) ** (2 * order))
    post_db = pre_db + butter_at_f
    # Pre-filter line (top of sinc envelope)
    ax.plot([f_mhz_pt, f_mhz_pt], [-100, pre_db], color=color, lw=2.5, alpha=0.85)
    # Post-filter dot (where the line ends up after filter)
    ax.plot([f_mhz_pt], [post_db], "o", color=color, mec=PMVB_FG, mew=0.6, ms=6, alpha=0.9)
    # Label above the pre-filter peak
    label = f"{f_mhz_pt:.0f} MHz"
    ax.annotate(label, xy=(f_mhz_pt, pre_db),
                xytext=(0, 7), textcoords="offset points",
                ha="center", va="bottom", color=color, fontsize=8.5)

# Spec markers
ax.axvline(f_sample / 1e6, color=PMVB_MUTED, lw=0.7, alpha=0.5)
ax.text(f_sample / 1e6, 4, " $f_{sample}$", color=PMVB_MUTED, fontsize=9,
        va="top", ha="left", style="italic")
ax.axvline(2 * f_sample / 1e6, color=PMVB_MUTED, lw=0.7, alpha=0.5)
ax.text(2 * f_sample / 1e6, 4, " $2\\,f_{sample}$", color=PMVB_MUTED, fontsize=9,
        va="top", ha="left", style="italic")

# Annotation pointing at the first-image attenuation
first_image_pre = 20 * np.log10(np.abs(np.sinc((f_sample - f_signal) / f_sample)) + 1e-12)
first_image_post = first_image_pre + (-10 * np.log10(1 + ((f_sample - f_signal) / f_cutoff) ** (2 * order)))
ax.annotate(f"First image dropped\nby ~{first_image_pre - first_image_post:.0f} dB",
            xy=((f_sample - f_signal) / 1e6, first_image_post),
            xytext=(70, -40),
            color=PMVB_GREEN, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=PMVB_GREEN, lw=0.9))

# Axes setup
ax.set_xlabel("Frequency (MHz)", color=PMVB_FG, fontsize=11)
ax.set_ylabel("Amplitude (dB)", color=PMVB_FG, fontsize=11)
ax.set_title(f"DAC output spectrum:  $f_{{signal}}$ = {f_signal/1e6:.0f} MHz at  "
             f"$f_{{sample}}$ = {f_sample/1e6:.0f} MSPS",
             color=PMVB_FG, fontsize=12)
ax.axhline(0, color=PMVB_MUTED, lw=0.6)
ax.set_xlim(0, 3 * f_sample / 1e6)
ax.set_ylim(-90, 8)
ax.grid(True, alpha=0.35, color=PMVB_GRID, ls="-", lw=0.5)
ax.tick_params(colors=PMVB_FG)
for spine in ax.spines.values():
    spine.set_color(PMVB_GRID)
ax.legend(loc="lower left", facecolor=PMVB_PANEL, edgecolor=PMVB_GRID,
          labelcolor=PMVB_FG, framealpha=0.9, fontsize=9)

fig.tight_layout()

here = os.path.dirname(os.path.abspath(__file__))
fig.savefig(os.path.join(here, "1e_dac_spectrum.svg"),
            facecolor=PMVB_BG, edgecolor="none")
fig.savefig(os.path.join(here, "1e_dac_spectrum.png"),
            facecolor=PMVB_BG, edgecolor="none", dpi=150)
plt.close(fig)
print("Wrote 1e_dac_spectrum.svg + .png")
