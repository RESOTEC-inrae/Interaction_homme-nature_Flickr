import geopandas as gpd
import pandas as pd
import shapely as shp
from shapely.geometry import box, Polygon, MultiPolygon
import numpy as np
#import osmnx as ox
import rasterio
from rasterio.merge import merge
#from rasterio.transform import rowcol
from pathlib import Path
#import multiprocessing
from multiprocessing import Pool
from configuration import name_territory_full,name_territory,photo,image_caracteristic,territory_L93,geom_union_territory,territory_city


# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# parcs = gpd.read_file("data_input/Parc/ref_parc_bdtopo_pnrpaca.geojson") #File containing all the boundaries of the regional parks in the region PACA
# territory_L93 = parcs.loc[parcs["pnr_qgis"] == name_territory_full].to_crs(2154) #Keeping only one park
# geom_union_territory = territory_L93.union_all() #Cleaning up the file to remove errors
# territory_city = gpd.read_file("data_input/ADMIN-EXPRESS_4-0__GPKG_LAMB93_FXX_2025-05-12/ADMIN-EXPRESS/1_DONNEES_LIVRAISON_2025-05-00071/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12.gpkg",
#                                layer = "commune") # Administrative boundaries of towns and cities : Useful file to create center of the urban area

vegetal_04 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D004_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D004/FORMATION_VEGETALE.shp")
vegetal_05 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D005_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D005/FORMATION_VEGETALE.shp")
vegetal_06 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D006_2021-03-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D006/FORMATION_VEGETALE.shp")
vegetal_07 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D007_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D007/FORMATION_VEGETALE.shp")
vegetal_13 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D013_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D013/FORMATION_VEGETALE.shp")
vegetal_2A = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D02A_2017-05-10/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D02A/FORMATION_VEGETALE.shp")
vegetal_2B = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D02B_2016-02-16/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D02B/FORMATION_VEGETALE.shp")
vegetal_26 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D026_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D026/FORMATION_VEGETALE.shp")
vegetal_43 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D043_2021-11-15/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D043/FORMATION_VEGETALE.shp")
vegetal_83 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D083_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D083/FORMATION_VEGETALE.shp")
vegetal_84 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D084_2022-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D084/FORMATION_VEGETALE.shp")
list_dep_vegetal = [vegetal_04,vegetal_05,vegetal_06,vegetal_07,vegetal_13,vegetal_2A,vegetal_2B,vegetal_26,vegetal_43,vegetal_83,vegetal_84] # General territory of study
list_vegetal = []
liste_dep=[] # Department position (ex: vegetal_04 = 0, vegetal_06 = 2)
j=0
for i in list_dep_vegetal:
    bbox = box(*i.total_bounds)
    if bbox.intersects(geom_union_territory):
        list_vegetal.append(i) # Keeping only the important departments for the park in question
        liste_dep.append(j) # Keeping the position of the important departments 
        # ==> It's important to add every data for all department to keep it working
        # It allows a much faster speed of processing for other information (building)
    j=j+1
vegetal = pd.concat(list_vegetal,ignore_index=True)  # fusionning the data from the remaining department 
vegetal["geometry"] = vegetal.geometry.make_valid()

# #%%%%%%%%  Bd Alti  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Elevation data that can be used with at least 1 park

dtm04 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D004_2023-08-08/BDALTIV2/1_DONNEES_LIVRAISON_2023-08-00161/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D004")
dtm05 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D005_2021-08-04/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D005")
dtm06 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D006_2023-08-08/BDALTIV2/1_DONNEES_LIVRAISON_2023-08-00161/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D006")
dtm07 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D007_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D007")
dtm13 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D013_2022-07-29/BDALTIV2/1_DONNEES_LIVRAISON_2022-08-00118/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D013")
dtm2A = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN78C_D02A_2020-04-16/BDALTIV2/1_DONNEES_LIVRAISON_2020-06-00405/BDALTIV2_MNT_25M_ASC_LAMB93_IGN78C_D02A")
dtm2B = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN78C_D02B_2020-04-16/BDALTIV2/1_DONNEES_LIVRAISON_2020-06-00405/BDALTIV2_MNT_25M_ASC_LAMB93_IGN78C_D02B")
dtm26 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D026_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D026")
dtm43 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D043_2022-10-03/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D043")
dtm83 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D083_2022-12-05/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D083")
dtm84 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D084_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D084")
list_dep_dtm = [dtm04,dtm05,dtm06,dtm07,dtm13,dtm2A,dtm2B,dtm26,dtm43,dtm83,dtm84]  # General territory of study

