!pip -q install kerrgeopy

import kerrgeopy as kg
import matplotlib.pyplot as plt
from math import cos, radians

print("\nCalculation for:")
print("1. Stable Orbit")
print("2. Constant Of Motion")

choice = input("\nSelect Calculation: ")

if choice == "1":
    a = float(input("Blackhole spin (0-0.998): "))
    p = float(input("Semi-latus rectum p (>6 suggested): "))
    e = float(input("Eccentricity (0-0.8): "))
    inc = float(input("Inclination (degree): "))

    x = cos(radians(inc))

    orbit = kg.StableOrbit(a=a, p=p, e=e, x=x)

    print("\nOrbit created successfully\n")
    print("Available properties:\n")

    public = []

    for item in dir(orbit):
        if not item.startswith("_"):
            public.append(item)

    for item in sorted(public):
        print(item)

    ans = input("\nPlot orbit? (y/n): ")

    if ans.lower() == "y":
        orbit.plot(0, 40)
        plt.show()


elif choice == "2":
    print("\nConstant Of Motion")

    a = float(input("Blackhole spin: "))
    E = float(input("Specific energy E: "))
    Lz = float(input("Angular momentum Lz: "))
    Q = float(input("Carter constant Q: "))

    orbit = kg.StableOrbit.from_constants(a, E, Lz, Q)

    print("\nOrbit created successfully\n")

    print("Calculated orbital parameters:")
    print(f"Semi-latus rectum (p): {orbit.p:.6f}")
    print(f"Eccentricity (e):       {orbit.e:.6f}")
    print(f"Inclination parameter (x): {orbit.x:.6f}")

    ans = input("\nPlot orbit? (y/n): ")

    if ans.lower() == "y":
        orbit.plot(0, 40)
        plt.show()
elif choice == "2":
    print("\nConstant Of Motion")

    a = float(input("Blackhole spin: "))
    E = float(input("Specific energy E: "))
    Lz = float(input("Angular momentum Lz: "))
    Q = float(input("Carter constant Q: "))

    orbit = kg.StableOrbit.from_constants(a, E, Lz, Q)

    print("\nOrbit created successfully\n")

    print("Calculated orbital parameters:")
    print(f"Semi-latus rectum (p): {orbit.p:.6f}")
    print(f"Eccentricity (e):       {orbit.e:.6f}")
    print(f"Inclination parameter (x): {orbit.x:.6f}")

    ans = input("\nPlot orbit? (y/n): ")

    if ans.lower() == "y":
        orbit.plot(0, 40)
        plt.show()
