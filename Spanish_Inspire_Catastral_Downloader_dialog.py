# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Spanish_Inspire_Catastral_DownloaderDialog
                                 A QGIS plugin
 Spanish Inspire Catastral Downloader
                             -------------------
        begin                : 2017-06-18
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Patricio Soriano :: SIGdeletras.com
        email                : pasoriano@sigdeletras.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import Qt
import os
# from PyQt5.QtWidgets import QDialog

try:
    from qgis.core import Qgis
    from qgis.PyQt.QtCore import *
    from qgis.PyQt.QtGui import *
    from qgis.PyQt.QtWidgets import *
    from qgis.PyQt import uic
    from .qt.get_qt_elements import *
    QT_VERSION=QT_MAJOR
    os.environ['QT_API'] = f'pyqt{QT_MAJOR}'
except:
    raise ValueError(f'QT_VERSION {QT_VERSION} not supported')

import os.path
from qgis.core import *
from qgis.gui import *
from .resources import *


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Spanish_Inspire_Catastral_Downloader_dialog_base.ui'))


class Spanish_Inspire_Catastral_DownloaderDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Spanish_Inspire_Catastral_DownloaderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
