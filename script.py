#pip install geopandas
#pip install osmnx
#pip install rasterio
#pip install shapely==2.1.2
import geopandas as gpd
import pandas as pd
import shapely as shp
from shapely.geometry import box, Polygon, MultiPolygon
import numpy as np
import osmnx as ox
import rasterio
from rasterio.merge import merge
#from rasterio.transform import rowcol
from pathlib import Path
import multiprocessing
from multiprocessing import Pool


###Variable

square_size = 1000  # size of square border (in meters)
name_territory = "Sainte-Baume" # possible name = ["Sainte-Baume","Luberon","Baronnies provençales","Alpilles","Camargue","Mont-Ventoux","Queyras","Verdon"]

### Data 

photo = pd.read_csv("data_input/Image/flickr_location_Sainte-Baume.csv") #File where the informations about the photo are located
image_caracteristic = pd.read_csv("data_input/Image/SainteBaume_inference.csv")
parcs = gpd.read_file("data_input/Parc/ref_parc_bdtopo_pnrpaca.geojson") #File containing all the boundaries of the regional parks in the region PACA
territory_L93 = parcs.loc[parcs["pnr_qgis"] == name_territory].to_crs(2154) #Keeping only one park
geom_union_territory = territory_L93.union_all() #Cleaning up the file to remove errors
territory_city = gpd.read_file("data_input/ADMIN-EXPRESS_4-0__GPKG_LAMB93_FXX_2025-05-12/ADMIN-EXPRESS/1_DONNEES_LIVRAISON_2025-05-00071/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12.gpkg",
                               layer = "commune") # Administrative boundaries of towns and cities : Useful file to create center of the urban area


#%%%%%%%%  Bd Foret  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Vegetation data that can be used with at least 1 park

vegetal_04 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D004_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D004/FORMATION_VEGETALE.shp")
vegetal_05 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D005_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D005/FORMATION_VEGETALE.shp")
vegetal_06 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D006_2021-03-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D006/FORMATION_VEGETALE.shp")
vegetal_13 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D013_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D013/FORMATION_VEGETALE.shp")
vegetal_26 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D026_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D026/FORMATION_VEGETALE.shp")
vegetal_83 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D083_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D083/FORMATION_VEGETALE.shp")
vegetal_84 = gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D084_2022-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D084/FORMATION_VEGETALE.shp")
list_dep_vegetal = [vegetal_04,vegetal_05,vegetal_06,vegetal_13,vegetal_26,vegetal_83,vegetal_84] # General territory of study
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

#%%%%%%%%  Bd Alti  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Elevation data that can be used with at least 1 park

dtm04 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D004_2023-08-08/BDALTIV2/1_DONNEES_LIVRAISON_2023-08-00161/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D004")
dtm05 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D005_2021-08-04/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D005")
dtm06 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D006_2023-08-08/BDALTIV2/1_DONNEES_LIVRAISON_2023-08-00161/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D006")
dtm13 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D013_2022-07-29/BDALTIV2/1_DONNEES_LIVRAISON_2022-08-00118/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D013")
dtm26 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D026_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D026")
dtm83 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D083_2022-12-05/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D083")
dtm84 = Path("data_input/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D084_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D084")
list_dep_dtm = [dtm04,dtm05,dtm06,dtm13,dtm26,dtm83,dtm84]  # General territory of study


square = [] # variable with all the tiles that overlaps with the park of study
for folder in list_dep_dtm :
    for file in folder.iterdir(): # see all file in the directories stored in list_dep_dtm
        if file.suffix.lower() in [".asc", ".tif", ".tiff"]: # keeping only file that are useful for a DEM file
            with rasterio.open(file) as src:
                bounds = src.bounds 
                raster_geom = box(*bounds)
                if raster_geom.intersects(geom_union_territory): # Check if the tile is overlapping the field of study 
                    square.append(file) 


