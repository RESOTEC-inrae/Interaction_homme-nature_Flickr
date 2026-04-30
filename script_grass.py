
import grass.script as gs
import grass.script.setup as gsetup

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#Lancer le script à partir du terminal "Grass"==> python script_grass.py
# g.mapset → changer de LOCATION
# vérifier avec g.gisenv
# relancer ton script

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# gs.create_location(
#     dbase="C:/Users/rgrandmaiso/Documents/grassdata",
#     location="lambert93",
#     epsg=2154
# )

gsetup.init(
    "C:/Users/rgrandmaiso/Documents/grassdata",
    "lambert93",
    "PERMANENT"
)

# gs.run_command("v.in.ogr", input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_marche.shp", output="edges", overwrite=True)
# gs.run_command("v.in.ogr", input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/season.shp", output="grid", overwrite=True)

# gs.run_command("v.clean",input="edges",output="edges_clean",tool="snap,break",threshold=10,overwrite=True)

# gs.run_command("v.db.addcolumn",map="grid",columns="x double precision")
# gs.run_command("v.db.addcolumn",map="grid",columns="y double precision")
# gs.run_command("v.distance",from_="grid",to="edges_clean",output="connections",dmax=10000,upload="to_x,to_y",column="x,y", overwrite=True)
#gs.run_command("v.split",input="edges_clean",points="connections",output="edges_split",overwrite=True)
gs.run_command("v.overlay",ainput="edges_clean",binput="connections",operator="and",output="edges_split",overwrite=True)
#gs.run_command("v.distance",from_="grid",to="edges_clean",output="connections",dmax=10000,upload="dist",column="square_id", overwrite=True)
gs.run_command("v.net",input="edges_split",points="grid",operation="connect",output="network_connected",threshold=10,arc_type = 'line',overwrite=True)

gs.run_command("v.patch",input="network_split,connections",output="reseau_complet",overwrite=True)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Add length to the information of the network
gs.run_command("v.clean",input="reseau_complet",output="reseau_clean",tool="rmdupl",overwrite=True)
gs.run_command("v.db.addtable",map="reseau_clean",overwrite=True)
gs.run_command("v.db.addcolumn",map="reseau_clean",columns="length double precision",overwrite=True)
gs.run_command("v.to.db",map="reseau_clean",option="length",columns="length",units="meters",overwrite=True)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


#--- 1. Import des données ---
# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_marche.shp",output="edges",overwrite=True)
# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/season.shp",output="grid",overwrite=True)
# # --- 2. Nettoyage du réseau ---
# gs.run_command("v.clean",input="edges",output="edges_clean",tool="snap,break",threshold=10,overwrite=True)
# # --- 3. Projection des points sur le réseau (points de découpe) ---
# # gs.run_command("v.db.addcolumn",map="grid",columns="x double precision")
# gs.run_command("v.db.addcolumn",map="grid",columns="y double precision")
# # --- 4. Création des segments de connexion (grid → réseau) ---
# gs.run_command("v.distance",from_="grid",to="edges_clean",output="points_on_lines",dmax=10000,upload="to_x,to_y",column="x,y", overwrite=True)
#gs.run_command("v.distance",from_="grid",to="edges_clean",output="connections",dmax=10000,upload="to_x,to_y",column="x,y",overwrite=True)
# --- 5. Découpage du réseau aux points projetés ---
#gs.run_command("v.split",input="edges_clean",points="points_on_lines",output="edges_split",overwrite=True)
# gs.run_command("v.net",input="edges_clean",points="points_on_lines",output="network_split",operation="connect",threshold=1,overwrite=True)
# # --- 6. Fusion réseau + connexions ---
# #gs.run_command("v.patch",input="edges_split,connections",output="reseau_complet",overwrite=True)
# # --- 7. Nettoyage topologique final ---
# gs.run_command("v.clean",input="network_split",output="reseau_clean",tool="break,rmdupl",overwrite=True)
# # --- 8. Ajout des longueurs ---
# #gs.run_command("v.db.addtable",map="reseau_clean",overwrite=True)
# gs.run_command("v.db.addcolumn", map="reseau_clean", columns="length double precision",overwrite=True)
# gs.run_command("v.to.db",map="reseau_clean",option="length",columns="length",units="meters",overwrite=True)


gs.run_command("v.out.ogr", input="reseau_clean",type="line", output="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau.shp", format="ESRI_Shapefile",overwrite=True)
#gs.run_command("v.out.ogr", input="connections",type="point", output="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_point.shp", format="ESRI_Shapefile",overwrite=True)

