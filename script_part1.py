import geopandas as gpd
import pandas as pd
from shapely.geometry import box
import numpy as np
import osmnx as ox
import configuration 

# getting all necessary information for this script
def main(name_territory_full,square_size):
    (name_territory,photo,image_caracteristic,territory_L93,geom_union_territory,department_area,territory_city) = configuration.config(name_territory_full) 

#%%%%%%%%  Bd Foret V2 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Vegetation data that can be used with at least 1 park

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


    #%%%%%%%%  #BD TOPO  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Building data that can be used with at least 1 park
    building_04 = gpd.read_file("data_input/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D004_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D004-ED2024-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_05 = gpd.read_file("data_input/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D005_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D005-ED2024-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_06 = gpd.read_file("data_input/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D006_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D006-ED2024-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_07 = gpd.read_file("data_input/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D007_2026-06-15/BDTOPO/1_DONNEES_LIVRAISON_2026-06-00412/BDT_3-5_SHP_LAMB93_D007_ED2026-06-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_13 = gpd.read_file("data_input/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D013_2022-03-15/BDTOPO/1_DONNEES_LIVRAISON_2022-03-00081/BDT_3-0_SHP_LAMB93_D013-ED2022-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_2A = gpd.read_file("data_input/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D02A_2026-06-15/BDTOPO/1_DONNEES_LIVRAISON_2026-06-00412/BDT_3-5_SHP_LAMB93_D02A_ED2026-06-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_2B = gpd.read_file("data_input/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D02B_2026-06-15/BDTOPO/1_DONNEES_LIVRAISON_2026-06-00412/BDT_3-5_SHP_LAMB93_D02B_ED2026-06-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_26 = gpd.read_file("data_input/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D026_2026-03-15/BDTOPO/1_DONNEES_LIVRAISON_2026-03-00141/BDT_3-5_SHP_LAMB93_D026_ED2026-03-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_43 = gpd.read_file("data_input/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D043_2026-06-15/BDTOPO/1_DONNEES_LIVRAISON_2026-06-00412/BDT_3-5_SHP_LAMB93_D043_ED2026-06-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_83 = gpd.read_file("data_input/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D083_2021-06-15/BDTOPO/1_DONNEES_LIVRAISON_2021-06-00164/BDT_3-0_SHP_LAMB93_D083-ED2021-06-15/BATI/BATIMENT.shp",datetime_as_string=True)
    building_84 = gpd.read_file("data_input/BDTOPO_3-4_TOUSTHEMES_SHP_LAMB93_D084_2025-03-15/BDTOPO/1_DONNEES_LIVRAISON_2025-03-00288/BDT_3-4_SHP_LAMB93_D084_ED2025-03-15/BATI/BATIMENT.shp",datetime_as_string=True)

    list_dep_building = [building_04,building_05,building_06,building_07,building_13,building_2A,building_2B,building_26,building_43,building_83,building_84]

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


    # #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Photo filtering to remove photos of urban areas
    territory_L93_buffer = territory_L93.geometry.iloc[0].buffer(5000) # Adding 5km around the park to better represent the urban area around the park
    building = gpd.clip(building, territory_L93_buffer) # Keeping only the building in or close to the park

    urban_area = building.buffer(250).union_all().buffer(-250) # Transforming the urban area into a single geometry, easier to manipulate
    urban_area_gdf = gpd.GeoDataFrame(
    geometry=[urban_area],
    crs=2154
    )

    # #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # # Determining urban center of each towns

    urban_area_city = gpd.overlay(urban_area_gdf, territory_city, how="intersection") # separating the urban area by towns boundaries
    urban_area_city = urban_area_city.explode(index_parts=False) # transform multipolygons into simple polygons
    largest_urban = (
        urban_area_city
        .assign(area=urban_area_city.area)
        .sort_values("area", ascending=False)
        .groupby("code_insee")
        .head(1)
    ) # Keep for each town (groupby) the largest urban area (sort_values and head)

    center_town = largest_urban.geometry.centroid # Create the centroid from this remaining geometry
    center_town.to_file(f"data_output/centre_ville_{name_territory}.shp") # Necessary to save for the itinerary calculation in "itinerary_grid_to_town"

    # #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # Counting the number of photo in each square for each season while removing photo without végétation (vegatation == 0)

    photo = photo.merge(image_caracteristic, left_on="ID", right_on="images", how="left")
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
    gdf_photo = gdf_photo.loc[~gdf_photo.geometry.intersects(urban_area_gdf.union_all())]
    gdf_photo = gdf_photo.to_crs(2154) # change the projection to match the rest of the script

    photo_interest = gdf_photo.loc[(gdf_photo["nature"] == 1) | (gdf_photo["leasure"] == 1)].copy()


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
    grid_photo_general = grid_photo_general.sort_values("Date_Taken").drop_duplicates(subset=["index_right", "Date","Owner_Name"]) # Take only one interaction per square for each hour and user

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
    counts_nature['nature']= (counts_nature["nat_autumn"]+ counts_nature["nat_spring"]+ counts_nature["nat_summer"]+ counts_nature["nat_winter"])
    grid = grid.join(counts_nature) # join the information on the main grid

    counts_leasure = counts_leasure.rename(columns={
        "nb_autumn": "leas_autum",
        "nb_spring": "leas_sprin",
        "nb_summer": "leas_sumer",
        "nb_winter": "leas_wint",
    }) # Renaiming the name to better reflect what the value show
    counts_leasure['leasure']= (counts_leasure["leas_autum"]+ counts_leasure["leas_sprin"]+ counts_leasure["leas_sumer"]+ counts_leasure["leas_wint"])
    grid = grid.join(counts_leasure) # join the information on the main grid

    grid = grid.fillna(0) # fill the empty one by 0

    cols = ["nb_spring", "nb_summer", "nb_autumn", "nb_winter","nat_autumn","nat_spring", "nat_summer","nat_winter","leas_autum", "leas_sprin", "leas_sumer","leas_wint","nature","leasure"]
    for col in cols:
        grid[col] = grid[col].astype(int) #transform into integer ==> transform numbers like 2.000000000000000 as 2 for better visibility


    # #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # #Obtain walking OSM network and calculate the distance between the squares with the network
    territory_WGS84 = territory_L93.buffer(5000).to_crs(4326) #the geometry need to be in 4326 to be used with the library of osmnx
    study_area = territory_WGS84.geometry.iloc[0]


    G_walk = ox.graph_from_polygon(study_area, network_type="walk") # get all path where you can walk in the territory
    
    edges_G_Walk = ox.graph_to_gdfs(G_walk, nodes=False).to_crs(2154) # transform the network into a geodatabe, and make it come back to 2154
    edges_G_Walk.to_file(f"data_output/reseau_marche_{name_territory}.shp")

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

    # removing the columns not used
    dist = dist.drop(columns=["geometry",'u','v','key','osmid','maxspeed','est_width','access','junction','bridge','width','service','tunnel','highway','name','ref','oneway','reversed','length','lanes','index_right'],errors="ignore")
    
    dist = dist.drop_duplicates(subset="square_id") # remove the duplicate for each square

    #Obtain driving OSM network and calculate the distance between the squares and the network
    G_road = ox.graph_from_polygon(study_area, network_type="drive") # get all path where you can drive in the territory
    edges_G_Road = ox.graph_to_gdfs(G_road, nodes=False).to_crs(2154) # transform the network into a geodatabe, and make it come back to 2154


    dist_road = gpd.sjoin_nearest(
        grid_centroid,
        edges_G_Road,
        how='left',
        distance_col="dist_road"
        ) # Spatial join to estimate the distance (dist_path) between the network (driving) and the center of each square of the grid

    dist_road = dist_road.drop(columns=["geometry",'u','v','key','osmid','est_width','maxspeed','access','junction','bridge','width','service','tunnel','highway','name','ref','oneway','reversed','length','lanes',"index_right"],errors="ignore")
    # removing the columns not used
    dist_road = dist_road.drop_duplicates(subset="square_id") # remove the duplicate for each square

    grid = grid.merge(dist, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','leas_autum', 'leas_sprin', 'leas_sumer', 'leas_wint',"nature","leasure"]) #Inserting the distance to a pathway into the main data file
    grid = grid.merge(dist_road, on=["square_id",'sq_id_2X','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','leas_autum', 'leas_sprin', 'leas_sumer', 'leas_wint',"nature","leasure"]) #Inserting the distance to a roadway into the main data file

    grid.to_file(f"data_output/grid_script_part1_{name_territory}.shp")