
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


# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# # Version Final
# # Import
# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_marche.shp",output="edges",overwrite=True)
# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/season.shp",output="grid",overwrite=True)
# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/centre_ville.shp",output="city_center",overwrite=True)

# # Nettoyage réseau
# gs.run_command("v.clean", input="edges", output="edges_clean",tool="snap,break", threshold=10, overwrite=True)

# #Création des connexions
# gs.run_command("v.db.addcolumn",map="grid",columns="dist double precision")
# gs.run_command("v.db.addcolumn",map="city_center",columns="dist double precision")
# gs.run_command("v.distance",from_="city_center",to="edges_clean",output="connections_center",dmax=10000,upload="dist",column="dist",overwrite=True)

# # Fusion réseau + connexions
# gs.run_command("v.patch",input="edges_clean,connections_grid", output="connections",overwrite=True)
# gs.run_command("v.patch",input="connections,connections_center",output="network_all",overwrite=True)

# # # Nettoyage final
# gs.run_command("v.clean",input="network_all",output="reseau_clean",tool="rmdupl,break",overwrite=True)

# #Add length to the information of the network
# gs.run_command("v.db.addtable",map="reseau_clean",overwrite=True)
# gs.run_command("v.db.addcolumn",map="reseau_clean",columns="length double precision",overwrite=True)
# gs.run_command("v.to.db",map="reseau_clean",option="length",columns="length",units="meters",overwrite=True)

gs.run_command("v.out.ogr", input="reseau_clean",type="line", output="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau.shp", format="ESRI_Shapefile",overwrite=True)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# calcul des itinéraire

# gs.run_command("v.net",input="reseau_clean",points="city_center",operation="connect",output="reseau_final_1",threshold=100,overwrite=True)
# gs.run_command("v.net",input="reseau_final_1",points="grid",operation="connect",output="reseau_final_2",threshold=100,overwrite=True)
# print(gs.read_command("v.category",input="reseau_final_2",option="report"))
# gs.run_command("v.net.distance", input="reseau_final_2", output="reseau_final", flayer="1", to_layer="2",overwrite=True)



# gs.run_command("v.net",input="reseau_clean",points="city_center",operation="connect",output="reseau_final_1",arc_layer=1,node_layer=2,threshold=100,overwrite=True)
# gs.run_command("v.net",input="reseau_final_1",points="grid",operation="connect",output="reseau_final_2",arc_layer=1,node_layer=3,threshold=100,overwrite=True)
# gs.run_command("v.category",input="reseau_final_2",option="add",layer=3,output="reseau_final_3",overwrite=True)
# print(gs.read_command("v.category",input="reseau_final_2",option="report"))
# gs.run_command("v.net.distance",input="reseau_final_2",from_layer=3,to_layer=2,output="reseau_final",overwrite=True)

gs.run_command("v.net", input="reseau_clean", points="city_center", output="reseau_final_1", operation="connect", threshold=50.0, arc_layer=1, node_layer=2, overwrite = True)
gs.run_command("v.net", input="reseau_final_1", points="grid", output="reseau_final_2", operation="connect", threshold=50.0, arc_layer=1, node_layer=3, overwrite = True)
gs.run_command("v.db.connect", map="reseau_final_2", table="city_center", layer=2)
gs.run_command("v.db.connect", map="reseau_final_2", table="grid", layer=3)
gs.run_command("v.net.distance", input="reseau_final_2", arc_type="line", to_type="point", from_layer="2", to_layer="3", output="reseau_final", overwrite = True)

gs.run_command("v.out.ogr", input="reseau_final",type="line", output="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_distance.shp", format="ESRI_Shapefile",overwrite=True)

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# # gs.run_command("v.in.ogr", input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_marche.shp", output="edges", overwrite=True)
# # gs.run_command("v.in.ogr", input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/season.shp", output="grid", overwrite=True)

# # gs.run_command("v.clean",input="edges",output="edges_clean",tool="snap,break",threshold=10,overwrite=True)

# # gs.run_command("v.db.addcolumn",map="grid",columns="x double precision")
# # gs.run_command("v.db.addcolumn",map="grid",columns="y double precision")
# # gs.run_command("v.distance",from_="grid",to="edges_clean",output="connections",dmax=10000,upload="to_x,to_y",column="x,y", overwrite=True)
# #gs.run_command("v.split",input="edges_clean",points="connections",output="edges_split",overwrite=True)
# gs.run_command("v.overlay",ainput="edges_clean",binput="connections",operator="and",output="edges_split",overwrite=True)
# #gs.run_command("v.distance",from_="grid",to="edges_clean",output="connections",dmax=10000,upload="dist",column="square_id", overwrite=True)
# gs.run_command("v.net",input="edges_split",points="grid",operation="connect",output="network_connected",threshold=10,arc_type = 'line',overwrite=True)

# gs.run_command("v.patch",input="network_split,connections",output="reseau_complet",overwrite=True)

# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# #Add length to the information of the network
# gs.run_command("v.clean",input="reseau_complet",output="reseau_clean",tool="rmdupl",overwrite=True)
# gs.run_command("v.db.addtable",map="reseau_clean",overwrite=True)
# gs.run_command("v.db.addcolumn",map="reseau_clean",columns="length double precision",overwrite=True)
# gs.run_command("v.to.db",map="reseau_clean",option="length",columns="length",units="meters",overwrite=True)
# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/reseau_marche.shp",output="edges",overwrite=True)
# gs.run_command("v.in.ogr",input="C:/Users/rgrandmaiso/Documents/Flickr_vegetation_Roland/data_output/season.shp",output="grid",overwrite=True)
# gs.run_command("v.clean",input="edges",output="edges_clean",tool="snap,break",threshold=10,overwrite=True)
# gs.run_command("v.db.addcolumn",map="grid",columns="x double precision")
# gs.run_command("v.db.addcolumn",map="grid",columns="y double precision")
# gs.run_command("v.distance",from_="grid",to="edges_clean",output="connections",dmax=10000,upload="to_x,to_y",column="x,y",overwrite=True)





