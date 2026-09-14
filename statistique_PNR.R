# Packages
library(sf)
library(dplyr)
library(factoextra)
setwd("C:/Users/rgrandmaiso/Downloads")

name_territory = c("Sainte-Baume","Luberon","Baronnies provencales","Alpilles",
                   "Mont-Ventoux","Queyras","Verdon","Corse","Monts d'Ardeche")
#name_territory = c("Sainte-Baume","Luberon","Baronnies provencales","Alpilles","Mont-Ventoux","Queyras","Verdon","Monts d'Ardeche")

for(i in 1:length(name_territory)){
  data.i = st_read(paste0(name_territory[i], ".shp")) %>%
    mutate(pnr = name_territory[i])
  data.i <- data.i %>%
    select(-any_of(c("area_x", "area_y")))
  if(i == 1) data = data.i
  else data = rbind(data, data.i)
}


data$feuillus <- data$Peupleraie+data$Ffer_F+data$Fouv_F
data$conifere <- data$Ffer_C+data$Fouv_C
data$mixte <- data$Ffer_M+data$Fouv_M
data$vege_basse <- data$vege_bas+data$Ffer_sansA+data$Fouv_sansA
data$veg_moy <- data$veg_alt
data$feuillus[data$feuillus > 100] <- 100
data$conifere[data$conifere > 100] <- 100
data$mixte[data$mixte > 100] <- 100
data$elevation[data$elevation < 0] <- 0
data$photo <- data$leasure+data$nature
data$veg_ouvert <- data$Fouv_C+data$Fouv_F+data$Fouv_M

data$veg_ferme <- data$Ffer_C+data$Ffer_F+data$Ffer_M

df <- data %>%
  group_by(pnr) %>%
  summarise(somme = sum(photo, na.rm = TRUE))

# Préparation des données
data_num <- data |>
  st_drop_geometry() |>
  dplyr::filter(sans_foret < 50) |>
  dplyr::mutate(sans_foret = ifelse(sans_foret < 0, 0, sans_foret))

colSums(is.na(data_num))
data_num <- na.omit(data_num)

#####################################################

data_accessibility <- data_num |>
  subset(select = c(dist_path,dist_road,dist_town,elevation,apl_bird,apl_bird_c,apl,apl_square))

acp_access <- prcomp(
  data_accessibility,
  center = TRUE,
  scale. = TRUE
)
summary(acp_access)
fviz_pca_var(
  acp_access,
  col.var = "contrib"
)
fviz_pca_biplot(
  acp_access,
  geom.ind = "point",
  geom.var = "arrow",
  repel = TRUE,
  col.var = "contrib",
  gradient.cols = c("blue", "yellow", "red"),
  arrowsize = 1.5,
  labelsize = 5
)

#####################################################

data_vegetation <-data_num |>
  subset(select = c(feuillus,conifere,mixte))

acp_veg <- prcomp(
  data_vegetation,
  center = TRUE,
  scale. = TRUE
)

fviz_pca_var(
  acp_veg,
  col.var = "contrib"
)

fviz_pca_biplot(
  acp_veg,
  geom.ind = "point",
  geom.var = "arrow",
  repel = TRUE,
  col.var = "contrib",
  gradient.cols = c("blue", "yellow", "red"),
  arrowsize = 1.5,
  labelsize = 5
)

#####################################################

data_densite <-data_num |>
  subset(select = c(veg_ouvert,veg_ferme))

acp_densite <- prcomp(
  data_densite,
  center = TRUE,
  scale. = TRUE
)

fviz_pca_var(
  acp_densite,
  col.var = "contrib"
)

#####################################################

data_lidar <- data_num |>
  subset(select = c(veg_moy,veg_q90,vege_bas,sans_foret,veg_sd))

acp_lidar <- prcomp(
  data_lidar,
  center = TRUE,
  scale. = TRUE
)
fviz_pca_var(
  acp_lidar,
  col.var = "contrib"
)
fviz_pca_biplot(
  acp_lidar,
  geom.ind = "point",
  geom.var = "arrow",
  repel = TRUE,
  col.var = "contrib",
  gradient.cols = c("blue", "yellow", "red"),
  arrowsize = 1.5,
  labelsize = 5
)

#####################################################

