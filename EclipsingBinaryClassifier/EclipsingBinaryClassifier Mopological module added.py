!pip install lightkurve scipy -q

import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_widths

target = input("\nEnter target/star name: ").strip()
mission = input("Enter mission [Kepler/TESS]: ").strip().lower()

if mission not in ["kepler", "tess"]:
    print("Invalid mission.")
    raise SystemExit

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

print("Finding orbital period...")

periodogram = lc.to_periodogram(
    method="boxleastsquares",
    minimum_period=0.4,
    maximum_period=5,
    frequency_factor=20
)

period = periodogram.period_at_max_power

print(f"Orbital period: {period.value:.4f} days")

folded = lc.fold(period)

phase = folded.phase.value
flux = folded.flux.value

order = np.argsort(phase)

phase = phase[order]
flux = flux[order]

print("\nCalculating morphological features...")

# Minima become peaks when the flux is inverted.
peaks, properties = find_peaks(
    -flux,
    distance=max(5, len(flux) // 8),
    prominence=0.003
)

if len(peaks) < 2:
    print("Could not detect two eclipses.")
    raise SystemExit

depths = 1 - flux[peaks]

# Select the two deepest minima
idx = np.argsort(depths)[-2:]

eclipse_indices = peaks[idx]
depths = depths[idx]

# Sort the eclipses according to phase
phase_order = np.argsort(phase[eclipse_indices])

eclipse_indices = eclipse_indices[phase_order]
depths = depths[phase_order]

primary_index = eclipse_indices[np.argmax(depths)]
secondary_index = eclipse_indices[np.argmin(depths)]

primary_depth = 1 - flux[primary_index]
secondary_depth = 1 - flux[secondary_index]

primary_phase = phase[primary_index]
secondary_phase = phase[secondary_index]

depth_ratio = secondary_depth / primary_depth


widths, width_heights, left_ips, right_ips = peak_widths(
    -flux,
    eclipse_indices,
    rel_height=0.5
)

# Convert the width from data points into orbital phase.
phase_step = np.median(np.diff(phase))

eclipse_widths = widths * phase_step

primary_width = eclipse_widths[np.argmax(depths)]
secondary_width = eclipse_widths[np.argmin(depths)]


# Exclude a region around each eclipse.
# The remaining data describe the light curve between
# the eclipses.

exclude_width = 0.08

out_of_eclipse = (
    (np.abs(phase - primary_phase) > exclude_width) &
    (np.abs(phase - secondary_phase) > exclude_width)
)

oe_phase = phase[out_of_eclipse]
oe_flux = flux[out_of_eclipse]

if len(oe_flux) < 10:

    curvature = np.nan
    oe_amplitude = np.nan

else:

    # Sort by phase
    sort_order = np.argsort(oe_phase)

    oe_phase = oe_phase[sort_order]
    oe_flux = oe_flux[sort_order]

    coefficients = np.polyfit(
        oe_phase,
        oe_flux,
        2
    )

    curvature = 2 * coefficients[0]

    oe_amplitude = np.max(oe_flux) - np.min(oe_flux)

if np.isnan(oe_amplitude):

    out_of_eclipse_note = (
        "Insufficient out-of-eclipse data for a reliable "
        "morphological assessment."
    )

elif oe_amplitude < 0.01:

    out_of_eclipse_note = (
        "The out-of-eclipse region is relatively flat, "
        "showing little continuous brightness variation."
    )

elif oe_amplitude < 0.03:

    out_of_eclipse_note = (
        "The out-of-eclipse region shows moderate "
        "continuous brightness variation."
    )

else:

    out_of_eclipse_note = (
        "The out-of-eclipse region shows strong continuous "
        "brightness variation, which may indicate significant "
        "ellipsoidal or contact-related behaviour."
    )

print("\nMORPHOLOGICAL FEATURES")

print(f"Primary eclipse phase:       {primary_phase:.4f}")
print(f"Secondary eclipse phase:     {secondary_phase:.4f}")

print(f"Primary eclipse depth:       {primary_depth:.4f}")
print(f"Secondary eclipse depth:     {secondary_depth:.4f}")

print(f"Eclipse depth ratio:         {depth_ratio:.4f}")

print(f"Primary eclipse width:        {primary_width:.4f}")
print(f"Secondary eclipse width:      {secondary_width:.4f}")

print(f"Out-of-eclipse amplitude:    {oe_amplitude:.6f}")
print(f"Out-of-eclipse curvature:    {curvature:.6f}")

print("\nOut-of-eclipse assessment:")
print(out_of_eclipse_note)


classification = "Morphological classification pending calibration"

print("\nECLIPSING BINARY CLASSIFIER")

print(f"Target:           {target}")
print(f"Mission:          {mission.upper()}")
print(f"Period:           {period.value:.4f} days")

print(f"Primary eclipse:  {primary_depth:.4f}")
print(f"Secondary eclipse:{secondary_depth:.4f}")
print(f"Depth ratio:      {depth_ratio:.4f}")

print(f"\nClassification: {classification}")


plt.figure(figsize=(8, 5))

plt.scatter(
    phase,
    flux,
    s=4
)

plt.xlabel("Orbital Phase")
plt.ylabel("Normalized Flux")

plt.title(
    f"{target} — Phase-Folded Light Curve"
)

plt.grid(alpha=0.25)

plt.show()