square = [] # variable with all the tiles that overlaps with the park of study
for folder in list_dep_dtm :
    for file in folder.iterdir(): # see all file in the directories stored in list_dep_dtm
        if file.suffix.lower() in [".asc", ".tif", ".tiff"]: # keeping only file that are useful for a DEM file
            with rasterio.open(file) as src:
                bounds = src.bounds 
                raster_geom = box(*bounds)
                if raster_geom.intersects(geom_union_territory): # Check if the tile is overlapping the field of study 
                    square.append(file) 


# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# #GRASS Script which allow to know the distance between the squares and the town centers
# Doesn't work well

#Script R which allow to know the distance between the squares and the town centers
grid = gpd.read_file(f"data_output/distance_route_mairie_{name_territory}.shp")
dist_town = gpd.read_file(f"data_output/distance_town_{name_territory}.shp")

dist_town= dist_town.drop (columns=['geometry','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','leas_autum', 'leas_sprin', 'leas_sumer', 'leas_wint',"nature","leasure",'dist_path','dist_road'])
dist_town[["sq_id_2X", "square_id"]] = dist_town[["sq_id_2X", "square_id"]].astype(int)

grid = grid.merge(dist_town, on=["square_id",'sq_id_2X',],how="left")
#grid = grid.merge(dist_town, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','leas_autum', 'leas_sprin', 'leas_sumer', 'leas_wint',"nature","leasure",'dist_path','dist_road'],how="left") #Inserting the distance to the city into the main data file

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#Integration of the forest coverage
vegetal = gpd.clip(vegetal, territory_L93) #keep only the data around our field of study

modifications = {
    "Forêt fermée sans couvert arboré": "F_fermee",
    "Forêt fermée feuillus": "F_fermee",
    "Forêt fermée conifères": "F_fermee",
    "Forêt fermée mixte": "F_fermee",
    "Forêt ouverte sans couvert arboré": "F_ouvert",
    "Forêt ouverte feuillus": "F_ouvert",
    "Forêt ouverte conifères": "F_ouvert",
    "Forêt ouverte mixte": "F_ouvert",
    "Peupleraie": "Peupleraie",
    "Lande": "vege_bas",
    "Formation herbacée": "vege_bas",
} 
vegetal["TFV_G11"] = vegetal["TFV_G11"].replace(modifications) # we regroup some categories together when they are quite similar (in term of density)
 
vegetal["geometry"] = vegetal.buffer(0)
vegetal = vegetal.dissolve(by="TFV_G11").reset_index() # fusion of the same value of all polygons in the study area0

# vegetal["geometry"] = vegetal.geometry.simplify(10) # Reducing the weight of the geometries /// Not really useful