data_num$ouverture <- get_pca_ind(acp_densite)$coord[, "Dim.1"]
data_num$CvF <- get_pca_ind(acp_veg)$coord[, "Dim.1"]
data_num$mixite <- -abs(get_pca_ind(acp_veg)$coord[, "Dim.1"])
data_num$access <- -get_pca_ind(acp_access)$coord[, "Dim.1"]
data_num$hauteur <- -get_pca_ind(acp_lidar)$coord[, "Dim.1"]

#script acp Luberon
data_luberon <- data_num |>
  dplyr::filter(pnr ==  'Verdon') |>
  dplyr::select(square_id,CvF, hauteur, access,ouverture,mixite)
data_carte_luberon = st_read("Verdon.shp")
data_carte_luberon <- merge(data_carte_luberon,data_luberon,by = "square_id")
#st_write(data_carte_luberon,"Verdon_carte.shp")
###########

var_exp = c("conifere","veg_ferme","veg_q90","CvF", "elevation", "hauteur", "access","ouverture","sans_foret","mixite")
data_model = cbind(data_num[, "photo"], scale(data_num[, var_exp], center = TRUE, scale = TRUE))
colnames(data_model)[1] = "photo"
data_model = data_model %>%
  as.data.frame()%>%
  mutate(pnr = data_num$pnr)

library("glmmTMB")
#library(DHARMa)
mod1 = glmmTMB(photo ~ conifere + elevation  + veg_q90 + veg_ferme +(1|pnr), ziformula = ~ 1, data = data_model,  family = nbinom2)
#car::Anova(mod1)
AIC(mod1)
summary(mod1)

mod2 = glmmTMB(photo ~ CvF+ hauteur + access + ouverture + sans_foret + mixite + (1|pnr), ziformula = ~ 1, data = data_model,  family = nbinom2)
car::Anova(mod2)
AIC(mod2)
summary(mod2)

modcomplet = glmmTMB(photo ~ CvF + hauteur + access + ouverture + sans_foret + mixite + (1|pnr), ziformula = ~ 1, # Formule pour le nombre de photos
                     data = data_model,  family = nbinom2)
car::Anova(modcomplet)
AIC(modcomplet)
summary(modcomplet)

modcomplet = glmmTMB(photo ~ CvF + hauteur + access + ouverture + sans_foret + mixite + (1|pnr), # Formule pour le nombre de photos
                     ziformula = photo ~ elevation + access + sans_foret , # Modele pour la probabilité d'avoir au moins une photo
                     data = data_model,  family = nbinom2)
car::Anova(modcomplet)
AIC(modcomplet)
summary(modcomplet)

library(performance)
r2(modcomplet)

############## Image résultat modèle

library(broom.mixed)

data.out.j <- tidy(
  modcomplet,
  effects = "fixed",
  conf.int = TRUE
) |>
  dplyr::filter(term != "(Intercept)") |>
  dplyr::mutate(
    var.exp = term,
    est = estimate,
    est.low = conf.low,
    est.high = conf.high,
    significance = ifelse(
      est.low > 0 | est.high < 0,
      "yes",
      "no"
    )
  )

plot.j <- data.out.j %>%
  dplyr::filter(component == "cond") %>%
  dplyr::mutate(
    significance = ifelse(
      est.low > 0 | est.high < 0,
      "yes",
      "no"
    )
  ) %>%
  dplyr::mutate(
    var.exp = dplyr::case_when(
      var.exp == "CvF" ~ "CvF",
      var.exp == "veg_lidar" ~ "veg_lidar",
      var.exp == "access" ~ "access",
      var.exp == "ouverture" ~ "ouverture",
      var.exp == "sans_foret" ~ "sans_foret",
      var.exp == "mixite" ~ "mixite",
      TRUE ~ var.exp
    )
  ) %>%
  ggplot(aes(x = var.exp, y = est, color = significance)) + 
  geom_errorbar(aes(ymin = est.low, ymax = est.high),width = 0.1) + 
  geom_point(shape = 21,size = 3,fill = "#9B2226") +
  xlab("") + 
  #ylab("")+
  ylab("Effet des différentes variables explicatives \n sur le nombre d'interactions homme-nature observées") +
  scale_color_manual(
    values = c(
      `no` = "gray",
      `yes` = "black"
    )
  ) +
  geom_hline(yintercept = 0,linetype = "dashed") +
  theme(panel.background = element_rect(color = "black",fill = "white"), panel.grid = element_blank(), 
    strip.background = element_blank(), strip.text = element_text(face = "bold"), 
    legend.position = "none", axis.ticks.length = unit(-0.1, "cm"),axis.text.y = element_text(size = 16), axis.text.x = element_text(size = 14),axis.title = element_text(size=14))+
  coord_flip()
