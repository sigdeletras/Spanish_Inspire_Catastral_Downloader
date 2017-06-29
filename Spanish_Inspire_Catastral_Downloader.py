# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Spanish_Inspire_Catastral_Downloader
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon

from PyQt4.QtGui import QFileDialog #para cargar el buscador de archivos



# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Spanish_Inspire_Catastral_Downloader_dialog import Spanish_Inspire_Catastral_DownloaderDialog
import os.path

import qgis
from PyQt4.QtGui import QMessageBox
from qgis.core import QgsProject
from qgis.gui import QgsMessageBar


import urllib

import csv
import zipfile

listProvincias =  ['02-ALBACETE', '03-ALACANT', '04-ALMERIA', '05-AVILA', '06-BADAJOZ', '07-ILLES BALEARS', '08-BARCELONA', '09-BURGOS', '10-CACERES', '11-CADIZ', '12-CASTELLO', '13-CIUDAD REAL', '14-CORDOBA', u'15-A CORUÑA', '16-CUENCA', '17-GIRONA', '18-GRANADA', '19-GUADALAJARA', '21-HUELVA', '22-HUESCA', '23-JAEN', '24-LEON', '25-LLEIDA', '26-LA RIOJA', '27-LUGO', '28-MADRID', '29-MALAGA', '30-MURCIA', '32-OURENSE', '33-ASTURIAS', '34-PALENCIA', '35-LAS PALMAS', '36-PONTEVEDRA', '37-SALAMANCA', '38-S.C. TENERIFE', '39-CANTABRIA', '40-SEGOVIA', '41-SEVILLA', '42-SORIA', '43-TARRAGONA', '44-TERUEL', '45-TOLEDO', '46-VALENCIA', '47-VALLADOLID', '49-ZAMORA', '50-ZARAGOZA', '51-CEUTA', '52-MELILLA']
listMunicipios =  ['14001-ADAMUZ', '14002-AGUILAR', '14003-ALCARACEJOS', '14004-ALMEDINILLA', '14005-ALMODOVAR DEL RIO', u'14006-AÑORA', '14007-BAENA', '14008-BELALCAZAR', '14009-BELMEZ', '14010-BENAMEJI', '14011-BLAZQUEZ', '14012-BUJALANCE', '14013-CABRA', '14015-CARCABUEY', u'14016-CARDEÑA', '14019-CASTRO DEL RIO', u'14014-CAÑETE DE LAS TORRES', '14020-CONQUISTA', '14021-CORDOBA', '14023-DOS TORRES', u'14022-DOÑA MENCIA', '14018-EL CARPIO', '14074-EL VISO', '14024-ENCINAS REALES', '14025-ESPEJO', '14026-ESPIEL', u'14027-FERNAN NUÑEZ', '14028-FUENTE LA LANCHA', '14029-FUENTE OBEJUNA', '14030-FUENTE PALMERA', '14031-FUENTE TOJAR', '14033-GUADALCAZAR', '14034-GUIJO', '14035-HINOJOSA DEL DUQUE', '14036-HORNACHUELOS', '14037-IZNAJAR', '14017-LA CARLOTA', '14032-LA GRANJUELA', '14057-LA RAMBLA', '14065-LA VICTORIA', '14038-LUCENA', '14039-LUQUE', '14040-MONTALBAN DE CORDOBA', '14041-MONTEMAYOR', '14042-MONTILLA', '14043-MONTORO', '14044-MONTURQUE', '14045-MORILES', '14046-NUEVA CARTEYA', '14047-OBEJO', '14048-PALENCIANA', '14049-PALMA DEL RIO', '14050-PEDRO ABAD', '14051-PEDROCHE', u'14052-PEÑARROYA PUEBLONUEVO', '14053-POSADAS', '14054-POZOBLANCO', '14055-PRIEGO DE CORDOBA', '14056-PUENTE GENIL', '14058-RUTE', '14059-SAN SEBASTIAN DE LOS BALLESTER', '14061-SANTA EUFEMIA', '14060-SANTAELLA', '14062-TORRECAMPO', '14063-VALENZUELA', '14064-VALSEQUILLO', '14066-VILLA DEL RIO', '14067-VILLAFRANCA DE CORDOBA', '14068-VILLAHARTA', '14069-VILLANUEVA DE CORDOBA', '14070-VILLANUEVA DEL DUQUE', '14071-VILLANUEVA DEL REY', '14072-VILLARALTO', '14073-VILLAVICIOSA DE CORDOBA', '14075-ZUHEROS']

codprov = ''
codmuni = ''

