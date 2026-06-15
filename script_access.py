import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from rasterio.transform import xy
from scipy.spatial import cKDTree


name_territory = "Sainte-Baume" # possible name = ["Sainte-Baume","Luberon","Baronnies provençales","Alpilles","Camargue","Mont-Ventoux","Queyras","Verdon"]

grid= gpd.read_file(f"data_output/grid_square_{name_territory}.shp")
parcs = gpd.read_file("data_input/Parc/ref_parc_bdtopo_pnrpaca.geojson") #File containing all the boundaries of the regional parks in the region PACA
territory_L93 = parcs.loc[parcs["pnr_qgis"] == name_territory].to_crs(2154) #Keeping only one park
population =  "data_input/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R4_C19/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R4_C19.tif"

with rasterio.open(population) as src:

    transform, width, height = calculate_default_transform(
        src.crs, "EPSG:2154", src.width, src.height, *src.bounds
    )

    pop_2154 = np.empty((height, width), dtype=src.dtypes[0])

    reproject(
        source=src.read(1),
        destination=pop_2154,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs="EPSG:2154",
        resampling=Resampling.nearest
    )


# Coordonnées des centres des pixels
rows, cols = np.indices(pop_2154.shape)
xs, ys = xy(transform, rows, cols)

from shapely import contains_xy

living_space = territory_L93.geometry.iloc[0].buffer(20000)

mask = contains_xy(
    living_space,
    np.array(xs).ravel(),
    np.array(ys).ravel()
).reshape(pop_2154.shape)

population_area = np.where(mask, pop_2154, 0)

print(np.sum(population_area > 0))

xs = np.array(xs)
ys = np.array(ys)

# Conservation uniquement des pixels avec une population > 0

mask_pop = population_area > 0
coords_pop = np.column_stack([
    np.array(xs).ravel()[mask_pop.ravel()],
    np.array(ys).ravel()[mask_pop.ravel()]
])
pop_values = population_area[mask_pop]

# Construction de l'index spatial
tree = cKDTree(coords_pop)

# Centroïdes des carrés de la grille
centres = np.column_stack([
    grid.centroid.x,
    grid.centroid.y
])

# Rayon de recherche (en mètres)
rayon = 20000

# Calcul du potentiel de population
scores = []
scores_simple = []

for centre in centres:
    indices = tree.query_ball_point(centre, r=rayon)
    if len(indices) == 0:
        scores.append(0)
        continue
    pts = coords_pop[indices]
    dist = np.linalg.norm(pts - centre, axis=1)
    # Évite la division par zéro
    dist = np.maximum(dist, 1)
    score_dist = np.sum(pop_values[indices] / dist)
    scores_simple.append(score_dist)
    score_dist2 = np.sum(pop_values[indices] / (dist*dist))
    scores.append(score_dist2)

# Ajout du résultat à la grille
grid["pot_pop"] = scores
grid["pot2_pop"] = scores
grid.to_file("data_output/score_access.shp")