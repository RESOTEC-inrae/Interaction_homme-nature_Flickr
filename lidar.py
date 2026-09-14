from pathlib import Path
import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import box
import configuration 
import re
from scipy.spatial import cKDTree
import configuration 

def main(name_territory_full,grid_input):
    (name_territory,photo,image_caracteristic,territory_L93,geom_union_territory,department_area,territory_city) = configuration.config(name_territory_full)
    name_territory_simple = re.sub(r"(-| provencales|Monts d'|Mont)", "", name_territory)


    dtmlidar = Path(f"/local/AIX/jbarrere/lidarhd/data/mnh/{name_territory_simple}") #Localisation of all Lidar HD Data

    vegetal = gpd.read_file("data_output/vegetation.shp")
    

    pairs = gpd.sjoin(vegetal[["geometry"]],grid_input[["square_id", "geometry"]],predicate="intersects",how="inner")
    pairs["grid_geom"] = grid_input.geometry.take(pairs["index_right"].to_numpy()).values
    pairs["geometry"] = pairs.geometry.intersection(pairs["grid_geom"])
    pairs = pairs[~pairs.geometry.is_empty]
    grid = (pairs[["square_id", "geometry"]].dissolve(by="square_id").reset_index())

    square = []

    for file in dtmlidar.iterdir(): # see all file in the directories stored in list_dep_dtm            
        if file.suffix.lower() in [".asc", ".tif", ".tiff"]: # keeping only file that are useful for a DEM file
            square.append(file) 

    valid_files = []
    invalid_files = []
    for file in square:
        try:
            with rasterio.open(file) as src:
                src.read(1)
                valid_files.append(file)
        except Exception as e:
            invalid_files.append(file)

    print("Invalid files:", len(invalid_files)) # Some informations were not readable but the number was small enough

    resultats = []
    for file in valid_files:
        with rasterio.open(file) as src:
            # Read pixels
            data = src.read(1)
            # Remplace NoData (-9999) by NaN
            data = np.where((data == src.nodata) | (data == 0), np.nan, data)
            # valid pixels means
            moyenne = np.nanmean(data)
            ecart_type = np.nanstd(data)
            percentile_10 = np.nanpercentile(data, 10)
            percentile_90 = np.nanpercentile(data, 90)
            # Tile geographic area
            bounds = src.bounds
            geometrie = box(
                bounds.left,
                bounds.bottom,
                bounds.right,
                bounds.top
            )
            resultats.append({
                "moyenne": moyenne,
                "q10": percentile_10,
                "q90": percentile_90,
                "geometry": geometrie,
                "ecart_type" : ecart_type
            })

    gdf = gpd.GeoDataFrame(
        resultats,
        crs="EPSG:2154"
    )

    centre_lidar = np.column_stack([
        gdf.centroid.x,
        gdf.centroid.y,
    ])

    centre_grid = np.column_stack([
        grid.centroid.x,
        grid.centroid.y,
    ])


    tree = cKDTree(centre_lidar)

    # Finding the Lidar square closest to each tile of the grid
    distances, indices = tree.query(centre_grid, k=1)

    # Getting the datas of the Lidar
    grid["veg_alt"] = gdf.iloc[indices]["moyenne"].to_numpy()
    grid["veg_q10"] = gdf.iloc[indices]["q10"].to_numpy()
    grid["veg_q90"] = gdf.iloc[indices]["q90"].to_numpy()
    grid["veg_sd"] = gdf.iloc[indices]["ecart_type"].to_numpy()


    grid= grid.drop (columns=['geometry'])

    grid_output = grid_input.merge(grid, on=["square_id"],how="left")
    return grid_output

