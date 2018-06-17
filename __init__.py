# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Spanish_Inspire_Catastral_Downloader
                                 A QGIS plugin
 Spanish Inspire Catastral Downloader
                             -------------------
        begin                : 2017-06-18
        copyright            : (C) 2017 by Patricio Soriano :: SIGdeletras.com
        email                : pasoriano@sigdeletras.com
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
# For Debug
import sys
try:
    sys.path.append(
        "D:\eclipse\plugins\org.python.pydev_6.2.0.201711281614\pysrc")
except ImportError:
    None
    
from .resources import *
# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Spanish_Inspire_Catastral_Downloader class from file Spanish_Inspire_Catastral_Downloader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Spanish_Inspire_Catastral_Downloader import Spanish_Inspire_Catastral_Downloader
    return Spanish_Inspire_Catastral_Downloader(iface)
