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
from pathlib import Path


###Variable

square_size = 100  # size of square (in meters)
name_territory = "Sainte-Baume" # possible name = ["Sainte-Baume","Luberon","Baronnies provençales","Alpilles","Camargue","Mont-Ventoux","Queyras","Verdon"]

### Data reading

#donnée photo
photo = pd.read_csv("data_raw/Image/flickr_location_Sainte-Baume.csv")

#every field of study

parcs = gpd.read_file("data_raw/Parc/ref_parc_bdtopo_pnrpaca.geojson")
territory_L93 = parcs.loc[parcs["pnr_qgis"] == name_territory].to_crs(2154)
geom_union_territory = territory_L93.union_all()
territory_city = gpd.read_file("Data_raw/ADMIN-EXPRESS_4-0__GPKG_LAMB93_FXX_2025-05-12/ADMIN-EXPRESS/1_DONNEES_LIVRAISON_2025-05-00071/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12.gpkg",layer = "commune")

liste_dep=[] #Position des dep (ex: vegetal_04 = position 0)

#%%%%%%%%  Bd Foret  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

vegetal_04 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D004_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D004/FORMATION_VEGETALE.shp")
vegetal_05 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D005_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D005/FORMATION_VEGETALE.shp")
vegetal_06 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D006_2021-03-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D006/FORMATION_VEGETALE.shp")
vegetal_13 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D013_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D013/FORMATION_VEGETALE.shp")
vegetal_26 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D026_2014-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D026/FORMATION_VEGETALE.shp")
vegetal_83 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D083_2015-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D083/FORMATION_VEGETALE.shp")
vegetal_84 = gpd.read_file("data_raw/BDFORET_2-0__SHP_LAMB93_D084_2022-04-01/BDFORET/1_DONNEES_LIVRAISON/BDF_2-0_SHP_LAMB93_D084/FORMATION_VEGETALE.shp")
list_dep_vegetal = [vegetal_04,vegetal_05,vegetal_06,vegetal_13,vegetal_26,vegetal_83,vegetal_84]
list_vegetal = []
j=0
for i in list_dep_vegetal:
    bbox = box(*i.total_bounds)
    if bbox.intersects(geom_union_territory):
        list_vegetal.append(i)
        liste_dep.append(j)
    j=j+1
vegetal = pd.concat(list_vegetal,ignore_index=True)   

#%%%%%%%%  Bd Alti  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dtm04 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D004_2023-08-08/BDALTIV2/1_DONNEES_LIVRAISON_2023-08-00161/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D004")
dtm05 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D005_2021-08-04/BDALTIV2/1_DONNEES_LIVRAISON_2021-10-00008/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D005")
dtm06 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D006_2023-08-08/BDALTIV2/1_DONNEES_LIVRAISON_2023-08-00161/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D006")
dtm13 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D013_2022-07-29/BDALTIV2/1_DONNEES_LIVRAISON_2022-08-00118/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D013")
dtm26 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D026_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D026")
dtm83 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D083_2022-12-05/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D083")
dtm84 = Path("data_raw/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D084_2022-12-16/BDALTIV2/1_DONNEES_LIVRAISON_2023-01-00224/BDALTIV2_MNT_25M_ASC_LAMB93_IGN69_D084")
list_dep_dtm = [dtm04,dtm05,dtm06,dtm13,dtm26,dtm83,dtm84]


square = []
for folder in list_dep_dtm :
    for file in folder.iterdir():
        if file.suffix.lower() in [".asc", ".tif", ".tiff"]:
            with rasterio.open(file) as src:
                bounds = src.bounds
                raster_geom = box(*bounds)
                if raster_geom.intersects(geom_union_territory):
                    square.append(file)


