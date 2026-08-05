import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from rasterio.transform import xy,Affine
from scipy.spatial import cKDTree
from shapely import contains_xy
from shapely.geometry import box
from configuration import name_territory_full,name_territory,photo,image_caracteristic,territory_L93,geom_union_territory,territory_city


#name_territory_full = "Sainte-Baume" # possible name = ["Sainte-Baume","Luberon","Baronnies provençales","Alpilles","Camargue","Mont-Ventoux","Queyras","Verdon"]

grid= gpd.read_file(f"data_output/grid_square_{name_territory}.shp")
#print(grid['dist_town'].head(2))

#parcs = gpd.read_file("data_input/Parc/ref_parc_bdtopo_pnrpaca.geojson") #File containing all the boundaries of the regional parks in the region PACA
#territory_L93 = parcs.loc[parcs["pnr_qgis"] == name_territory_full].to_crs(2154) #Keeping only one park
population =  "data_input/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R4_C19/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R4_C19.tif"
factor = 10  # 1000 m / 100 m
raster_pop = f"data_output/pop_1km_{name_territory}.tif"
living_space = territory_L93.geometry.iloc[0].buffer(20000)

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

    # Dimensions compatibles avec le facteur d'agrégation
    new_height = pop_2154.shape[0] // factor
    new_width = pop_2154.shape[1] // factor

    
    # Découpage pour éliminer les bords incomplets
    pop_2154 = pop_2154[:new_height * factor, :new_width * factor]
    
    # Agrégation par somme sur des blocs 10x10
    pop_1km = pop_2154.reshape(
        new_height, factor,
        new_width, factor
    ).sum(axis=(1, 3))

    # Nouveau transform (taille pixel multipliée par 10)
    new_transform = transform * Affine.scale(factor, factor)

    profile = src.profile.copy()
    profile.update(
        driver="GTiff",
        crs="EPSG:2154",
        transform=new_transform,
        width=new_width,
        height=new_height,
        dtype=pop_1km.dtype,
        count=1,
        compress="lzw"
    )

    with rasterio.open(raster_pop, "w", **profile) as dst:
        dst.write(pop_1km, 1)




with rasterio.open(raster_pop) as src:
    pop = src.read(1)
    transform = src.transform

    # Coordonnées des centres des pixels
    rows_grid, cols_grid = np.indices(pop.shape)
    xs, ys = xy(transform, rows_grid, cols_grid)

    xs = np.asarray(xs)
    ys = np.asarray(ys)

    # Pixels dans le buffer
    mask_space = contains_xy(
        living_space,
        xs.ravel(),
        ys.ravel()
    ).reshape(pop.shape)

    # Pixels à conserver
    mask_final = (pop > 0) & mask_space

    rows, cols = np.where(mask_final)

    pixel_width = transform.a
    pixel_height = abs(transform.e)

    geoms = []
    values = []

    for row, col in zip(rows, cols):
        x_min, y_max = xy(transform, row, col, offset="ul")

        geoms.append(
            box(
                x_min,
                y_max - pixel_height,
                x_min + pixel_width,
                y_max
            )
        )

        values.append(pop[row, col])

gdf = gpd.GeoDataFrame(
    {"population": values},
    geometry=geoms,
    crs=src.crs
)

gdf.to_file(f"data_output/pixels_population_{name_territory}.shp")

rows, cols = np.where(mask_final)

x_centres, y_centres = xy(transform, rows, cols)

centres_pop = np.column_stack([
    x_centres,
    y_centres
])

pop_values = pop[rows, cols]

tree = cKDTree(centres_pop)

# Centres de la grille
centres = np.column_stack([
    grid.centroid.x,
    grid.centroid.y,
    grid["dist_town"]
])

# Centroïdes des carrés de la grille
# centres = np.column_stack([
#     grid.centroid.x,
#     grid.centroid.y,
#     grid["dist_town"]
# ])

# Rayon de recherche (en mètres)
rayon = 20000

# Calcul du potentiel de population
scores = []
scores_simple = []

for centre in centres:
    indices = tree.query_ball_point([centre[0],centre[1]], r=rayon)

    pts = centres_pop[indices]
    
    dist = np.linalg.norm(pts - [centre[0],centre[1]], axis=1)
    
    # Évite la division par zéro
    dist = np.maximum(dist, 10)
    dist_route = np.maximum(centre[2], 10)
    score_dist = np.sum(pop_values[indices] / dist)
    scores_simple.append(score_dist)
    score_dist2 = np.sum(pop_values[indices] / (dist*dist))
    scores.append(score_dist2)
    #print(centre[2])
    
    
# Ajout du résultat à la grille
grid["pot_pop"] = scores
grid["pot2_pop"] = scores_simple

print(sorted(grid["leasure"].unique()))
print(grid["leasure"].nunique())
grid.to_file(f"data_output/score_access_{name_territory}.shp")