plot.j

############################### ACP Access
library(cowplot)
n.cat <- 20
# - Extract the coordinates of the ndividuals on pca axis
res.ind <- data.frame(plot = data_num$square_id, 
                      pca1 = data_num$access)  %>%
  filter(pca1 < 11) %>%
  mutate(pca1_cut = cut(pca1, breaks = seq(min(pca1), max(pca1), length.out = n.cat)), 
         pca1_min = as.numeric(gsub("\\(", "", gsub("\\,.+", "", pca1_cut))), 
         pca1_max = as.numeric(gsub(".+\\,", "", gsub("\\]", "", pca1_cut))), 
         pca1_median = (pca1_min + pca1_max)/2) %>%
  filter(!is.na(pca1_cut))

# - Extract the coordinates of the variables on pca axis and classify by category
res.var <- data.frame(var = rownames(get_pca_var(acp_access)[[1]]), 
                      # Negative because inverse of pca in original data
                      pca1 = -get_pca_var(acp_access)[[1]][, 1]) %>%
  mutate(var.pos = c(1:dim(.)[1]))

# Plot the arrows of the first PCA axis
plot.var = res.var %>%
  ggplot(aes(x = var.pos, xend = var.pos, y = 0, yend = pca1)) + 
  geom_segment(arrow = arrow(length = unit(0.1, "cm"))) + 
  scale_x_continuous(breaks = res.var$var.pos, 
                     #labels = res.var$var, 
                     labels = c(expression(A[network_square]),expression(A[network]),expression(A[oiseau_square]),expression(A[oiseau]),"Elevation","Dist_town","Dist_road","Dist_path"),
                     limits = c(0.5, 8.5)) + 
  scale_y_continuous(breaks = c(-0.6, -0.3, 0, 0.3, 0.6)) +
  xlab("") + geom_hline(yintercept = 0, linetype = "dashed") +
  ylab(paste0("PC1_access (", round(summary(acp_access)$importance[2, 1]*100, digits = 2), "%)")) + 
  coord_flip() + 
  theme(panel.background = element_rect(fill = "white", color = "black"), 
        panel.grid = element_blank(),
        axis.text = element_text(size = 16),
        axis.title = element_text(size = 20)) 


# Plot the distribution of plots along the pca axis
plot.ind = res.ind %>%
  group_by(pca1_median) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = pca1_median, y = n)) +
  geom_bar(color = "black", fill = "steelblue", stat = "identity") +
  ylab("Nombre de \n carreaux") + 
  theme(panel.background = element_rect(color = "black", fill = "white"), 
        panel.grid = element_blank(), 
        axis.text.x = element_blank(),
        axis.title.y = element_text(size = 14),
        axis.text.y = element_text(size = 12),
        axis.title.x = element_blank(), 
        axis.ticks.x = element_blank(), 
        legend.position = "none") 

# Plot the pca climate
plot.pca = plot_grid(plot.ind, plot.var, ncol = 1, align = "v",rel_heights = c(1, 2))
plot.pca

############################# acp_lidar
res.ind <- data.frame(plot = data_num$square_id, 
                      pca1 = data_num$hauteur)  %>%
  filter(pca1 > -8) %>%
  mutate(pca1_cut = cut(pca1, breaks = seq(min(pca1), max(pca1), length.out = n.cat)), 
         pca1_min = as.numeric(gsub("\\(", "", gsub("\\,.+", "", pca1_cut))), 
         pca1_max = as.numeric(gsub(".+\\,", "", gsub("\\]", "", pca1_cut))), 
         pca1_median = (pca1_min + pca1_max)/2) %>%
  filter(!is.na(pca1_cut))

# - Extract the coordinates of the variables on pca axis and classify by category
res.var <- data.frame(var = rownames(get_pca_var(acp_lidar)[[1]]), 
                      # Negative because inverse of pca in original data
                      pca1 = get_pca_var(acp_lidar)[[1]][, 1]) %>%
  mutate(var.pos = c(1:dim(.)[1]))

