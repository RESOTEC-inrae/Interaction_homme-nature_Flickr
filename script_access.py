import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from rasterio.transform import xy,Affine
from scipy.spatial import cKDTree
from shapely import contains_xy
from shapely.geometry import box
import configuration 

def main(name_territory_full,grid,square_size):
    (name_territory,photo,image_caracteristic,territory_L93,geom_union_territory,department_area,territory_city) = configuration.config(name_territory_full)

    population =  "data_input/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R4_C19/GHS_POP_E2025_GLOBE_R2023A_54009_100_V1_0_R4_C19.tif"
    raster_pop = f"data_output/pop_{name_territory}.tif" #name of the file saved later

    if square_size % 100 != 0:
        print("La taille des carreaux n'est pas adapté à la donnée de population")
    factor = int(square_size / 100)  # 1000 m / 100 m
    
    living_space = territory_L93.geometry.iloc[0].buffer(20000) #getting population less than 20 km from the parc


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

        # Dimensions compatible with the aggregation factor
        new_height = pop_2154.shape[0] // factor
        new_width = pop_2154.shape[1] // factor

        
        # Trimming to remove incomplete edges
        pop_2154 = pop_2154[:new_height * factor, :new_width * factor]
        
        # Sum aggregation over the new size
        pop = pop_2154.reshape(
            new_height, factor,
            new_width, factor
        ).sum(axis=(1, 3))

        new_transform = transform * Affine.scale(factor, factor)

        profile = src.profile.copy()
        profile.update(
            driver="GTiff",
            crs="EPSG:2154",
            transform=new_transform,
            width=new_width,
            height=new_height,
            dtype=pop.dtype,
            count=1,
            compress="lzw"
        )

        with rasterio.open(raster_pop, "w", **profile) as dst:
            dst.write(pop, 1)


    with rasterio.open(raster_pop) as src:
        pop = src.read(1)
        transform = src.transform

        # Pixel centre coordinates
        rows_grid, cols_grid = np.indices(pop.shape)
        xs, ys = xy(transform, rows_grid, cols_grid)

        xs = np.asarray(xs)
        ys = np.asarray(ys)

        # Pixels in the buffer
        mask_space = contains_xy(
            living_space,
            xs.ravel(),
            ys.ravel()
        ).reshape(pop.shape)

        # Pixels to retain: 2 criteria to check
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

    # Centres of the grid
    centres = np.column_stack([
        grid.centroid.x,
        grid.centroid.y,
        grid["dist_town"]
    ])

    # Search radius (in metres)
    rayon = 20000

    # Calculation of population potential
    scores = []
    scores_simple = []

    for centre in centres:
        indices = tree.query_ball_point([centre[0],centre[1]], r=rayon)

        pts = centres_pop[indices]
        
        dist = np.linalg.norm(pts - [centre[0],centre[1]], axis=1)
        
        # Avoid division by zero
        dist = np.maximum(dist, 10)
        score_dist = np.sum(pop_values[indices] / dist)
        scores_simple.append(score_dist)
        score_dist2 = np.sum(pop_values[indices] / (dist*dist))
        scores.append(score_dist2)
        

    # Adding the result to the grid
    grid["apl_bird"] = scores_simple
    grid["apl_bird_c"] = scores

    grid.to_file(f"data_output/score_access_{name_territory}.shp")