#%%%%%%%%  #BD TOPO  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Building data that can be used with at least 1 park
building_04 = gpd.read_file("data_input/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D004_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D004-ED2024-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
building_05 = gpd.read_file("data_input/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D005_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D005-ED2024-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
building_06 = gpd.read_file("data_input/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D006_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D006-ED2024-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
building_13 = gpd.read_file("data_input/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D013_2022-03-15/BDTOPO/1_DONNEES_LIVRAISON_2022-03-00081/BDT_3-0_SHP_LAMB93_D013-ED2022-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
building_26 = gpd.read_file("data_input/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D026_2026-03-15/BDTOPO/1_DONNEES_LIVRAISON_2026-03-00141/BDT_3-5_SHP_LAMB93_D026_ED2026-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
building_83 = gpd.read_file("data_input/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D083_2021-06-15/BDTOPO/1_DONNEES_LIVRAISON_2021-06-00164/BDT_3-0_SHP_LAMB93_D083-ED2021-06-15/BATI/BATIMENT.shp",datetime_as_string=True)
building_84 = gpd.read_file("data_input/BDTOPO_3-4_TOUSTHEMES_SHP_LAMB93_D084_2025-03-15/BDTOPO/1_DONNEES_LIVRAISON_2025-03-00288/BDT_3-4_SHP_LAMB93_D084_ED2025-03-15/BATI/BATIMENT.shp",datetime_as_string=True)

list_dep_building = [building_04,building_05,building_06,building_13,building_26,building_83,building_84]

list_building = []
for i in liste_dep: # liste_dep has kept only the department that overlaps with the field of study.
    list_building.append(list_dep_building[i])

building = pd.concat(list_building,ignore_index=True)   # fusionning the data from the remaining department 

### Script #########################################
# Grid Creation  
geom = territory_L93.geometry.iloc[0] #Keeping only the colomns geometry (.geometry) and adapting it in a readable value by python (.iloc[0])
bounds = geom.bounds #taking the broad boundaries
xmin, ymin, xmax, ymax = bounds
cols = int(np.ceil((xmax - xmin) / square_size)) #calculating the numbers of columns needed
rows = int(np.ceil((ymax - ymin) / square_size)) #calculating the numbers of lines needed
grid = []
for i in range(rows):
    for j in range(cols):
        x0 = xmin + j * square_size #finding the left of the square
        y0 = ymin + i * square_size #finding the bottom of the square
        x1 = min(x0 + square_size, xmax) #extrapolating the right of the square (until the limit)
        y1 = min(y0 + square_size, ymax) #extrapolating the top of the square (until the limit)
        grid.append(box(x0, y0, x1, y1)) #adding the new square to the exit result

grid = gpd.GeoDataFrame(geometry=grid, crs=territory_L93.crs) #transform the list of geometry in a single geometry


# creation of a id with a 2x2 square
sq_ids = []
for i in range(rows):
    for j in range(cols):
        block_row = i // 2 # Ligne du bloc 2x2
        block_col = j // 2 # Colonne du bloc 2x2
        blocks_per_row = cols // 2 # Nombre de blocs par ligne
        square_id = block_row * blocks_per_row + block_col # Identifiant unique du bloc
        sq_ids.append(square_id)
grid["sq_id_2X"] = sq_ids

grid = gpd.clip(grid, territory_L93) 
grid["square_id"] = range(len(grid)) # create a unique ID
grid.to_file("data_output/blank_square.shp")

grid = gpd.read_file("data_output/blank_square.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Photo filtering to remove photos of urban areas
# territory_L93_buffer = territory_L93.buffer(5000) # Adding 5km around the park to better represent the urban area around the park
# building = gpd.clip(building, territory_L93_buffer) # Keeping only the building in or close to the park

# urban_area = building.buffer(150).union_all().buffer(-150) # Transforming the urban area into a single geometry, easier to manipulate
# urban_area_gdf = gpd.GeoDataFrame(
#    geometry=[urban_area],
#    crs=2154
# )
# urban_area_gdf.to_file("data_output/urban_area.shp")
urban_area_gdf = gpd.read_file("data_output/urban_area.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# # Determining urban center of each towns

# urban_area_city = gpd.overlay(urban_area_gdf, territory_city, how="intersection") # separating the urban area by towns boundaries
# urban_area_city = urban_area_city.explode(index_parts=False) # transform multipolygons into simple polygons
# # urban_area_city.to_file("data_output/temporaire_urbain.shp")

# largest_urban = (
#     urban_area_city
#     .assign(area=urban_area_city.area)
#     .sort_values("area", ascending=False)
#     .groupby("code_insee")
#     .head(1)
# ) # Keep for each town (groupby) the largest urban area (sort_values and head)

# center_town = largest_urban.geometry.centroid # Create the centroid from this remaining geometry
# center_town.to_file("data_output/centre_ville.shp")
#center_town = gpd.read_file("data_output/centre_ville.shp")

############ ancienne version ==> utilisation des données OSM ==> townhalls = ox.features_from_polygon(paca,tags={'amenity': 'townhall'})
# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Counting the number of photo in each square for each season

photo = photo.merge(image_caracteristic, left_on="ID", right_on="image", how="left")
photo["nature"] = (
    (photo["human"] != 1) &
    (photo["vegetation"] == 1)
).astype(int)
photo["leasure"] = (
    (photo["human"] == 1) &
    (photo["vegetation"] == 1)
).astype(int)

gdf_photo = gpd.GeoDataFrame(
    photo,
    geometry=gpd.points_from_xy(photo.Longitude, photo.Latitude),
    crs="EPSG:4326"
) # Transforming the photo information into geographical data
gdf_photo = gdf_photo.to_crs(2154) # change the projection to match the rest of the script

photo_interest = gdf_photo.loc[(gdf_photo["nature"] == 1) | (gdf_photo["leasure"] == 1)].copy()

# # #%%%%%%%%%%% Version sans filtre IA
# # # create a join between the photos and the urban area
# # photo_outside = gpd.sjoin(gdf_photo, urban_area_gdf, predicate="within", how="left")
# # # keep all photos that didn't find a correspondance with the urban area
# # photo_outside = photo_outside[photo_outside.index_right.isna()]
# # # photo_outside.to_file("data_output/photo_nature.shp")
# # #%%%%%%%%%%%

def get_season_astronomical(date): # function that determine which season the photo has been taken
    year = date.year
    spring = pd.Timestamp(year=year, month=3, day=20)
    summer = pd.Timestamp(year=year, month=6, day=21)
    autumn = pd.Timestamp(year=year, month=9, day=23)
    winter = pd.Timestamp(year=year, month=12, day=21)
    if spring <= date < summer:
        return "nb_spring"
    elif summer <= date < autumn:
        return "nb_summer"
    elif autumn <= date < winter:
        return "nb_autumn"
    else:
        return "nb_winter"

photo_interest["Date_Taken"] = pd.to_datetime(
    photo_interest["Date_Taken"],
    format="mixed",
    dayfirst=True) # transform the date in string into a date readable by the library panda. 
photo_interest["season"] = photo_interest["Date_Taken"].apply(get_season_astronomical) # call the function written above

photo_interest = photo_interest.drop(columns=["index_right"], errors="ignore") #remove columns that aren't useful if it exists (depend if we use directly from the start of the code or it read from a intermediate result)
grid = grid.drop(columns=["index_right"], errors="ignore") #remove columns that aren't useful (depend if we use directly from the start of the code or it read from a intermediate result)

grid_photo_general = gpd.sjoin(photo_interest, grid, predicate="within") #spatial join between the photo and the grid
grid_photo_general["Date"] = grid_photo_general["Date_Taken"].dt.round("h") # standardize date format like removing hour (date data from different devices can be different)
grid_photo_general = grid_photo_general.sort_values("Date_Taken").drop_duplicates(subset=["index_right", "Date","Owner_Name"]) # Take only one interaction per square for each day and user
# ########### grid_photo_general = grid_photo_general.sort_values("Date_Taken").drop_duplicates(subset=["index_right", "Date"]) ##########  Another version if we can't know the user

counts_photo = grid_photo_general.groupby(['index_right', 'season']).size().unstack(fill_value=0) #count the number of photo from each season per square and transform the value of season into columns from lines

grid = grid.join(counts_photo) # join the information on the main grid

counts_nature = grid_photo_general.loc[grid_photo_general["nature"] == 1].groupby(['index_right', 'season']).size().unstack(fill_value=0) #count the number of photo from each season per square and transform the value of season into columns from lines
counts_leasure = grid_photo_general.loc[grid_photo_general["leasure"] == 1].groupby(['index_right', 'season']).size().unstack(fill_value=0) #count the number of photo from each season per square and transform the value of season into columns from lines


counts_nature = counts_nature.rename(columns={
    "nb_autumn": "nat_autumn",
    "nb_spring": "nat_spring",
    "nb_summer": "nat_summer",
    "nb_winter": "nat_winter",
}) # Renaiming the name to better reflect what the value show
grid = grid.join(counts_nature) # join the information on the main grid

counts_leasure = counts_leasure.rename(columns={
    "nb_autumn": "hob_autumn",
    "nb_spring": "hob_spring",
    "nb_summer": "hob_summer",
    "nb_winter": "hob_winter",
}) # Renaiming the name to better reflect what the value show
grid = grid.join(counts_leasure) # join the information on the main grid

grid = grid.fillna(0) # fill the empty one by 0

cols = ["nb_spring", "nb_summer", "nb_autumn", "nb_winter","nat_autumn","nat_spring", "nat_summer","nat_winter","hob_autumn", "hob_spring", "hob_summer","hob_winter"]
for col in cols:
    grid[col] = grid[col].astype(int) #transform into integer ==> transform numbers like 2.000000000000000 as 2 for better visibility


grid.to_file("data_output/season.shp")

grid = gpd.read_file("data_output/season.shp")
# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# #Obtain walking OSM network and calculate the distance between the squares and the network
territory_WGS84 = territory_L93.buffer(5000).to_crs(4326) #the geometry need to be in 4326 to be used with the library of osmnx
study_area = territory_WGS84.geometry.iloc[0]

# G_walk = ox.graph_from_polygon(study_area, network_type="walk") # get all path where you can walk in the territory
# edges_G_Walk = ox.graph_to_gdfs(G_walk, nodes=False).to_crs(2154) # transform the network into a geodatabe, and make it come back to 2154
# edges_G_Walk.to_file("data_output/reseau_marche.shp")
edges_G_Walk = gpd.read_file("data_output/reseau_marche.shp")

grid_centroid = gpd.GeoDataFrame(
    grid,
    geometry=grid.centroid,
    crs="EPSG:2154"
)

dist = gpd.sjoin_nearest(
    grid_centroid,
    edges_G_Walk,
    how='left',
    distance_col="dist_path"
    ) # Spatial join to estimate the distance (dist_path) between the network (walking) and the center of each square of the grid

dist = dist.drop(columns=["geometry",'u','v','key','osmid','maxspeed','access','junction','bridge','width','service','tunnel','highway','name','ref','oneway','reversed','length','lanes'])
# removing the columns not used
dist = dist.drop_duplicates(subset="square_id") # remove the duplicate for each square
dist = dist.drop(columns=["index_right"], errors="ignore")


#Obtain driving OSM network and calculate the distance between the squares and the network

# G_road = ox.graph_from_polygon(study_area, network_type="drive") # get all path where you can drive in the territory
# edges_G_Road = ox.graph_to_gdfs(G_road, nodes=False).to_crs(2154) # transform the network into a geodatabe, and make it come back to 2154
# edges_G_Road.to_file("data_output/reseau_road.shp")

edges_G_Road = gpd.read_file("data_output/reseau_road.shp")

dist_road = gpd.sjoin_nearest(
    grid_centroid,
    edges_G_Road,
    how='left',
    distance_col="dist_road"
    ) # Spatial join to estimate the distance (dist_path) between the network (driving) and the center of each square of the grid
dist_road = dist_road.drop(columns=["geometry",'u','v','key','osmid','maxspeed','access','junction','bridge','width','service','tunnel','highway','name','ref','oneway','reversed','length','lanes'])
# removing the columns not used
dist_road = dist_road.drop_duplicates(subset="square_id") # remove the duplicate for each square
dist_road = dist_road.drop(columns=["index_right"], errors="ignore")

grid = grid.merge(dist, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','hob_autumn', 'hob_spring', 'hob_summer', 'hob_winter']) #Inserting the distance to a pathway into the main data file
grid = grid.merge(dist_road, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','hob_autumn', 'hob_spring', 'hob_summer', 'hob_winter']) #Inserting the distance to a roadway into the main data file
grid.to_file("data_output/distance_route_mairie.shp")
grid = gpd.read_file("data_output/distance_route_mairie.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# #GRASS Script which allow to know the distance between the squares and the town centers
# Doesn't work well

#Script R which allow to know the distance between the squares and the town centers
dist_town = gpd.read_file("data_output/distance_town.shp")
dist_town = dist_town.drop(columns='geometry')

grid = grid.merge(dist_town, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn'],how="left") #Inserting the distance to the city into the main data file

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

#Transform the value into percentages in order to better understand the details
grid["F_fermee"] = (grid["F_fermee"]/grid["area_cell"]*100).fillna(0)
grid["F_ouvert"] = (grid["F_ouvert"]/grid["area_cell"]*100).fillna(0)
grid["Peupleraie"] = (grid["Peupleraie"]/grid["area_cell"]*100).fillna(0)
grid["vege_bas"] = (grid["vege_bas"]/grid["area_cell"]*100).fillna(0)
grid = grid.drop(columns = "area_cell")

grid.to_file("data_output/square_vegetation.shp")
grid = gpd.read_file("data_output/square_vegetation.shp")

grid_vegetation = grid.copy()
grid_vegetation["geometry"] = grid_vegetation.geometry.centroid.buffer(1000) # create a circle of 1km of radius for each square of the grid

vegetal_inter = gpd.sjoin(grid,vegetal[["geometry","TFV_G11"]],predicate="intersects",how="inner") # spatial intersection to cut the vegetation with the grid
vegetal_inter["area"] = vegetal_inter.area # calculate the size of the new areas created by the line above

surface_buffer = np.pi * 1000**2 #Calculate the area of each circle created before (πR²)

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
    "F_fermee": "F_close1km",
    "F_ouvert": "F_open_1km",
    "Peupleraie": "Peup_1km",
    "vege_bas": "grass_1km",
}) # Renaiming the name to better reflect what the value show

grid = grid.merge(grid_forest, on=["square_id"],how="left") #Inserting the value of vegetation into the main data file
grid[["F_close1km", "F_open_1km", "Peup_1km", "grass_1km"]] = (
    grid[["F_close1km", "F_open_1km", "Peup_1km", "grass_1km"]].fillna(0)
)

grid.to_file("data_output/vegetation_cercle.shp")

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

# grid.to_file("data_output/vegetation_cercle.shp")
grid = gpd.read_file("data_output/vegetation_cercle.shp")
 
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

grid_centroid_alti = grid_centroid.copy() #The elevation chosen is the one at the center of the square

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

grid_centroid_alti = grid_centroid_alti.drop(columns = ["geometry"]) # remove the geometry before the merge to only keep one
 
grid = grid.merge(grid_centroid_alti, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','hob_autumn', 'hob_spring', 'hob_summer', 'hob_winter'],how="left") #Inserting the value of elevation into the main data file


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