class Spanish_Inspire_Catastral_Downloader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.msgBar = iface.messageBar()


        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Spanish_Inspire_Catastral_Downloader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Spanish Inspire Catastral Downloader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Spanish_Inspire_Catastral_Downloader')
        self.toolbar.setObjectName(u'Spanish_Inspire_Catastral_Downloader')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Spanish_Inspire_Catastral_Downloader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = Spanish_Inspire_Catastral_DownloaderDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Spanish_Inspire_Catastral_Downloader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg.pushButton_select_path.clicked.connect(self.select_output_folder)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Spanish Inspire Catastral Downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_folder(self):
        """Select output folder"""

        self.dlg.lineEdit_path.clear() 
        folder = QFileDialog.getExistingDirectory(self.dlg, "Select folder")
        self.dlg.lineEdit_path.setText(folder)

    # def show_variables(self):
        
    #     if self.dlg.comboBox_municipality.currentText() == '':
    #         self.msgBar.pushMessage('No se ha indicado el nunicipio', level=QgsMessageBar.INFO)
    #     else:
    #         prov = self.dlg.comboBox_province.currentText()
    #         muni = self.dlg.comboBox_municipality.currentText()
    #         self.msgBar.pushMessage(prov[0:2]+ muni[0:5], level=QgsMessageBar.INFO)

    def not_data(self):
        """Message for fields without information"""
        self.msgBar.pushMessage('Completar datos de municipio o indicar la ruta de descarga', level=QgsMessageBar.INFO)

    def filter_municipality(self, index):
        """Message for fields without information"""
        
        filtroprovincia = self.dlg.comboBox_province.currentText()
        self.dlg.comboBox_municipality.clear() 

        self.dlg.comboBox_municipality.addItems([muni for muni in listMunicipios if muni[0:2] == filtroprovincia[0:2]])

        inecode_catastro = self.dlg.comboBox_municipality.currentText()

        codprov = inecode_catastro[0:2]
        codmuni = inecode_catastro[0:5]


    def download(self):
        """Dowload data funtion"""

        if self.dlg.comboBox_municipality.currentText() == '' or self.dlg.lineEdit_path.text() == '':

            self.not_data()

        else:

            inecode_catastro = self.dlg.comboBox_municipality.currentText()
            codprov = inecode_catastro[0:2]
            codmuni = inecode_catastro[0:5]
            # pass

            # self.msgBar.pushMessage("Start downloading zip files...", level=QgsMessageBar.INFO)

            # download de Cadastral Parcels
            if self.dlg.checkBox_parcels.isChecked():

                
                url = u'http://www.catastro.minhap.es/INSPIRE/CadastralParcels/%s/%s/A.ES.SDGC.CP.%s.zip' % (codprov, inecode_catastro, codmuni)
                # self.msgBar.pushMessage(url, level=QgsMessageBar.SUCCESS)
                zippath = self.dlg.lineEdit_path.text()

                try:
                    os.makedirs(zippath + '\%s' % inecode_catastro)
                except OSError:
                    pass
                
                zipParcels = zippath + "\%s" % inecode_catastro + "\%s_Parcels.zip" % inecode_catastro # poner fecha

                urllib.urlretrieve(url.encode('utf-8'), zipParcels)
            
            # download de Buildings
            if self.dlg.checkBox_buildings.isChecked():

                url = u'http://www.catastro.minhap.es/INSPIRE/Buildings/%s/%s/A.ES.SDGC.BU.%s.zip' % (codprov, inecode_catastro, codmuni)
                zippath = self.dlg.lineEdit_path.text()

                try:
                    os.makedirs(zippath + '\%s' % inecode_catastro)
                except OSError:
                    pass
                

                zipbuildings = zippath + "\%s" % inecode_catastro + "\%s_Buildings.zip" % inecode_catastro # poner fecha
                urllib.urlretrieve(url.encode('utf-8'), zipbuildings)

            # download de Addresses
            if self.dlg.checkBox_addresses.isChecked():

                url = u'http://www.catastro.minhap.es/INSPIRE/Addresses/%s/%s/A.ES.SDGC.AD.%s.zip' % (codprov, inecode_catastro, codmuni)
                zippath = self.dlg.lineEdit_path.text()
 
                try:
                    os.makedirs(zippath + '\%s' % inecode_catastro)
                except OSError:
                    pass

                zipAddresses = zippath + "\%s" % inecode_catastro + "\%s_Addresses.zip" % inecode_catastro # poner fecha
                urllib.urlretrieve(url.encode('utf-8'), zipAddresses)
                       ## Descomprime y carga en proyecto si se marca la opcion

            # self.msgBar.clearWidgets()
            self.msgBar.pushMessage("Finished!", level=QgsMessageBar.SUCCESS)

            ## debe descomprimir cualquier archivos ZIP de la carptea
            if self.dlg.checkBox_load_layers.isChecked():
                ## Descomprime los zips downloaddos
                
                self.msgBar.pushMessage("Start loading GML files...", level=QgsMessageBar.INFO)

                for zipfilecatastro in os.listdir(zippath + "\%s" % inecode_catastro):
                    if zipfilecatastro[-4:] == ".zip":
                        with zipfile.ZipFile(zippath + "\%s" % inecode_catastro + '\\'+zipfilecatastro, "r") as z:
                            z.extractall(zippath + "\%s" % inecode_catastro)
                        #self.msgBar.pushMessage('Descomprimidos '+zippath, level=QgsMessageBar.SUCCESS)

                ## Carga los GMLs
                for gmlfile in os.listdir(zippath + "\%s" % inecode_catastro):
                    if gmlfile[-4:] == ".gml":
                        layer = self.iface.addVectorLayer(zippath + "\%s" % inecode_catastro + '\\' + gmlfile, "", "ogr")

                # self.msgBar.pushMessage("Finished!", level=QgsMessageBar.SUCCESS)

    def run(self):
        """Run method that performs all the real work"""
        # muestra variables
        # self.dlg.pushButton_show.clicked.connect(self.show_variables)  
        self.dlg.lineEdit_path.clear()

        # Datos para provincias
        self.dlg.comboBox_province.clear()
        self.dlg.comboBox_municipality.clear()
        self.dlg.comboBox_province.addItems(listProvincias)
        self.dlg.comboBox_province.currentIndexChanged.connect(self.filter_municipality)
        self.dlg.pushButton_run.clicked.connect(self.download)
       
        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
     
        # See if OK was pressed
        if result:

            pass

            
            