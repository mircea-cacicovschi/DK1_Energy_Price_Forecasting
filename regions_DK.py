import pandas as pd
import matplotlib.pyplot as plt
from dmi_open_data import DMIOpenDataClient
from adjustText import adjust_text

# Initialize DMI client with your API key
client = DMIOpenDataClient(api_key="6a73aa34-dc49-49d7-af91-5b8d487edf9f")

# Get all stations
stations = client.get_stations()

# Flatten geometry + properties
stations_flat = [{
    **s["properties"],
    "latitude": s["geometry"]["coordinates"][1],
    "longitude": s["geometry"]["coordinates"][0]
} for s in stations]

# Create DataFrame
df_stations = pd.DataFrame(stations_flat)

# Filter: Denmark + active SYNOP stations
df_dk_stations = df_stations[
    (df_stations["country"] == "DNK") &
    (df_stations["type"] == "Synop") &
    (df_stations["status"] == "Active")
].copy()

# Tag region based on longitude
df_dk_stations["region"] = df_dk_stations["longitude"].apply(lambda x: "DK1" if x < 11 else "DK2")

# # Separate DK1 and DK2 (optional coloring)
# colors = df_dk_stations["region"].map({"DK1": "blue", "DK2": "red"})

# # Create plot
# fig, ax = plt.subplots(figsize=(12, 14))
# ax.scatter(df_dk_stations["longitude"], df_dk_stations["latitude"], c=colors, s=40, alpha=0.7)

# # Add adjusted station name labels
# texts = []
# for _, row in df_dk_stations.iterrows():
#     texts.append(
#         ax.text(
#             row["longitude"],
#             row["latitude"],
#             row["name"],
#             fontsize=6,
#             alpha=0.85
#         )
#     )

# adjust_text(
#     texts,
#     arrowprops=dict(arrowstyle="-", color='gray', lw=0.4)
# )

# # Add vertical divider for DK1/DK2
# ax.axvline(x=12.1, color='gray', linestyle='--', label='Approx DK1/DK2 Boundary (12.1°E)')

# # Final plot settings
# ax.set_title("Active SYNOP Weather Stations in Denmark (Adjusted Labels)", fontsize=14)
# ax.set_xlabel("Longitude")
# ax.set_ylabel("Latitude")
# ax.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()


exclude_stations = ["Harald B", "Gorm C"]
df_dk_stations = df_dk_stations[~df_dk_stations["name"].isin(exclude_stations)]

import matplotlib.pyplot as plt
from adjustText import adjust_text

# --- 0) Optional: drop obvious duplicates by name (keeps the first occurrence)
df_dk_stations = df_dk_stations.drop_duplicates(subset="name").copy()

# --- 1) Colors by region
colors = df_dk_stations["region"].map({"DK1": "blue", "DK2": "red"})

# --- 2) Figure
fig, ax = plt.subplots(figsize=(14, 10), dpi=140)
ax.scatter(
    df_dk_stations["longitude"],
    df_dk_stations["latitude"],
    c=colors, s=35, alpha=0.85, edgecolor="none"
)

# --- 3) Label helper
texts = []

def add_labels(df, rotate_if_dense=False):
    for _, row in df.iterrows():
        rotation = 12 if (rotate_if_dense and row["region"] == "DK1") else 0
        texts.append(
            ax.text(
                row["longitude"],
                row["latitude"],
                row["name"],
                fontsize=7,
                rotation=rotation,
                alpha=0.96,
                zorder=5,
                bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=0.6)
            )
        )

# --- 4) Label order: DK2 first (fewer labels), then DK1 with slight rotation
add_labels(df_dk_stations[df_dk_stations["region"] == "DK2"], rotate_if_dense=False)
add_labels(df_dk_stations[df_dk_stations["region"] == "DK1"], rotate_if_dense=True)

# --- 5) Smarter adjustment (more room + more iterations)
adjust_text(
    texts,
    expand_points=(1.5, 2.0),   # push labels away from points more
    expand_text=(1.3, 1.7),     # allow labels to push apart more
    force_points=0.10,          # gentler pull to points
    force_text=1.00,            # stronger label-vs-label repulsion
    lim=1000,                   # more iterations for dense clusters
    only_move={'points': 'y', 'text': 'xy'},
    arrowprops=dict(arrowstyle="-", color="gray", lw=0.35, alpha=0.7)
)

# --- 6) DK1/DK2 divider
ax.axvline(x=11, color='gray', linestyle='--',
           label='Approx DK1/DK2 Boundary (11°E)')

# --- 7) Cosmetics
ax.set_title("Active SYNOP Weather Stations in Denmark", fontsize=13)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend(loc="upper right", frameon=True, framealpha=0.9)
ax.grid(True, alpha=0.25)
plt.tight_layout()
plt.show()