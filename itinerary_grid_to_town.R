library(FNN)
library(ggplot2)
library(sf)
library(dodgr)
library(reticulate)

use_python("/usr/bin/python3", required = TRUE)
args <- commandArgs(trailingOnly = TRUE)
name_territory_full <- args[1]
source_python("configuration.py")
name_territory = name(name_territory_full)

# -----------------------------
# Reading files
# -----------------------------
network <- st_read(paste0("data_output/reseau_marche_",name_territory,".shp")) # Network
from <- st_read(paste0("data_output/grid_script_part1_",name_territory,".shp")) # Grid 
to <- st_read(paste0("data_output/centre_ville_",name_territory,".shp")) # Center of towns

# -----------------------------
# Graph construction
# -----------------------------
network$dist_m <- as.numeric(st_length(network))
graph <- weight_streetnet(network,wt_profile = "foot")

# -----------------------------
# Keeping only the main composant
# -----------------------------
comp <- dodgr_components(graph)
main_comp <- as.integer(names(which.max(table(comp$component))))
graph_main <- graph[graph$component == main_comp,]

# -----------------------------
# Filtered graph's peaks
# -----------------------------
vertices <- dodgr_vertices(graph_main)

# -----------------------------
# Associate centroides to the network
# -----------------------------

from_centroid <- st_centroid(from)
from_xy <- st_coordinates(from_centroid)
nearest_grid <- get.knnx(data = vertices[, c("x", "y")],query = from_xy,k = 1)
from_id <- vertices$id[nearest_grid$nn.index[,1]]

# -----------------------------
# Destinations
# -----------------------------

to_xy <- st_coordinates(to)

nearest_town <- get.knnx(data = vertices[, c("x", "y")],query = to_xy,k = 1)
to_id <- unique(vertices$id[nearest_town$nn.index[,1]])

# -----------------------------
# Minimal distance Calcul
# -----------------------------

distances <- c()

for(i in seq(1, length(from_id), by = 200)) {
  ids_bloc <- from_id[i:min(i + 199, length(from_id))]
  cat("Processing :", i,"from", min(i + 199, length(from_id)),"to", length(from_id), "\n")
  d <- dodgr_dists(graph_main,from = ids_bloc,to = to_id)
  # distance minimale
  dmin <- apply(d,1,function(x) {x <- x[is.finite(x)]
      if(length(x) == 0) {
        return(NA)
      } else {
        return(min(x))
      }
    }
  )
  distances <- c(distances,as.numeric(dmin))
  gc()
}

# -----------------------------
# Adding the information of distance in the file
# -----------------------------
from$dist_town <- distances

st_write(from,paste0("data_output/distance_town_",name_territory,".shp"),append = FALSE,delete_layer = TRUE)