# Plot the arrows of the first PCA axis
plot.var = res.var %>%
  ggplot(aes(x = var.pos, xend = var.pos, y = 0, yend = pca1)) + 
  geom_segment(arrow = arrow(length = unit(0.1, "cm"))) + 
  scale_x_continuous(breaks = res.var$var.pos, 
                     #labels = res.var$var, 
                     labels = c(expression(H[moy]),expression(H[max]),expression(p[vegebas]),expression(p[sansforet]),expression(H[Div])),
                     limits = c(0.5, 5.5)) + 
  xlab("") + geom_hline(yintercept = 0, linetype = "dashed") +
  ylab(paste0("PC1_MNH (", round(summary(acp_lidar)$importance[2, 1]*100, digits = 2), "%)")) + 
  coord_flip() + 
  theme(panel.background = element_rect(fill = "white", color = "black"), 
        panel.grid = element_blank(),
        axis.text = element_text(size = 16),
        axis.title = element_text(size = 20)) 

# Plot the distribution of plots along the pca axis
plot.ind = res.ind %>%
  group_by(pca1_median) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = pca1_median, y = n)) +
  geom_bar(color = "black", fill = "steelblue", stat = "identity") +
  ylab("Nombre de \n carreaux") + 
  theme(panel.background = element_rect(color = "black", fill = "white"), 
        panel.grid = element_blank(), 
        axis.text.x = element_blank(),
        axis.title.y = element_text(size = 14),
        axis.text.y = element_text(size = 12),
        axis.title.x = element_blank(), 
        axis.ticks.x = element_blank(), 
        legend.position = "none") 

# Plot the pca climate
plot.pca = plot_grid(plot.ind, plot.var, ncol = 1, align = "v",rel_heights = c(1, 2))
plot.pca

############acp_veg
# - Extract the coordinates of the ndividuals on pca axis
res.ind <- data.frame(plot = data_num$square_id, 
                      pca1 = data_num$CvF)  %>%
  mutate(pca1_cut = cut(pca1, breaks = seq(min(pca1), max(pca1), length.out = n.cat)), 
         pca1_min = as.numeric(gsub("\\(", "", gsub("\\,.+", "", pca1_cut))), 
         pca1_max = as.numeric(gsub(".+\\,", "", gsub("\\]", "", pca1_cut))), 
         pca1_median = (pca1_min + pca1_max)/2) %>%
  filter(!is.na(pca1_cut))

# - Extract the coordinates of the variables on pca axis and classify by category
res.var <- data.frame(var = rownames(get_pca_var(acp_veg)[[1]]), 
                      # Negative because inverse of pca in original data
                      pca1 = get_pca_var(acp_veg)[[1]][, 1]) %>%
  mutate(var.pos = c(1:dim(.)[1]))

plot.var = res.var %>%
  ggplot(aes(x = var.pos, xend = var.pos, y = 0, yend = pca1)) + 
  geom_segment(arrow = arrow(length = unit(0.1, "cm"))) + 
  scale_x_continuous(breaks = res.var$var.pos, 
                     labels = res.var$var, 
                     limits = c(0.5, 3.5)) + 
  xlab("") + geom_hline(yintercept = 0, linetype = "dashed") +
  ylab(paste0("PC1_Composition (", round(summary(acp_veg)$importance[2, 1]*100, digits = 2), "%)")) + 
  coord_flip() + 
  theme(panel.background = element_rect(fill = "white", color = "black"), 
        panel.grid = element_blank(),
        axis.text = element_text(size = 16),
        axis.title = element_text(size = 20)) 

# Plot the distribution of plots along the pca axis
plot.ind = res.ind %>%
  group_by(pca1_median) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = pca1_median, y = n)) +
  geom_bar(color = "black", fill = "steelblue", stat = "identity") +
  ylab("Nombre de \n carreaux") + 
  theme(panel.background = element_rect(color = "black", fill = "white"), 
        panel.grid = element_blank(), 
        axis.text.x = element_blank(),
        axis.title.y = element_text(size = 14),
        axis.text.y = element_text(size = 12),
        axis.title.x = element_blank(), 
        axis.ticks.x = element_blank(), 
        legend.position = "none") 
plot.pca = plot_grid(plot.ind, plot.var, ncol = 1, align = "v",rel_heights = c(1, 2))
plot.pca

