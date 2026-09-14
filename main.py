import subprocess
import os
import script_part1
import script_part2 #Run script_part2
import lidar
import script_access #Run script_access

env = os.environ.copy()
env["R_LIBS_USER"] = "/local/AIX/rgrandmaiso/R/x86_64-pc-linux-gnu-library/4.5"

liste_PNR = ["Parc de la Sainte-Baume","Parc du Luberon","PNR Baronnies provencales","Parc des Alpilles","Parc du Mont-Ventoux","Parc du Queyras","Parc du Verdon","Parc des Monts d'Ardeche","Parc de Corse"]

square_size = 1000  # size of square border (in meters)

for i in liste_PNR :
    print(i," : début")
    name_territory_full = i
    
    script_part1.main(name_territory_full,square_size)
    result = subprocess.run(
        ["/usr/bin/Rscript", "itinerary_grid_to_town.R",name_territory_full],
        capture_output=True,
        text=True,
        env=env,
        check=True
    )

    grid = script_part2.main(name_territory_full)
    grid_lidar = lidar.main(name_territory_full,grid)
    script_access.main(name_territory_full,grid_lidar,square_size)

    result2 = subprocess.run(
        ["/usr/bin/Rscript", "itinerary_grid_to_pop.R",name_territory_full],
        capture_output=True,
        text=True,
        env=env,
        check=True
    )
    print(name_territory_full," : traitement fait")
