"""
/***************************************************************************
 GLViewer
                                 A QGIS plugin
 Equirectangular and 360° streetview like image viewer
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-12-17
        copyright            : (C) 2022 by Metrotopic
        email                : cazitouni@metrotopic.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GLViewer class from file GLViewer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GLViewer import GLViewer

    return GLViewer(iface)