vegetal.to_file("data_output/vegetation.shp")
vegetal = gpd.read_file("data_output/vegetation.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# # Version 1: USING JOIN #################################################### 

 
vegetal = vegetal.explode(index_parts=False).reset_index(drop=True) # split complex geometries into simpler ones, in order to speed up the process

pairs = gpd.sjoin(grid,vegetal[["geometry","TFV_G11"]],predicate="intersects",how="inner") # spatial intersection to cut the vegetation with the grid
pairs["veg_geom"] = vegetal.geometry.take(pairs["index_right"].to_numpy()).values # Retrieve the geometry of the matched vegetation polygon for each pair
intersections = pairs.geometry.intersection(pairs["veg_geom"])# create the geometric intersection between the grid cells and its corresponding vegetation polygon

grid["area_cell"] = grid.area
pairs["area_veg"] = intersections.area

area_veg = (pairs.pivot_table( index="square_id", columns="TFV_G11",values="area_veg",aggfunc="sum",fill_value=0).reset_index()) 
# Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area

grid = grid.merge(area_veg,on="square_id",how="left")

if "Peupleraie" not in grid.columns:
    grid["Peupleraie"] = 0

#Transform the value into percentages in order to better understand the details
grid["F_fermee"] = (grid["F_fermee"]/grid["area_cell"]*100).fillna(0)
grid["F_ouvert"] = (grid["F_ouvert"]/grid["area_cell"]*100).fillna(0)
grid["Peupleraie"] = (grid["Peupleraie"]/grid["area_cell"]*100).fillna(0)
grid["vege_bas"] = (grid["vege_bas"]/grid["area_cell"]*100).fillna(0)
grid = grid.drop(columns = "area_cell")


# grid.to_file("data_output/square_vegetation.shp")
# grid = gpd.read_file("data_output/square_vegetation.shp")

grid_vegetation = grid.copy()
grid_vegetation["geometry"] = grid_vegetation.geometry.centroid.buffer(10000) # create a circle of 10km of radius for each square of the grid

vegetal_inter = gpd.sjoin(grid,vegetal[["geometry","TFV_G11"]],predicate="intersects",how="inner") # spatial intersection to cut the vegetation with the grid
vegetal_inter["area"] = vegetal_inter.area # calculate the size of the new areas created by the line above

surface_buffer = np.pi * 10000**2 #Calculate the area of each circle created before (πR²)

grid_veg_stat = vegetal_inter.groupby(
    ["square_id", "TFV_G11"]
)["area"].sum().reset_index() # Adding all polygon present with the same type of vegetation, here we add them together 
grid_veg_stat["area"] = (grid_veg_stat["area"] / surface_buffer) * 100  # Obtain the proportion (%) of the vegetation in the circle

# Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area
grid_forest = grid_veg_stat.pivot(
    index="square_id",
    columns="TFV_G11",
    values="area"
).fillna(0) # Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area


grid_forest = grid_forest.rename(columns={
    "F_fermee": "F_clos10km",
    "F_ouvert": "F_open10km",
    "Peupleraie": "Peup10km",
    "vege_bas": "grass10km",
}) # Renaiming the name to better reflect what the value show

if "Peup10km" not in grid_forest.columns:
    grid["Peup10km"] = 0

grid = grid.merge(grid_forest, on=["square_id"],how="left") #Inserting the value of vegetation into the main data file
grid[["F_clos10km", "F_open10km", "Peup10km", "grass10km"]] = (
    grid[["F_clos10km", "F_open10km", "Peup10km", "grass10km"]].fillna(0)
)

grid.to_file(f"data_output/vegetation_cercle_{name_territory}.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# # Version 2 USING OVERLAY #################################################
# vegetal = gpd.overlay(vegetal, grid, how="intersection") # spatial intersection to cut the vegetation with the grid
# vegetal["surface"] = vegetal.area # calculate the size of the new areas created by the line above
# grid_forest = vegetal.groupby(["square_id", "TFV_G11"])["surface"].sum().reset_index() 
# # It's possible that multiple polygon are present with the same type of vegetation, here we add them together 

# grid_forest["surface"]=grid_forest["surface"]/100 #/10000 m²(surface)*100(%) ------ Obtain the proportion in the square of the vegetation

# grid_forest = grid_forest.pivot(
#     index="square_id",
#     columns="TFV_G11",
#     values="surface"
# ).fillna(0) # Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area
# grid = grid.merge(grid_forest, on=["square_id"],how="left") #Inserting the value of vegetation into the main data file
# grid.to_file("data_output/square_vegetation.shp")
# grid = gpd.read_file("data_output/square_vegetation.shp")

# #%%%%%%%%%%%%

# grid_vegetation = grid.copy()
# grid_vegetation["geometry"] = grid_vegetation.geometry.centroid.buffer(1000) # create a circle of 1km of radius for each square of the grid

# vegetal_inter = gpd.overlay(vegetal, grid_vegetation, how="intersection") #  spatial intersection to cut the vegetation with the new geometries
# vegetal_inter["surface"] = vegetal_inter.area # calculate the size of the new areas created by the line above

# surface_buffer = np.pi * 1000**2 #Calculate the area of each circle created before (πR²)

# grid_veg_stat = vegetal_inter.groupby(
#     ["square_id", "TFV_G11"]
# )["surface"].sum().reset_index() # Adding all polygon present with the same type of vegetation, here we add them together 
# grid_veg_stat["surface"] = (grid_veg_stat["surface"] / surface_buffer) * 100  # Obtain the proportion (%) of the vegetation in the circle

# grid_forest = grid_veg_stat.pivot(
#     index="square_id",
#     columns="TFV_G11",
#     values="surface"
# ).fillna(0) # Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area

# grid_forest = grid_forest.rename(columns={
#     "F_fermee": "F_close1km",
#     "F_ouvert": "F_open_1km",
#     "Peupleraie": "Peup_1km",
#     "vege_bas": "grass_1km",
# }) # Renaiming the name to better reflect what the value show

# grid = grid.merge(grid_forest, on=["square_id"],how="left") #Inserting the value of vegetation into the main data file

# grid.to_file("data_output/vegetation_cercle_{name_territory}.shp")
#grid = gpd.read_file(f"data_output/vegetation_cercle_{name_territory}.shp")
 
# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# %%%%%%%%%%%%%%%%% DTM

mosaic, out_transform = merge(square) # Merge all raster tiles (previously only a list) into a single mosaic raster.
with rasterio.open(square[0]) as src:
    metadonne_tif = src.meta.copy()
    metadonne_tif.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform,
        "crs": "EPSG:2154"
    }) # Getting metadata from one square to complete the properties of the merged raster, plus the projection