############acp_veg mixite
res.ind <- data.frame(plot = data_num$square_id, 
                      pca1 = data_num$mixite)  %>%
  mutate(pca1_cut = cut(pca1, breaks = seq(min(pca1), max(pca1), length.out = n.cat)), 
         pca1_min = as.numeric(gsub("\\(", "", gsub("\\,.+", "", pca1_cut))), 
         pca1_max = as.numeric(gsub(".+\\,", "", gsub("\\]", "", pca1_cut))), 
         pca1_median = (pca1_min + pca1_max)/2) %>%
  filter(!is.na(pca1_cut))

# - Extract the coordinates of the variables on pca axis and classify by category
res.var <- data.frame(var = rownames(get_pca_var(acp_veg)[[1]]), 
                      # Negative because inverse of pca in original data
                      pca1 = -abs(get_pca_var(acp_veg)[[1]][, 1])) %>%
  mutate(var.pos = c(1:dim(.)[1]))

# Plot the arrows of the first PCA axis
plot.var = res.var %>%
  ggplot(aes(x = var.pos, xend = var.pos, y = 0, yend = pca1)) + 
  geom_segment(arrow = arrow(length = unit(0.1, "cm"))) + 
  scale_x_continuous(breaks = res.var$var.pos, 
                     labels = res.var$var, 
                     limits = c(0.5, 3.5)) + 
  xlab("") + geom_hline(yintercept = 0, linetype = "dashed") +
  ylab(paste0("PC1_Mixite (", round(summary(acp_veg)$importance[2, 1]*100, digits = 2), "%)")) + 
  coord_flip() + 
  theme(panel.background = element_rect(fill = "white", color = "black"), 
        panel.grid = element_blank(),
        axis.text = element_text(size = 16),
        axis.title = element_text(size = 20)) 

# Plot the distribution of plots along the pca axis
plot.ind = res.ind %>%
  group_by(pca1_median) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = pca1_median, y = n)) +
  geom_bar(color = "black", fill = "steelblue", stat = "identity") +
  ylab("Nombre de \n carreaux") + 
  theme(panel.background = element_rect(color = "black", fill = "white"), 
        panel.grid = element_blank(), 
        axis.text.x = element_blank(),
        axis.title.y = element_text(size = 14),
        axis.text.y = element_text(size = 12),
        axis.title.x = element_blank(), 
        axis.ticks.x = element_blank(), 
        legend.position = "none") 
# Plot the pca climate
plot.pca = plot_grid(plot.ind, plot.var, ncol = 1, align = "v",rel_heights = c(1, 2))
plot.pca

############ acp_densite
res.ind <- data.frame(plot = data_num$square_id, 
                      pca1 = data_num$ouverture)  %>%
  mutate(pca1_cut = cut(pca1, breaks = seq(min(pca1), max(pca1), length.out = n.cat)), 
         pca1_min = as.numeric(gsub("\\(", "", gsub("\\,.+", "", pca1_cut))), 
         pca1_max = as.numeric(gsub(".+\\,", "", gsub("\\]", "", pca1_cut))), 
         pca1_median = (pca1_min + pca1_max)/2) %>%
  filter(!is.na(pca1_cut))

# - Extract the coordinates of the variables on pca axis and classify by category
res.var <- data.frame(var = rownames(get_pca_var(acp_densite)[[1]]), 
                      # Negative because inverse of pca in original data
                      pca1 = get_pca_var(acp_densite)[[1]][, 1]) %>%
  mutate(var.pos = c(1:dim(.)[1]))

# Plot the arrows of the first PCA axis
plot.var = res.var %>%
  ggplot(aes(x = var.pos, xend = var.pos, y = 0, yend = pca1)) + 
  geom_segment(arrow = arrow(length = unit(0.1, "cm"))) + 
  scale_x_continuous(breaks = res.var$var.pos, 
                     labels = res.var$var, 
                     limits = c(0.5, 2.5)) + 
  xlab("") + geom_hline(yintercept = 0, linetype = "dashed") +
  ylab(paste0("PC1_Ouverture (", round(summary(acp_densite)$importance[2, 1]*100, digits = 2), "%)")) + 
  coord_flip() + 
  theme(panel.background = element_rect(fill = "white", color = "black"), 
        panel.grid = element_blank(),
        axis.text = element_text(size = 16),
        axis.title = element_text(size = 20)) 

