import subprocess
import os


env = os.environ.copy()
env["R_LIBS_USER"] = "/local/AIX/rgrandmaiso/R/x86_64-pc-linux-gnu-library/4.5"

import script_part1 #Run script_part1 

result = subprocess.run(
    ["/usr/bin/Rscript", "itinerary_grid_to_town.R"],
    capture_output=True,
    text=True,
    env=env
)
# print("rrrrrrrrrrrr")
# print(result.stderr)

import script_part2 #Run script_part2

import script_access #Run script_access

result2 = subprocess.run(
    ["/usr/bin/Rscript", "itinerary_grid_to_pop.R"],
    capture_output=True,
    text=True,
    env=env
)

# print("rrrrrrrrrrrr")
# print(result2.stderr)