grid_centroid_alti = gpd.GeoDataFrame(
    grid,
    geometry=grid.centroid,
    crs="EPSG:2154"
) #The elevation chosen is the one at the center of the square

######### Version 1

# Create a static version of the result
with rasterio.open("data_output/mnt.tif", "w",**metadonne_tif) as dest:
    dest.write(mosaic)
with rasterio.open("data_output/mnt.tif") as src:
    coords = [(geom.x, geom.y) for geom in grid_centroid_alti.geometry]
    values = list(src.sample(coords))
grid_centroid_alti["elevation"] = [val[0] for val in values] # Obtain the elevation for each centroid of the squares

######## Version 2

# coords = [(geom.x, geom.y) for geom in grid_centroid.geometry]
# values = [] # Extract elevation values from the mosaic
# for x, y in coords:
#     row, col = rowcol(out_transform, x, y)
#     values.append(mosaic[0, row, col])
# grid_centroid_alti["elevation"] = values # Obtain the elevation for each centroid of the squares

# ########

#grid_centroid_alti = grid_centroid_alti.drop(columns = ["geometry"]) # remove the geometry before the merge to only keep one
grid_centroid_alti = grid_centroid_alti[["square_id",'sq_id_2X',"elevation"]]

grid = grid.merge(grid_centroid_alti, on=["square_id",'sq_id_2X'],how="left") #Inserting the value of elevation into the main data file

grid.to_file(f"data_output/grid_square_{name_territory}.shp")

# %%%%%%%%%%%%%%%%
# OLD Script

# grid["F_fermee"] = grid["F_fermee"].fillna(0)
# grid["F_ouvert"] = grid["F_ouvert"].fillna(0)
# grid["Peupleraie"] = grid["Peupleraie"].fillna(0)
# grid["vege_bas"] = grid["vege_bas"].fillna(0)

# #Occupation du sol BD TOPO
# # occupation_sol = pd.concat([occupation_sol_13, occupation_sol_83], ignore_index=True)
# # occupation_sol = gpd.clip(occupation_sol, territory_L93)
# # occupation_sol = occupation_sol.dissolve(by="NATURE")
# # #vegetal.to_file("data_output/vegetation.shp")

# # grid_centroid_bdtopo = gpd.sjoin(grid_centroid, occupation_sol, predicate="intersects")
# # print(grid_centroid_bdtopo.columns)
# # grid_centroid_bdtopo = grid_centroid_bdtopo.drop(columns = ["nb_photo","geometry","ID","DATE_CREAT","DATE_MAJ","DATE_APP","DATE_CONF","PREC_PLANI","SOURCE","ID_SOURCE"])
# # grid_centroid_bdtopo = grid_centroid_bdtopo.rename(columns ={
# #     "NATURE": "Nat_BDtp"
# # })
# # grid = grid.merge(grid_centroid_bdtopo, on=["square_id"],how="left")

# # Ajout végétation dans les 400 mètres autour soit 0.9 km²

# def compute_mean_1km(square_id,col):
#     ids_voisins = (
#         list(range(square_id - 1308, square_id - 1301))+
#         list(range(square_id - 873, square_id - 866))+
#         list(range(square_id - 438, square_id - 431))+
#         list(range(square_id - 3, square_id + 4)) +
#         list(range(square_id + 432, square_id + 439))+
#         list(range(square_id + 867, square_id + 874))+
#         list(range(square_id + 1302, square_id + 1309))
#     )
#     voisins = grid[grid["square_id"].isin(ids_voisins)]
#     return voisins[col].mean()

# cols = ["F_fermee", "F_ouvert", "Peupleraie", "vege_bas"]
# nom_sorti = ["F_fer","F_ouv","peup","veg"]
# for col, nom in zip(cols, nom_sorti):
#     grid[nom+"_1km"] = grid["square_id"].apply(
#         lambda x: compute_mean_1km(x, col)
#     )
