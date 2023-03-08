# Equirectangular 360° Viewer

A simple streetview-like Qgis plugin for equirectangular image visualization.

This plugin takes point data from a geopackage and/or a PostGIS database and loads the corresponding image when you click on the position in the map canvas.

![image](https://user-images.githubusercontent.com/92778930/210170388-e5fa5da5-ab23-446c-977a-b801bfb7fbbc.png)

## Plugin usage

### Global usage 

To use this plugin, simply fill in your database connection and/or geopackage and define the related columns:

- **Geometry column**: the geometry column of the point table
- **Direction column**: image starting direction in north angle where 0-360 is north
- **Link column**: link to the image, could be a directory or a web URL
- **Date column**: date the image was taken

Once the parameters are filled in, simply click on the point position on the map and drag the cursor to the direction you want, and the image will load, no need to load the point layer in your project.

The plugin also offer the ability to jump to different images, you only have to click on the image in the direction you want.
The gap parameter could be set to change the jump distance (in meters), by default it's set to 5.

In addition it's possible for the user to press the **C** key to make a crosshair appear on the image. 

### Comparative view 

![image](https://user-images.githubusercontent.com/92778930/222739732-52a6e90b-1ce5-429c-8ef5-767e10f0f55c.png)


The comparative view offer the possibility for the user to cross a position between two image in order to get the intersection point between the two.

To launch the second view, the user can press the Comparative view button then navigate to the desired images in both of the view. 
The user can set the line length with the gap parameter. 
Once both line crossed each other, it's possible to make an intersection point appears by clicking on the Cross position button.
A second click on the comparative view button will close the second view.

Once finished the user can export all the points generated to a virtual layer by usjng the related menu option.

It's also possible to remove all point on the canvas in the plugin's icon menu under the reload connection parameter.

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
