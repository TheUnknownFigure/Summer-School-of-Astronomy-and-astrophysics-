import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

target = input("\nEnter a star/target name (e.g. Kepler-10): ")

mission = input("Enter mission [Kepler/TESS]: ").strip().lower()

print("\nSearching for pixel data...")

if mission == "kepler":
    search = lk.search_targetpixelfile(
        target,
        mission="Kepler"
    )

elif mission == "tess":
    search = lk.search_targetpixelfile(
        target,
        mission="TESS"
    )

else:
    print("Invalid mission.")
    raise SystemExit

if len(search) == 0:
    print("No Target Pixel File found.")
    raise SystemExit

print(f"Found {len(search)} available pixel files.")


tpf = search[0].download()

if tpf is None:
    print("Could not download the pixel file.")
    raise SystemExit

print("\nPixel file successfully loaded.")

#Tpf = 3 D array
#tpf.shape[1] → number of pixels in Y
#tpf.shape[2] → number of pixels in X
#tpf.time → observation times

print(f"Target: {target}")
print(f"Mission: {mission.upper()}")
print(f"Pixel dimensions: {tpf.shape[1]} × {tpf.shape[2]}")
print(f"Number of frames: {len(tpf.time)}")

frame_number = len(tpf.time) // 2

image = tpf.flux[frame_number].value

plt.figure(figsize=(7, 6))

plt.imshow(
    image,
    origin="lower",
    cmap="inferno"
)

plt.colorbar(label="Flux")

plt.title(
    f"{target} — Detector Pixel Frame\n"
    f"Frame {frame_number}"
)

plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")

plt.show()


brightest_pixel = np.unravel_index(
    np.nanargmax(image),
    image.shape
)

print("\nBrightest pixel:")
print(f"Y = {brightest_pixel[0]}")
print(f"X = {brightest_pixel[1]}")
print(f"Flux = {image[brightest_pixel]:.2f}")


mean_image = np.nanmedian(
    tpf.flux.value,
    axis=0
)

plt.figure(figsize=(7, 6))

plt.imshow(
    mean_image,
    origin="lower",
    cmap="inferno"
)

plt.colorbar(label="Median Flux")

plt.scatter(
    brightest_pixel[1],
    brightest_pixel[0],
    marker="x",
    s=100
)

plt.title(
    f"{target} — Median Pixel Flux Map"
)

plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")

plt.show()


pixel_variability = np.nanstd(
    tpf.flux.value,
    axis=0
)

plt.figure(figsize=(7, 6))

plt.imshow(
    pixel_variability,
    origin="lower",
    cmap="viridis"
)

plt.colorbar(label="Flux Standard Deviation")

plt.title(
    f"{target} — Pixel Variability Map"
)

plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")

plt.show()


lc = tpf.to_lightcurve(
    method="aperture"
)

lc = lc.normalize()

plt.figure(figsize=(10, 5))

plt.plot(
    lc.time.value,
    lc.flux.value
)

plt.xlabel("Time")
plt.ylabel("Normalized Flux")

plt.title(
    f"{target} — Light Curve Extracted From Pixels"
)

plt.show()
