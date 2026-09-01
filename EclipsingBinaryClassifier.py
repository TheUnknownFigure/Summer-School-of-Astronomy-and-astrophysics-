# Eclipsing Binary Classifier: EA / EB / EW

!pip install lightkurve scipy -q

import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# ---------------- USER INPUT ----------------

target = input("\nEnter target/star name: ").strip()
mission = input("Enter mission [Kepler/TESS]: ").strip().lower()

if mission not in ["kepler", "tess"]:
    print("Invalid mission.")
    raise SystemExit

# ---------------- GET DATA ----------------

print("\nSearching for light curve...")

search = lk.search_lightcurve(target, mission=mission)

if len(search) == 0:
    print("No light curve found.")
    raise SystemExit

# Use ONE light curve instead of stitching everything
lc = search[0].download()

lc = lc.remove_nans().normalize()

# Downsample to keep computation small
lc = lc.bin(time_bin_size=0.02)

# ---------------- FIND PERIOD ----------------

print("Finding orbital period...")

periodogram = lc.to_periodogram(
    method="boxleastsquares",
    minimum_period=0.4,
    maximum_period=5,
    frequency_factor=20
)

period = periodogram.period_at_max_power

print(f"Orbital period: {period.value:.4f} days")

# ---------------- PHASE FOLD ----------------

folded = lc.fold(period)

phase = folded.phase.value
flux = folded.flux.value

order = np.argsort(phase)
phase = phase[order]
flux = flux[order]

# ---------------- FIND ECLIPSES ----------------

# Find minima in the light curve
peaks, _ = find_peaks(
    -flux,
    distance=max(5, len(flux) // 8),
    prominence=0.003
)

if len(peaks) < 2:
    print("Could not detect two eclipses.")
    raise SystemExit

depths = 1 - flux[peaks]

# Two strongest eclipses
idx = np.argsort(depths)[-2:]
depths = depths[idx]

primary = max(depths)
secondary = min(depths)

ratio = secondary / primary

# ---------------- CLASSIFY ----------------

if ratio < 0.45:
    classification = "EA — Algol-like"

elif ratio > 0.70:
    classification = "EW — W UMa-like"

else:
    classification = "EB — Beta Lyrae-like"

# ---------------- OUTPUT ----------------

print("\n==============================")
print(" ECLIPSING BINARY CLASSIFIER")
print("==============================")

print(f"Target:           {target}")
print(f"Mission:          {mission.upper()}")
print(f"Period:           {period.value:.4f} days")
print(f"Primary depth:    {primary:.4f}")
print(f"Secondary depth:  {secondary:.4f}")
print(f"Depth ratio:      {ratio:.3f}")

print(f"\nClassification: {classification}")

# ---------------- PLOT ----------------

plt.figure(figsize=(8, 5))
plt.scatter(phase, flux, s=4)

plt.xlabel("Orbital Phase")
plt.ylabel("Normalized Flux")
plt.title(f"{target} — {classification}")
plt.grid(alpha=0.25)

plt.show()