#%%%%%%%%  #BD TOPO  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
building_04 = gpd.read_file("data_raw/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D004_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D004-ED2024-03-15/BATI/BATIMENT.shp")
building_05 = gpd.read_file("data_raw/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D005_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D005-ED2024-03-15/BATI/BATIMENT.shp")
building_06 = gpd.read_file("data_raw/BDTOPO_3-3_TOUSTHEMES_SHP_LAMB93_D006_2024-03-15/BDTOPO/1_DONNEES_LIVRAISON_2024-04-00042/BDT_3-3_SHP_LAMB93_D006-ED2024-03-15/BATI/BATIMENT.shp")
building_13 = gpd.read_file("data_raw/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D013_2022-03-15/BDTOPO/1_DONNEES_LIVRAISON_2022-03-00081/BDT_3-0_SHP_LAMB93_D013-ED2022-03-15/BATI/BATIMENT.shp")
building_26 = gpd.read_file("data_raw/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D026_2026-03-15/BDTOPO/1_DONNEES_LIVRAISON_2026-03-00141/BDT_3-5_SHP_LAMB93_D026_ED2026-03-15/BATI/BATIMENT.shp")
building_83 = gpd.read_file("data_raw/BDTOPO_3-0_TOUSTHEMES_SHP_LAMB93_D083_2021-06-15/BDTOPO/1_DONNEES_LIVRAISON_2021-06-00164/BDT_3-0_SHP_LAMB93_D083-ED2021-06-15/BATI/BATIMENT.shp")
building_84 = gpd.read_file("data_raw/BDTOPO_3-4_TOUSTHEMES_SHP_LAMB93_D084_2025-03-15/BDTOPO/1_DONNEES_LIVRAISON_2025-03-00288/BDT_3-4_SHP_LAMB93_D084_ED2025-03-15/BATI/BATIMENT.shp")

list_dep_building = [building_04,building_05,building_06,building_13,building_26,building_83,building_84]
list_building = []
for i in liste_dep:
    list_building.append(list_dep_building[i])
building = pd.concat(list_building,ignore_index=True)   

# ### Script #########################################

# # Création de la grid 

# geom = territory_L93.geometry.iloc[0]
# bounds = geom.bounds 

# xmin, ymin, xmax, ymax = bounds
# cols = int(np.ceil((xmax - xmin) / square_size))
# rows = int(np.ceil((ymax - ymin) / square_size))
# grid = []
# for i in range(rows):
#     for j in range(cols):
#         x0 = xmin + j * square_size
#         y0 = ymin + i * square_size
#         x1 = min(x0 + square_size, xmax)
#         y1 = min(y0 + square_size, ymax)
#         grid.append(box(x0, y0, x1, y1))

# grid = gpd.GeoDataFrame(geometry=grid, crs=territory_L93.crs)
# grid["square_id"] = range(len(grid))

# # creation of a id with a 2x2 square
# grid["sq_id_2X"] = [
#     (i // 2) * (cols // 2) + (j // 2)
#     for i in range(rows)
#     for j in range(cols)
# ]

# grid.to_file("data_output/blank_square.shp")

