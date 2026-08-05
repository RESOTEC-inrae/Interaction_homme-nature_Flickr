import pandas as pd
import geopandas as gpd
import re


name_territory_full = "Parc de la Sainte-Baume" # possible name = ["Parc de la Sainte-Baume","Parc du Luberon","PNR Baronnies provencales","Parc des Alpilles","Parc du Mont-Ventoux","Parc du Queyras","Parc du Verdon","Parc des Monts d'Ardeche","Parc de Corse"]
name_territory = re.sub(
    r"^(Parc de la |Parc des |Parcs des |Parc du |Parc de |PNR )",
    "",
    name_territory_full
)

photo = pd.read_csv(f"data_input/Image/{name_territory}.csv") #File where the informations about the photo are located
image_caracteristic = pd.read_csv(f"data_input/Image/inference_10sites.csv") # Sainte-Baume_inference.csv


#parcs = gpd.read_file("data_input/Parc/ref_parc_bdtopo_pnrpaca.geojson") #File containing all the boundaries of the regional parks in the region PACA
#territory_L93 = parcs.loc[parcs["pnr_qgis"] == name_territory].to_crs(2154) #Keeping only one park
parcs = gpd.read_file("data_input/Parc/pnr_polygonPolygon.shp")
territory_L93 = parcs.loc[parcs["short_name"] == name_territory_full].to_crs(2154) #Keeping only one park
geom_union_territory = territory_L93.union_all() #Cleaning up the file to remove errors
territory_city = gpd.read_file("data_input/ADMIN-EXPRESS_4-0__GPKG_LAMB93_FXX_2025-05-12/ADMIN-EXPRESS/1_DONNEES_LIVRAISON_2025-05-00071/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12/ADE_4-0_GPKG_LAMB93_FXX-ED2025-05-12.gpkg",
                               layer = "commune") # Administrative boundaries of towns and cities : Useful file to create center of the urban area
