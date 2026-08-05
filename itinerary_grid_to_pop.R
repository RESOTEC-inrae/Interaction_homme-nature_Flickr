library(sf)
library(dodgr)
library(FNN)
library(ggplot2)

library(reticulate)
use_python("/usr/bin/python3", required = TRUE)
source_python("configuration.py")


# -----------------------------
# Lecture des données
# -----------------------------
#setwd("C:/Users/rgrandmaiso/Documents")
#name_territory_full = "Sainte-Baume" # possible name = ["Sainte-Baume","Luberon","Baronnies provençales","Alpilles","Camargue","Mont-Ventoux","Queyras","Verdon"]
network <- st_read(paste0("data_output/reseau_marche_",name_territory,".shp"))
from <- st_read(paste0("data_output/score_access_",name_territory,".shp"))
to <- st_read(paste0("data_output/pixels_population_",name_territory,".shp"))

# -----------------------------
# Construction du graphe
# -----------------------------
network$dist_m <- as.numeric(st_length(network))
graph <- weight_streetnet(network,wt_profile = "foot")
graph$d <- sqrt((graph$from_lon - graph$to_lon)^2 +(graph$from_lat - graph$to_lat)^2)
graph$d_weighted <- graph$d

# -----------------------------
# Garder uniquement
# la composante principale
# -----------------------------

comp <- dodgr_components(graph)
main_comp <- as.integer(names(which.max(table(comp$component))))
graph_main <- graph[graph$component == main_comp,]
#vertices_keep <- comp$id[comp$component == main_comp]
#graph_main <- graph[graph$from_id %in% vertices_keep & graph$to_id %in% vertices_keep,]

# -----------------------------
# Sommets du graphe filtré
# -----------------------------
vertices <- dodgr_vertices(graph_main)

# -----------------------------
# Associer les centroides
# au réseau
# -----------------------------

from_centroid <- st_centroid(from)
from_xy <- st_coordinates(from_centroid)
nearest_grid <- get.knnx(data = vertices[, c("x", "y")],query = from_xy[, c("X", "Y")],k = 1)

from_id <- data.frame(from_xy,id = vertices$id[nearest_grid$nn.index],distance = nearest_grid$nn.dist)
from_id$id <- seq_len(nrow(from_id))

# -----------------------------
# Destinations
# -----------------------------
centroids <- st_centroid(to)
to_xy <- st_coordinates(centroids)
nearest_town <- get.knnx(data = vertices[, c("x", "y")],query = to_xy[, c("X", "Y")], k = 1)

#to_id <- vertices$id[nearest_town$nn.index[,1]]
to_id <- data.frame(to_xy,id = vertices$id[nearest_town$nn.index],distance = nearest_town$nn.dist)
#to_id <- cbind(to_xy,vertices[nearest_town$nn.index, "n"],distance = nearest_town$nn.dist,row.names = NULL)
to_id$id <- seq_len(nrow(to_id))
to_id$population = to$population
# -----------------------------
# Calcul des distances minimales
# -----------------------------

dist_net <- dodgr_dists(
  graph_main,
  from = from_id[, c("X", "Y")],
  to   = to_id[, c("X", "Y")]
)
rownames(dist_net) <- from_id$id



for (i in seq_len(nrow(from))) {
  accessibility = 0
  accessibility_square = 0
  temp = 0
  for (j in seq_len(nrow(to_id))) {
    value = dist_net[i,j]
    if(value < 1){
      value = 30
    }
    pop = to_id$population[j]
    accessibility = accessibility + 1000000*(pop/value)
    accessibility_square = accessibility_square + 1000000*(pop/(value*value))
    if (is.infinite(accessibility)&temp ==0) {
      #print(pop)
      #print(value)
      temp = 1
    }
  }
  potential = accessibility/nrow(to_id)
  potential_square = accessibility_square/nrow(to_id)
  from$apl[i] = potential
  from$apl_square[i] = potential_square
}

# -----------------------------
# Ajout au sf
# -----------------------------

st_write(from,paste0("data_output/final_result/",name_territory,".shp"),append = FALSE,delete_layer = TRUE)