grid = gpd.read_file("data_output/blank_square.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# #Filtrage des photos pour enlever les photos des zones urbaines
# territory_L93_buffer = territory_L93.buffer(5000)
# building = gpd.clip(building, territory_L93_buffer)

# urban_area = building.buffer(150).union_all().buffer(-150)
# urban_area_gdf = gpd.GeoDataFrame(
#    geometry=[urban_area],
#    crs=2154
# )
# urban_area_gdf.to_file("data_output/urban_area.shp")
urban_area_gdf = gpd.read_file("data_output/urban_area.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# donnée des mairies
# urban_area_city = gpd.overlay(urban_area_gdf, territory_city, how="intersection")
# urban_area_city = urban_area_city.explode(index_parts=False)
# urban_area_city.to_file("data_output/temporaire_urbain.shp")

# largest_urban = (
#     urban_area_city
#     .assign(area=urban_area_city.area)
#     .sort_values("area", ascending=False)
#     .groupby("code_insee")
#     .head(1)
# )
# center_town = largest_urban.geometry.centroid
# center_town.to_file("data_output/centre_ville.shp")
center_town = gpd.read_file("data_output/centre_ville.shp")

############ ancienne version ==> utilisation des données OSM ==> townhalls = ox.features_from_polygon(paca,tags={'amenity': 'townhall'})
# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#Compte du nombre de photo dans chaque carreaux de la grid pour chaque saison

gdf_photo = gpd.GeoDataFrame(
    photo,
    geometry=gpd.points_from_xy(photo.Longitude, photo.Latitude),
    crs="EPSG:4326"
)
gdf_photo = gdf_photo.to_crs(2154)

# create a join between the photos and the urban area
photo_outside = gpd.sjoin(gdf_photo, urban_area_gdf, predicate="within", how="left")
# keep all photos that didn't find a correspondance with the urban area
photo_outside = photo_outside[photo_outside.index_right.isna()]
#photo_outside.to_file("data_output/photo_nature.shp")

def get_season_astronomical(date):
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

# photo_outside["Date_Taken"] = pd.to_datetime(
#     photo_outside["Date_Taken"],
#     format="mixed",
#     dayfirst=True)
# photo_outside["season"] = photo_outside["Date_Taken"].apply(get_season_astronomical)

# photo_outside = photo_outside.drop(columns=["index_right"], errors="ignore")
# grid = grid.drop(columns=["index_right"], errors="ignore")

# joined = gpd.sjoin(photo_outside, grid, predicate="within")
# joined["Date"] = joined["Date_Taken"].dt.round("h")
# joined = joined.sort_values("Date_Taken").drop_duplicates(subset=["index_right", "Date","Owner_Name"])
# ########### joined = joined.sort_values("Date_Taken").drop_duplicates(subset=["index_right", "Date"]) ##########  Another version if we can't know the user
# counts = joined.groupby(['index_right', 'season']).size().unstack(fill_value=0)
# grid = grid.join(counts)
# grid = grid.fillna(0)

# #transform into integer ==> transform numbers like 2.000000000000000 as 2 for better visibility
# cols = ["nb_spring", "nb_summer", "nb_autumn", "nb_winter"]
# for col in cols:
#     grid[col] = grid[col].astype(int)

# grid.to_file("data_output/season.shp")
# #grid = gpd.read_file("data_output/season.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# #Récupération des chemins et calcul de la distance des carrés au chemin
# territory_WGS84 = territory_L93.buffer(5000).to_crs(4326)
# zone_etude = territory_WGS84.geometry.iloc[0]
# G_walk = ox.graph_from_polygon(zone_etude, network_type="walk")
# edges_G_Walk = ox.graph_to_gdfs(G_walk, nodes=False).to_crs(2154)

# edges_G_Walk.to_file("data_output/reseau_marche.shp")

grid_centroid = gpd.GeoDataFrame(
    grid,
    geometry=grid.centroid,
    crs="EPSG:2154"
)

# dist = gpd.sjoin_nearest(
#     grid_centroid,
#     edges_G_Walk,
#     how='left',
#     distance_col="dist_path"
#     )
# dist = dist.drop(columns=["geometry",'u','v','key','osmid','maxspeed','access','junction','bridge','width','service','tunnel','highway','name','ref','oneway','reversed','length','lanes'])

# #Récupération des routes et calcul de la distance des carrés au routes
# G_road = ox.graph_from_polygon(zone_etude, network_type="drive")
# edges_G_Road = ox.graph_to_gdfs(G_road, nodes=False).to_crs(2154)


# dist_road = gpd.sjoin_nearest(
#     grid_centroid,
#     edges_G_Road,
#     how='left',
#     distance_col="dist_road"
#     )
# dist_road = dist_road.drop(columns=["geometry",'u','v','key','osmid','maxspeed','access','junction','bridge','width','service','tunnel','highway','name','ref','oneway','reversed','length','lanes'])



# gs.run_command(
#     "v.net",
#     input=edges_G_Walk,
#     points=grid_centroid,
#     output=dist_center_town,
#     operation="connect",
#     thresh=100
# )
# dist_center_town.to_file("data_output/exemple.shp")
# dist_center_town = gpd.sjoin_nearest(
#     grid_centroid,
#     center_town,
#     how='left',
#     distance_col="dist_town"
#     )

# grid = grid.merge(dist, on=["square_id",'nb_spring','nb_summer','nb_winter','nb_autumn'])
# grid = grid.merge(dist_road, on=["square_id",'nb_spring','nb_summer','nb_winter','nb_autumn'])
# dist_center_town = dist_center_town[['dist_town', "square_id",'nb_spring','nb_summer','nb_winter','nb_autumn']]
# grid = grid.merge(dist_center_town, on=["square_id",'nb_spring','nb_summer','nb_winter','nb_autumn'])
# grid = grid.drop_duplicates(subset="square_id")

# grid.to_file("data_output/distance_route_mairie.shp")

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# # #Intégration du couvert végétal dans ma grid (Vegetation au niveau du centroide, à améliorer potentiellement pour la végétation la plus présente dans le carré)
# vegetal = gpd.clip(vegetal, territory_L93)

# modifications = {
#     "Forêt fermée sans couvert arboré": "F_fermee",
#     "Forêt fermée feuillus": "F_fermee",
#     "Forêt fermée conifères": "F_fermee",
#     "Forêt fermée mixte": "F_fermee",
#     "Forêt ouverte sans couvert arboré": "F_ouvert",
#     "Forêt ouverte feuillus": "F_ouvert",
#     "Forêt ouverte conifères": "F_ouvert",
#     "Forêt ouverte mixte": "F_ouvert",
#     "Peupleraie": "Peupleraie",
#     "Lande": "vege_bas",
#     "Formation herbacée": "vege_bas",
# }
# vegetal["TFV_G11"] = vegetal["TFV_G11"].replace(modifications)

# vegetal = vegetal.dissolve(by="TFV_G11").reset_index()
# print("roreo")
# vegetal["geometry"] = vegetal.geometry.simplify(10)

# # vegetal.to_file("data_output/vegetation.shp")
vegetal = gpd.read_file("data_output/vegetation.shp")

# # ####################################################

# vegetal = gpd.overlay(vegetal, grid, how="intersection")
# vegetal["surface"] = vegetal.area
# grid_forest = vegetal.groupby(["square_id", "TFV_G11"])["surface"].sum().reset_index()

# grid_forest["surface"]=grid_forest["surface"]/100 #/10000 m²(surface)*100(%)

# grid_forest = grid_forest.pivot(
#     index="square_id",
#     columns="TFV_G11",
#     values="surface"
# ).fillna(0)
# grid = grid.merge(grid_forest, on=["square_id"],how="left")

# grid.to_file("data_output/square_vegetation.shp")
# grid = gpd.read_file("data_output/square_vegetation.shp")


# # ###############################################
# grid_vegetation = grid.copy()
# grid_vegetation["geometry"] = grid_vegetation.geometry.centroid.buffer(1000)
# print("rrrrrrrrrr")
# vegetal_inter = gpd.overlay(vegetal, grid_vegetation, how="intersection")
# vegetal_inter["surface"] = vegetal_inter.area
# print("eeeeeeeeee")
# surface_buffer = np.pi * 1000**2

# grid_veg_stat = vegetal_inter.groupby(
#     ["square_id", "TFV_G11"]
# )["surface"].sum().reset_index()
# grid_veg_stat["surface"] = (grid_veg_stat["surface"] / surface_buffer) * 100

# grid_forest = grid_veg_stat.pivot(
#     index="square_id",
#     columns="TFV_G11",
#     values="surface"
# ).fillna(0)

# grid_forest = grid_forest.rename(columns={
#     "F_fermee": "F_close1km",
#     "F_ouvert": "F_open_1km",
#     "Peupleraie": "Peup_1km",
#     "vege_bas": "grass_1km",

# })

# grid = grid.merge(grid_forest, on=["square_id"],how="left")

# grid.to_file("data_output/vegetation_cercle.shp")
grid = gpd.read_file("data_output/vegetation_cercle.shp")


##vegetal.to_file("data_output/vegetation.shp")



#   dtm

# mosaic, out_transform = merge(square)
# with rasterio.open(square[0]) as src:
#     metadonne_tif = src.meta.copy()
#     metadonne_tif.update({
#         "driver": "GTiff",
#         "height": mosaic.shape[1],
#         "width": mosaic.shape[2],
#         "transform": out_transform,
#         "crs": "EPSG:2154"
#     })

# grid_centroid_alti = grid_centroid.copy()

# with rasterio.open("data_output/mnt.tif", "w",**metadonne_tif) as dest:
#     dest.write(mosaic)
# with rasterio.open("data_output/mnt.tif") as src:
#     coords = [(geom.x, geom.y) for geom in grid_centroid_alti.geometry]
#     values = list(src.sample(coords))


# grid_centroid_alti["altitude"] = [val[0] for val in values]
# grid_centroid_alti = grid_centroid_alti.drop(columns = ["geometry"])
# grid = grid.merge(grid_centroid_alti, on=["square_id"],how="left")

# grid.to_file("data_output/altitude.shp")



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

if (name_territory == "Sainte-Baume"):
    print('fini')
    #grid.to_file("data_output/grille_carreaux_Sainte_Baume.shp")
elif (name_territory == "Luberon"):
    grid.to_file("data_output/grille_carreaux_Luberon.shp")
else :
    print("not done yet")