# Plot the distribution of plots along the pca axis
plot.ind = res.ind %>%
  group_by(pca1_median) %>%
  summarize(n = n()) %>%
  ggplot(aes(x = pca1_median, y = n)) +
  geom_bar(color = "black", fill = "steelblue", stat = "identity") +
  ylab("Nombre de \n carreaux") + 
  theme(panel.background = element_rect(color = "black", fill = "white"), 
        panel.grid = element_blank(), 
        axis.text.x = element_blank(),
        axis.title.y = element_text(size = 14),
        axis.text.y = element_text(size = 12),
        axis.title.x = element_blank(), 
        axis.ticks.x = element_blank(), 
        legend.position = "none") 
# Plot the pca climate
plot.pca = plot_grid(plot.ind, plot.var, ncol = 1, align = "v",rel_heights = c(1, 2))
plot.pca

#################

library(ggplot2)

# Coordonnées des individus
data.ind <- as.data.frame(acp_lidar$x) %>%mutate(id_square = data_num$id_square)

# Coordonnées des variables
data.var <- as.data.frame(acp_lidar$rotation) %>%mutate(var = rownames(acp_lidar$rotation))

# Pourcentage de variance expliquée
var_explained <- summary(acp_lidar)$importance[2, ] * 100

# Limites du graphique
range.x <- range(c(-8,max(data.ind$PC1)))
range.y <- range(c(min(data.ind$PC2),4))

# Facteur pour agrandir légèrement les limites
space.frac <- 0.1

# Agrandir les limites pour les flèches
#range.x <- c(min(range.x[1], data.var$PC1),max(range.x[2], data.var$PC1))
#range.y <- c(min(range.y[1], data.var$PC2),max(range.y[2], data.var$PC2))

# Coordonnées finales des labels des variables

data.var <- data.var |>
  mutate(
    PC1_arrow = PC1 * 3,
    PC2_arrow = PC2 * 3
  )
library(ggrepel)

# Graphique ACP
plot.out <- ggplot(
  data.ind,
  aes(x = PC1, y = PC2)
) +
  # Points des observations
  geom_point(
    size = 2,
    shape = 21,
    fill = "#22333B",
    color = "black",
    alpha = 0.5
  ) +
  
  # Flèches des variables
  geom_segment(
    data = data.var,
    aes(
      x = 0,
      xend = PC1_arrow,
      y = 0,
      yend = PC2_arrow
    ),
    color = "red",
    linewidth = 1,
    arrow = arrow(
      length = unit(0.3, "cm"),
      type = "closed"
    ),
    inherit.aes = FALSE
  )+
  # Noms des variables
  geom_text_repel(
    data = data.var,
    aes(
      x = PC1*3,
      y = PC2*3,
      label = var
    ),
    fontface = "bold",
    size = 4,
    color = "red",
    nudge_x = 0.1,
    nudge_y = -0.1,
    force = 2,
    segment.color = "grey50",
    segment.size = 0.3,
    box.padding = 0.3,
    point.padding = 0.2,
    inherit.aes = FALSE
  )+
  

  # Cadre
  geom_rect(
    aes(
      xmin = range.x[1],
      xmax = range.x[2],
      ymin = range.y[1],
      ymax = range.y[2]
    ),
    color = "black",
    fill = NA,
    inherit.aes = FALSE
  ) +
  
  # Ligne horizontale à zéro
  geom_segment(
    x = range.x[1],
    xend = range.x[2],
    y = 0,
    yend = 0,
    linetype = "dashed"
  ) +
  
  # Ligne verticale à zéro
  geom_segment(
    x = 0,
    xend = 0,
    y = range.y[1],
    yend = range.y[2],
    linetype = "dashed"
  ) +
  
  # Axe X
  xlab(
    paste0(
      "PCA1 (",
      round(var_explained[1], 2),
      "%)"
    )
  ) +
  
  # Axe Y
  ylab(
    paste0(
      "PCA2 (",
      round(var_explained[2], 2),
      "%)"
    )
  ) +
  
  # Thème
  theme(
    panel.background = element_blank(),
    panel.grid = element_blank(),
    axis.ticks = element_blank()
  ) +
  # Limites
  xlim(c(1.2, 1.2) * range.x) +
  ylim(
    c(1.2, 1.2) * range.y
  )
plot.out

# - Save the plot=ggsave(file.in, plot.out, width = 12, height = 12, units = "cm", dpi = 600, bg = "white")


