# Equirectangular 360° Viewer

A simple streetview-like Qgis plugin for equirectangular image visualization.

This plugin takes point data from a geopackage and/or a PostGIS database and loads the corresponding image when you click on the position in the map canvas.

![image](https://user-images.githubusercontent.com/92778930/210170388-e5fa5da5-ab23-446c-977a-b801bfb7fbbc.png)

## Plugin usage

To use this plugin, simply fill in your database connection and/or geopackage and define the related columns:

- **Geometry column**: the geometry column of the point table
- **Direction column**: image starting direction in north angle where 0-360 is north
- **Link column**: link to the image, could be a directory or a web URL
- **Date column**: date the image was taken

Once the parameters are filled in, simply click on the point position on the map and the image will load, no need to load the point layer in your project.

## For Linux users

On Linux systems, you may need to install the others packages in order to use the plugin:

To install them on Ubuntu:
```
sudo apt-get install python3-pyqt5.qtopengl
sudo apt-get install python3-opengl
```
For Fedora : 
```
sudo dnf install python-pyopengl
sudo dnf install mesa-libGLU mesa-libGL
```
