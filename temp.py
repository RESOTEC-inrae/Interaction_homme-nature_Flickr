import subprocess
import os

env = os.environ.copy()
env["R_LIBS_USER"] = "/local/AIX/rgrandmaiso/R/x86_64-pc-linux-gnu-library/4.5"

result = subprocess.run(
    ["/usr/bin/Rscript", "itinerary_grid_to_town.R"],
    capture_output=True,
    text=True,
    env=env
)


result2 = subprocess.run(
    ["/usr/bin/Rscript", "itinerary_grid_to_pop.R"],
    capture_output=True,
    text=True,
    env=env
)

# print("Code retour :", result2.returncode)
# print("STDOUT :")
# print(result2.stdout)
# print("STDERR :")
# print(result2.stderr) 