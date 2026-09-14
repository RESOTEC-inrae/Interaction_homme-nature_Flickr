import geopandas as gpd
import pandas as pd
from shapely.geometry import box
import numpy as np
import rasterio
from rasterio.merge import merge
from pathlib import Path
import configuration 



def main(name_territory_full):
    (name_territory,photo,image_caracteristic,territory_L93,geom_union_territory,department_area,territory_city) = configuration.config(name_territory_full)
    # #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    list_dep_vegetal = {
        "04": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D004_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D004/FORMATION_VEGETALE.shp"),
        "05": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D005_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D005/FORMATION_VEGETALE.shp"),
        "06": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D006_2021-03-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D006/FORMATION_VEGETALE.shp"),
        "07": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D007_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D007/FORMATION_VEGETALE.shp"),
        "13": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D013_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D013/FORMATION_VEGETALE.shp"),
        "2A": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D02A_2017-05-10/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D02A/FORMATION_VEGETALE.shp"),
        "2B": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D02B_2016-02-16/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D02B/FORMATION_VEGETALE.shp"),
        "26": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D026_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D026/FORMATION_VEGETALE.shp"),
        "43": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D043_2021-11-15/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D043/FORMATION_VEGETALE.shp"),
        "83": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D083_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D083/FORMATION_VEGETALE.shp"),
        "84": gpd.read_file("data_input/BDFORET_2-0__SHP_LAMB93_D084_2022-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D084/FORMATION_VEGETALE.shp")  
    }
    
    list_vegetal = []
    liste_dep=[] # Department position (ex: vegetal_04 = 0, vegetal_06 = 2)
    j=0

    for code_dep, i in list_dep_vegetal.items():
        bbox = box(*i.total_bounds)
        if bbox.intersects(geom_union_territory):
            # Option to remove the vegetation that crosses over into another department to avoid inaccuracies
            # department = department_area[department_area["code_insee"].astype(str).str.startswith(code_dep)]
            # i = gpd.clip(i, department)
            list_vegetal.append(i) # Keeping only the important departments for the park in question
            liste_dep.append(j) # Keeping the position of the important departments 
        j=j+1
    vegetal = pd.concat(list_vegetal,ignore_index=True)  # fusionning the data from the remaining department 
    vegetal["geometry"] = vegetal.geometry.make_valid() # solve some geometries that are wrong

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

    #Adding distance obtained with the R Script R
    grid = gpd.read_file(f"data_output/grid_script_part1_{name_territory}.shp")
    dist_town = gpd.read_file(f"data_output/distance_town_{name_territory}.shp")
    dist_town= dist_town.drop (columns=['geometry','nb_spring','nb_summer','nb_winter','nb_autumn','nat_autumn', 'nat_spring', 'nat_summer', 'nat_winter','leas_autum', 'leas_sprin', 'leas_sumer', 'leas_wint',"nature","leasure",'dist_path','dist_road'])
    dist_town[["sq_id_2X", "square_id"]] = dist_town[["sq_id_2X", "square_id"]].astype(int)

    grid = grid.merge(dist_town, on=["square_id",'sq_id_2X',],how="left")
   
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # Forest coverage integration
    vegetal = gpd.clip(vegetal, territory_L93) #keep only the data present in the parc

    modifications = {
        "Forêt fermée sans couvert arboré": "Ffer_sansA",
        "Forêt fermée feuillus": "Ffer_F",
        "Forêt fermée conifères": "Ffer_C",
        "Forêt fermée mixte": "Ffer_M",
        "Forêt ouverte sans couvert arboré": "Fouv_sansA",
        "Forêt ouverte feuillus": "Fouv_F",
        "Forêt ouverte conifères": "Fouv_C",
        "Forêt ouverte mixte": "Fouv_M",
        "Peupleraie": "Peupleraie",
        "Lande": "vege_bas",
        "Formation herbacée": "vege_bas",
    } 
    vegetal["TFV_G11"] = vegetal["TFV_G11"].replace(modifications) # we rename and regroup the categories when they are quite similar (in term of density)
    
    vegetal["geometry"] = vegetal.buffer(0) # removing strange geometries
    vegetal = vegetal.dissolve(by="TFV_G11").reset_index() # fusion of the same value of all polygons in the study area0

    vegetal.to_file("data_output/vegetation.shp")
    
    # #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
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
    if "Fouv_sansA" not in grid.columns:
        grid["Fouv_sansA"] = 0

    #Transform the value into percentages in order to better understand the details
    grid["Ffer_sansA"] = (grid["Ffer_sansA"]/grid["area_cell"]*100).fillna(0)
    grid["Ffer_F"] = (grid["Ffer_F"]/grid["area_cell"]*100).fillna(0)
    grid["Ffer_C"] = (grid["Ffer_C"]/grid["area_cell"]*100).fillna(0)
    grid["Ffer_M"] = (grid["Ffer_M"]/grid["area_cell"]*100).fillna(0)
    grid["Fouv_sansA"] = (grid["Fouv_sansA"]/grid["area_cell"]*100).fillna(0)
    grid["Fouv_F"] = (grid["Fouv_F"]/grid["area_cell"]*100).fillna(0)
    grid["Fouv_C"] = (grid["Fouv_C"]/grid["area_cell"]*100).fillna(0)
    grid["Fouv_M"] = (grid["Fouv_M"]/grid["area_cell"]*100).fillna(0)
    grid["Peupleraie"] = (grid["Peupleraie"]/grid["area_cell"]*100).fillna(0)
    grid["vege_bas"] = (grid["vege_bas"]/grid["area_cell"]*100).fillna(0)


    vegetal_uni = vegetal[["geometry"]].dissolve()
    intersections = grid.geometry.intersection(vegetal_uni.geometry.iloc[0])

    # precise information of area without forest
    grid["sans_foret"] = 100 - (intersections.area / grid["area_cell"] * 100)

    grid_vegetation = grid.copy()
    grid_vegetation["geometry"] = grid_vegetation.geometry.centroid.buffer(10000) # create a circle of 10km of radius for each square of the grid

    vegetal_inter = gpd.sjoin(grid,vegetal[["geometry","TFV_G11"]],predicate="intersects",how="inner") # spatial intersection to cut the vegetation with the grid
    vegetal_inter["area"] = vegetal_inter.area # calculate the size of the new areas created by the line above

    surface_buffer = np.pi * 10000**2 #Calculate the area of each circle created before (πR²)

    grid_veg_stat = vegetal_inter.groupby(["square_id", "TFV_G11"])["area"].sum().reset_index() # Adding all polygon present with the same type of vegetation, here we add them together 
    grid_veg_stat["area"] = (grid_veg_stat["area"] / surface_buffer) * 100  # Obtain the proportion (%) of the vegetation in the circle

    # Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area
    grid_forest = grid_veg_stat.pivot(
        index="square_id",
        columns="TFV_G11",
        values="area"
    ).fillna(0) # Reshape the table so that each vegetation class in TFV_G11 (F_fermee, F_ouverte, Peupleraie, vege_bas) becomes a separate column containing the associated surface area


    grid_forest = grid_forest.rename(columns={
        "Ffer_sansA": "FFA_10km",
        "Ffer_F": "FFF_10km",
        "Ffer_C": "FFC_10km",
        "Ffer_M": "FFM_10km",
        "Fouv_sansA": "FOA_10km",
        "Fouv_F": "FOF_10km",
        "Fouv_C": "FOC_10km",
        "Fouv_M": "FOM_10km",
        "Peupleraie": "Peup10km",
        "vege_bas": "grass10km",
    }) # Renaiming the name to better reflect what the value show


    if "Peup10km" not in grid_forest.columns:
        grid["Peup10km"] = 0
    if "FOA_10km" not in grid_forest.columns:
        grid["FOA_10km"] = 0
    if "FOA_10km" not in grid_forest.columns:
            grid["FOA_10km"] = 0
    

    grid = grid.merge(grid_forest, on=["square_id"],how="left") #Inserting the value of vegetation into the main data file
    grid[["FFA_10km","FFF_10km","FFC_10km","FFM_10km","FOA_10km","FOF_10km","FOC_10km","FOM_10km","Peup10km","grass10km"]] = (
        grid[["FFA_10km","FFF_10km","FFC_10km","FFM_10km","FOA_10km","FOF_10km","FOC_10km","FOM_10km","Peup10km","grass10km"]].fillna(0)
    )

    grid.to_file(f"data_output/vegetation_cercle_{name_territory}.shp")

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

    ######### Version 1 : using a file as a intermediary

    # Create a static version of the result
    with rasterio.open("data_output/mnt.tif", "w",**metadonne_tif) as dest:
        dest.write(mosaic)
    with rasterio.open("data_output/mnt.tif") as src:
        coords = [(geom.x, geom.y) for geom in grid_centroid_alti.geometry]
        values = list(src.sample(coords))

    grid_centroid_alti["elevation"] = [val[0] for val in values] # Obtain the elevation for each centroid of the squares

    grid_centroid_alti.loc[grid_centroid_alti["elevation"] < 0, "elevation"] = 0

    # ########

    grid_centroid_alti = grid_centroid_alti[["square_id",'sq_id_2X',"elevation"]] #keeping only the interesting columns

    grid = grid.merge(grid_centroid_alti, on=["square_id",'sq_id_2X'],how="left") #Inserting the value of elevation into the main data file
    return grid
