#cat("HOME =", Sys.getenv("HOME"), "\n")
#cat("WD =", getwd(), "\n")
#print(.libPaths())

library(FNN)
library(ggplot2)
library(sf)
library(dodgr)


# -----------------------------
# Lecture des données
# -----------------------------
#setwd("C:/Users/rgrandmaiso/Documents")
name_territory = "Sainte-Baume" # possible name = ["Sainte-Baume","Luberon","Baronnies provençales","Alpilles","Camargue","Mont-Ventoux","Queyras","Verdon"]
network <- st_read(paste0("data_output/reseau_marche_",name_territory,".shp"))
from <- st_read(paste0("data_output/distance_route_mairie_",name_territory,".shp"))
to <- st_read(paste0("data_output/centre_ville_",name_territory,".shp"))

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
nearest_grid <- get.knnx(data = vertices[, c("x", "y")],query = from_xy,k = 1)

from_id <- vertices$id[nearest_grid$nn.index[,1]]

# -----------------------------
# Destinations
# -----------------------------

to_xy <- st_coordinates(to)
nearest_town <- get.knnx(data = vertices[, c("x", "y")],query = to_xy,k = 1)
to_id <- unique(vertices$id[nearest_town$nn.index[,1]])

# -----------------------------
# Calcul des distances minimales
# -----------------------------

distances <- c()

for(i in seq(1, length(from_id), by = 200)) {
  ids_bloc <- from_id[i:min(i + 199, length(from_id))]
  cat("Traitement :", i,"à", min(i + 199, length(from_id)),"sur", length(from_id), "\n")
  d <- dodgr_dists(graph_main,from = ids_bloc,to = to_id)
  # chemins impossibles
  d[d > 1e9] <- NA
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
# Ajout au sf
# -----------------------------
from$dist_town <- distances


st_write(from,paste0("data_output/distance_town_",name_territory,".shp"),append = FALSE,delete_layer = TRUE)
