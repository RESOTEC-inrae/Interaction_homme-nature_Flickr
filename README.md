# Stage Grandmaison Roland

This code allow to link photos taken from a social network (Here Flickr) and the various informations about the vegetation and the condition (altitude,accessibility...) when they were taken.


# Pré-requis et Installation

This project has been developped on python 3.12.10
The list of librairies necessary is written in the file "requirement.txt"

## Informations

### Important information about the script

They are two differents informations that can be modified, on line 18 and 19.
They are the size of the square of study and the name of the natural parc where you want the informations.

You also need adapt line 24 to read you file with the photos informations. 

### Important information for the photo

For this script, we are using deux different informations :  
When the photo was taken : "Date"  
The name of the username who posted the photo : "Owner_Name"  
It's possible to remove the username as a condition if it doesn't exist, 
you just need to uncomment the line 200 and comment the line 199

### Data

For this script, we used mainly informations from the french IGN(geographical national institute) 
Vegetation (BD Foret) : https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-FORET?redirected_from=geoservices.ign.fr#telechargementv1  
Altitude (BD Alti): https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-ALTI  
Building (BD Topo): https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-TOPO  

For mesuring the acceess to the city, we use informations from Open Street Map (OSM)

