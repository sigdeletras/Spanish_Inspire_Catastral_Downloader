# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Spanish_Inspire_Catastral_Downloader
                                 A QGIS plugin
 Spanish Inspire Catastral Downloader
                              -------------------
        begin				: 2017-06-18
        git sha			  : $Format:%H$
        copyright			: (C) 2017 by Patricio Soriano :: SIGdeletras.com
        email				: pasoriano@sigdeletras.com
 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or	 *
 *   (at your option) any later version.								   *
 *																		 *
 ***************************************************************************/
"""

import json
import os
import os.path
import shutil
import socket
import ssl
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from urllib import parse, request

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import Qt

# from PyQt5.QtWidgets import QDialog
# For Debug
try:
    from pydevd import *
except ImportError:
    None

from qgis.PyQt import QtNetwork, uic
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import Qgis
from .qt.get_qt_elements import *


if QT_MAJOR == 5:
    os.environ['QT_API'] = 'pyqt5'
elif QT_MAJOR == 6:
    os.environ['QT_API'] = 'pyqt6'
else:
    raise ValueError(f'QT_VERSION {QT_MAJOR} not supported')

from qgis.core import *
from qgis.core import (QgsMessageLog)

from .Spanish_Inspire_Catastral_Downloader_dialog import \
    Spanish_Inspire_Catastral_DownloaderDialog

from .Config import _port, _proxy

CODPROV = ''
CODMUNI = ''
ULR_CATASTRO = 'https://www.catastro.hacienda.gob.es'

# SHA-256 fingerprint of the root CA that signs the certificate of
# www.catastro.hacienda.gob.es: "AC RAIZ FNMT-RCM SERVIDORES SEGUROS" (FNMT-RCM).
# This root is NOT shipped by every platform trust store (notably macOS, and it is
# not present in the certifi bundle that QGIS uses for Python), which makes the
# TLS handshake fail and the download silently stall at 0%. We only trust it when
# the fingerprint matches exactly (certificate pinning), never blindly.
CATASTRO_ROOT_CA_SHA256 = '554153b13d2cf9ddb753bfbe1a4e0ae08d0aa4187058fe60a2b862b2e4b87bcb'

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
        self.data_dir = ''

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
        self.toolbar = self.iface.addToolBar(u'Spanish_Inspire_Catastral_Downloader')
        self.toolbar.setObjectName(u'Spanish_Inspire_Catastral_Downloader')

        socket.setdefaulttimeout(5)

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
        # self.dlg.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

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
            text=self.tr(u'&Spanish Inspire Catastral Downloader'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg.pushButton_select_path.clicked.connect(self.select_output_folder)
        self.dlg.pushButton_run.clicked.connect(self.download)
        self.dlg.pushButton_add_layers.clicked.connect(self.add_layers)
        self.dlg.comboBox_province.currentTextChanged.connect(self.on_combobox_changed)
        self.dlg.comboBox_province.currentTextChanged.connect(self.on_combobox_changed)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Spanish Inspire Catastral Downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_folder(self) -> None:
        """Select output folder"""

        self.dlg.lineEdit_path.clear()
        folder = QFileDialog.getExistingDirectory(self.dlg, "Select folder")
        self.dlg.lineEdit_path.setText(folder)

    def check_form(self, option: int) -> None:
        """Message for fields without information"""

        messages = {
            1: self.tr('You must complete the data of the province and municipality and indicate the download route.'),
            2: self.tr('You must select at least one cadastral entity to download.')
        }

        QgsMessageLog.logMessage(messages[option], 'SICD',
                                 level=Qgis.Warning)

        self.msgBar.pushMessage(messages[option], level=Qgis.Warning, duration=3)

    # Progress Download
    def reporthook(self, blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 1e2 / totalsize
            self.dlg.progressBar.setValue(int(percent))

    # Set Proxy
    def set_proxy(self):
        proxy_handler = request.ProxyHandler({
            'http': '%s:%s' % (_proxy, _port),
            'https': '%s:%s' % (_proxy, _port)
        })
        opener = request.build_opener(proxy_handler)
        request.install_opener(opener)
        return

    def unset_proxy(self):
        """ Unset Proxy """

        proxy_handler = request.ProxyHandler({})
        opener = request.build_opener(proxy_handler)
        request.install_opener(opener)
        return

    def encode_url(self, url):
        """ Encode URL Download """

        url = parse.urlsplit(url)
        url = list(url)
        # The Catastro ATOM feed replaces every non-ASCII character of the
        # municipality folder with a blank, so entries such as
        # "08221-SANT LLORENC SAVALL" or "08005-L'AMETLLA DEL VALLES" are
        # published with a double blank while the real folder on the server has
        # a single one. Collapsing runs of blanks (and trimming each segment)
        # makes those municipalities downloadable again.
        url[2] = parse.quote('/'.join(' '.join(part.split())
                                      for part in url[2].split('/')))
        encoded_link = parse.urlunsplit(url)
        return encoded_link

    def formatFolderName(self, foldername) -> str:
        """ """
        foldernameformat = foldername.replace(' ', "_")
        return foldernameformat

    def gml2geojson(self, input, output):
        """ Convert a GML to a GeoJSON file """

        try:
            connect_command = """ogr2ogr -f GeoJSON {} {} -a_srs EPSG:25830""".format(output, input)
            print("\n Executing: ", connect_command)
            process = subprocess.Popen(connect_command, shell=True)
            process.communicate()
            process.wait()
            QgsMessageLog.logMessage(f'09.1 Función gml2geojson()', 'SICD', level=Qgis.Info)
            QgsMessageLog.logMessage(f'09.2 Input {input}', 'SICD', level=Qgis.Info)
            QgsMessageLog.logMessage(f'09.3 GML {input} converted to {output}', 'SICD', level=Qgis.Info)

        except Exception as err:
            msg = self.tr("Error converting files to GML")
            QgsMessageLog.logMessage(f'{msg}', 'SICD', level=Qgis.Warning)
            self.msgBar.pushMessage(f'{msg}', level=Qgis.Warning, duration=3)
            raise
        return

    # ------------------------------------------------------------------
    # TLS helpers
    # ------------------------------------------------------------------
    def catastro_ca_path(self):
        """Path of the temporary PEM where the Catastro root CA is cached."""
        return os.path.join(tempfile.gettempdir(), 'sicd_catastro_root_ca.pem')

    def remember_root_ca(self, reply):
        """Cache the root CA of the Catastro chain if its fingerprint matches.

        The certificate is only stored when its SHA-256 fingerprint is exactly
        the one of the FNMT root documented in CATASTRO_ROOT_CA_SHA256, so this
        can never be used to trust an arbitrary certificate.
        """
        try:
            chain = reply.sslConfiguration().peerCertificateChain()
            if not chain:
                return False
            root = chain[-1]
            # Qt5 exposes the enum unscoped, Qt6 only through .Algorithm
            sha256 = getattr(QCryptographicHash, 'Sha256', None)
            if sha256 is None:
                sha256 = QCryptographicHash.Algorithm.Sha256
            digest = bytes(root.digest(sha256).toHex()).decode()
            if digest != CATASTRO_ROOT_CA_SHA256:
                return False
            with open(self.catastro_ca_path(), 'wb') as handle:
                handle.write(bytes(root.toPem()))
            return True
        except Exception:
            return False

    def on_ssl_errors(self, reply, errors):
        """Accept the Catastro chain when it is anchored on the known FNMT root."""
        if self.remember_root_ca(reply):
            QgsMessageLog.logMessage(
                '06.0 Cadena TLS de Catastro anclada en la raiz FNMT conocida; '
                'se acepta explicitamente (la raiz no esta en el almacen del sistema).',
                'SICD', level=Qgis.Info)
            reply.ignoreSslErrors()
        else:
            QgsMessageLog.logMessage(
                '06.0 Errores TLS no reconocidos: %s'
                % ', '.join(e.errorString() for e in errors),
                'SICD', level=Qgis.Critical)

    def ssl_context(self):
        """Default SSL context, extended with the cached Catastro root CA."""
        context = ssl.create_default_context()
        extra = self.catastro_ca_path()
        if os.path.exists(extra):
            try:
                context.load_verify_locations(cafile=extra)
            except Exception:
                pass
        return context

    def search_url(self, inecode_catastro, tipo, codtipo, wd):

        inecode_catastro = inecode_catastro.split(' - ')[0]
        CODPROV = inecode_catastro[0:2]
        ATOM = f'{ULR_CATASTRO}/INSPIRE/{tipo}/{CODPROV}/ES.SDGC.{codtipo}.atom_{CODPROV}.xml?tipo={tipo}&wd={wd}'

        req = QtNetwork.QNetworkRequest(QUrl(ATOM))
        self.manager_ATOM.get(req)

    def generate_download_url(self, reply):

        QgsMessageLog.logMessage(f'06.1 Genera url de descarga generate_download_url()', 'SICD', level=Qgis.Info)

        inecode_catastro = self.dlg.comboBox_municipality.currentText().split(' - ')[0]

        er = reply.error()

        if er != QtNetwork.QNetworkReply.NetworkError.NoError:
            # Without this branch a failed request left the plugin stuck at 0%
            # with no message at all (see issues #26, #27 and #28).
            QApplication.restoreOverrideCursor()
            txt = self.tr('Could not read the Catastro ATOM service')
            msg = f'{txt}: {reply.errorString()}'
            QgsMessageLog.logMessage(msg, 'SICD', level=Qgis.Critical)
            self.msgBar.pushMessage(msg, level=Qgis.Critical, duration=10)
            self.dlg.progressBar.setValue(0)
            return

        self.remember_root_ca(reply)

        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            response = str(bytes_string, 'iso-8859-1')
            root = ET.fromstring(response)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                try:
                    url_cadastre = entry.find('{http://www.w3.org/2005/Atom}id').text
                    QgsMessageLog.logMessage(f'06.2 {url_cadastre}', 'SICD', level=Qgis.Info)
                except:
                    msg = self.tr("The data set was not found.")
                    self.msgBar.pushMessage(msg, level=Qgis.Info, duration=3)

                if url_cadastre is not None and url_cadastre.endswith('{}.zip'.format(inecode_catastro)):
                    params = parse.parse_qs(parse.urlparse(reply.request().url().toString()).query)
                    tipo = params['tipo'][0]
                    wd = params['wd'][0]
                    self.create_download_file(inecode_catastro, tipo, url_cadastre, wd)
                    break

    def create_download_file(self, inecode_catastro, tipo, url, wd):

        QgsMessageLog.logMessage(f'07.1 Función create_download_file', 'SICD', level=Qgis.Info)
        QgsMessageLog.logMessage(
            f'07.2 Parámetros inecode_catastro {inecode_catastro}, tipo {tipo}, url {url}, wd {wd})',
            'SICD', level=Qgis.Info)

        self.data_dir = os.path.normpath(os.path.join(wd, inecode_catastro))

        QgsMessageLog.logMessage(f'07.1 {self.data_dir}', 'SICD', level=Qgis.Info)
        try:
            os.makedirs(self.data_dir)
            QgsMessageLog.logMessage(
                f'07.3 Creada  carpeta en {self.data_dir})', 'SICD', level=Qgis.Success)
        except OSError:
            pass

        zip_file = os.path.join(self.data_dir, "{}_{}.zip".format(inecode_catastro, tipo))  # poner fecha

        if not os.path.exists(zip_file):
            e_url = self.encode_url(url)
            try:
                self.retrieve_zip(e_url, zip_file)

                QgsMessageLog.logMessage(f"7.4 Ficheros descargados correctamente en {self.data_dir}", 'SICD',
                                         level=Qgis.Success)
                txt = self.tr('Files downloaded correctly in')
                msg = f'😎 {txt} <a href="file:///{self.data_dir}">{self.data_dir}</a>'
                self.msgBar.pushMessage(msg, level=Qgis.Success, duration=5)
                self.unzip_files(self.data_dir)

            except:
                shutil.rmtree(self.data_dir)
                raise
        else:
            QApplication.restoreOverrideCursor()
            txt1 = self.tr('The data set already exists in the folder')
            txt2 = self.tr('You must delete them first if you want to download them to the same location')
            msg = f'{txt1} <a href="file:///{self.data_dir}">{self.data_dir}</a>. {txt2} '

            QgsMessageLog.logMessage(msg, 'SICD', level=Qgis.Critical)

            self.msgBar.pushMessage(msg, level=Qgis.Critical)
            pass

    def retrieve_zip(self, url, zip_file):
        """Download `url` into `zip_file` reporting progress.

        Replaces request.urlretrieve() so that (a) the SSL context can include
        the Catastro root CA and (b) the payload is validated: the service
        answers with an HTML page (HTTP 200) when the path does not exist, which
        used to be saved as a corrupt .zip and failed silently later on.
        """
        handlers = [request.HTTPSHandler(context=self.ssl_context())]
        if (_proxy is not None and _proxy != "") and (_port is not None and _port != ""):
            handlers.append(request.ProxyHandler({'http': '%s:%s' % (_proxy, _port),
                                                  'https': '%s:%s' % (_proxy, _port)}))
        else:
            handlers.append(request.ProxyHandler({}))
        opener = request.build_opener(*handlers)

        block_size = 64 * 1024
        with opener.open(url, timeout=120) as response:
            content_type = (response.headers.get('Content-Type') or '').lower()
            total_size = int(response.headers.get('Content-Length') or 0)
            if 'text/html' in content_type:
                raise IOError(
                    'Catastro devolvio una pagina HTML en lugar de un ZIP para %s' % url)
            with open(zip_file, 'wb') as handle:
                block_number = 0
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    handle.write(chunk)
                    block_number += 1
                    self.reporthook(block_number, block_size, total_size)

        if not zipfile.is_zipfile(zip_file):
            os.remove(zip_file)
            raise IOError('El fichero descargado no es un ZIP valido: %s' % url)

    def unzip_files(self, wd):

        try:
            if os.path.isdir(wd):
                for zipfilecatastro in os.listdir(wd):
                    if zipfilecatastro.endswith('.zip'):
                        with zipfile.ZipFile(os.path.join(wd, zipfilecatastro), "r") as z:
                            z.extractall(wd)
                            QgsMessageLog.logMessage(f'08.1 Zip descomprimidos', 'SICD', level=Qgis.Info)

                self.dlg.pushButton_add_layers.setEnabled(1)
            else:
                msg = self.tr("Select at least one data set to download")
                self.msgBar.pushMessage(msg, level=Qgis.Critical)
                return
        except Exception as err:
            QgsMessageLog.logMessage(f'08.2 Error descomprimiendo: {err}', 'SICD', level=Qgis.Critical)
            self.msgBar.pushMessage(self.tr("An error occurred while decompressing the file."), level=Qgis.Warning, duration=3)

        QApplication.restoreOverrideCursor()

        self.dlg.progressBar.setValue(100)  # No llega al 100% aunque lo descargue,es random

        QApplication.restoreOverrideCursor()

    def add_layers(self):

        inecode_catastro = self.dlg.comboBox_municipality.currentText().split(' - ')
        zippath = self.dlg.lineEdit_path.text()
        wd = os.path.join(zippath, inecode_catastro[0])

        group_name = self.dlg.comboBox_municipality.currentText()
        project = QgsProject.instance()
        tree_root = project.layerTreeRoot()
        layers_group = tree_root.addGroup(group_name)

        for gmlfile in os.listdir(wd):
            if gmlfile.endswith('.gml'):
                layer_path = os.path.join(wd, gmlfile)
                file_name = os.path.splitext(gmlfile)[0]
                QgsMessageLog.logMessage(layer_path, 'SICD', level=Qgis.Info)
                gml_layer = QgsVectorLayer(layer_path, file_name, "ogr")
                project.addMapLayer(gml_layer, False)
                layers_group.addLayer(gml_layer)

        QgsMessageLog.logMessage("10. Capas cargadas", 'SICD', level=Qgis.Info)

    def run(self):
        """Run method that performs all the real work"""

        QgsMessageLog.logMessage(f"0. URL de Catastro {ULR_CATASTRO}", 'SICD', level=Qgis.Info)

        self.dlg.lineEdit_path.clear()
        self.dlg.comboBox_province.clear()
        self.dlg.comboBox_municipality.clear()

        self.obtener_provincias()

        self.dlg.checkBox_parcels.setChecked(0)
        self.dlg.checkBox_buildings.setChecked(0)
        self.dlg.checkBox_addresses.setChecked(0)

        # self.dlg.checkBox_load_layers.setChecked(0)

        self.dlg.pushButton_add_layers.setEnabled(0)

        # show the dialog
        self.dlg.progressBar.setValue(0)
        self.dlg.setWindowIcon(QIcon(':/plugins/Spanish_Inspire_Catastral_Downloader/icon.png'));
        self.dlg.show()

        # Run the dialog event loop
        result = exec_dialog(self.dlg)

        # See if OK was pressed
        if result: pass

    def on_combobox_changed(self):
        self.dlg.lineEdit_path.clear()
        self.dlg.checkBox_parcels.setChecked(0)
        self.dlg.checkBox_buildings.setChecked(0)
        self.dlg.checkBox_addresses.setChecked(0)
        self.dlg.pushButton_add_layers.setEnabled(0)

    def obtener_provincias(self):

        QgsMessageLog.logMessage("01.1 Obtenindo provincias (obtener_provincias)", 'SICD', level=Qgis.Info)

        self.manager_provincias = QtNetwork.QNetworkAccessManager()
        self.manager_provincias.finished.connect(self.rellenar_provincias)

        url = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json/ObtenerProvincias'

        QgsMessageLog.logMessage(f'01.2 URL JSON Provincias de Catastro {url}', 'SICD', level=Qgis.Info)

        req = QtNetwork.QNetworkRequest(QUrl(url))
        self.manager_provincias.get(req)

    def rellenar_provincias(self, reply):

        QgsMessageLog.logMessage("02. Rellenando provincias (rellenar_provincias)", 'SICD', level=Qgis.Info)
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            response = str(bytes_string, 'utf-8')
            response_json = json.loads(response)
            provincias = response_json['consulta_provincieroResult']['provinciero']['prov']

            list_provincias = [self.tr('Select a province...')]

            for provincia in provincias:
                list_provincias.append('{} - {}'.format(provincia['cpine'], provincia['np']))

            self.dlg.comboBox_province.addItems(list_provincias)
            self.dlg.comboBox_province.currentIndexChanged.connect(self.obtener_municipos)

    def obtener_municipos(self):

        try:
            self.manager_municipios = QtNetwork.QNetworkAccessManager()
            self.manager_municipios.finished.connect(self.rellenar_municipios)
            provincia_cod = self.dlg.comboBox_province.currentText()
            msg = f'03.1 Obteniendo municipios (obtener_municipios) de la provincia {provincia_cod}'
            QgsMessageLog.logMessage(msg, 'SICD', level=Qgis.Info)
            provincia = provincia_cod.split(' - ')[0]

            url = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejeroCodigos.svc/json/ObtenerMunicipiosCodigos?CodigoProvincia=' + str(
                provincia)

            QgsMessageLog.logMessage(f'03.2 URL JSON Municipios de Catastro de la {provincia_cod}:  {url}', 'SICD',
                                     level=Qgis.Info)

            req = QtNetwork.QNetworkRequest(QUrl(url))
            self.manager_municipios.get(req)
        except Exception as e:
            print(e)

    def rellenar_municipios(self, reply):

        er = reply.error()
        if er == QtNetwork.QNetworkReply.NetworkError.NoError:

            bytes_string = reply.readAll()
            response = str(bytes_string, 'utf-8')
            response_json = json.loads(response)
            list_municipios = []

            try:
                municipios = response_json['consulta_municipieroResult']['municipiero']['muni']
                QgsMessageLog.logMessage("04. Rellenando municipios (rellenar_municipios)", 'SICD', level=Qgis.Info)
                for municipio in municipios:
                    codigo_provincia = str(municipio['locat']['cd']).zfill(2)
                    codigo_municipio = str(municipio['locat']['cmc']).zfill(3)
                    codigo = codigo_provincia + codigo_municipio
                    list_municipios.append(codigo + ' - ' + municipio['nm'])
            except:
                pass

            self.dlg.comboBox_municipality.clear()
            self.dlg.comboBox_municipality.addItems(list_municipios)

    def download(self):
        """Download data funtion"""

        if self.dlg.comboBox_municipality.currentText() == '' or self.dlg.lineEdit_path.text() == '':
            self.check_form(1)
        elif not (
                self.dlg.checkBox_parcels.isChecked() or self.dlg.checkBox_buildings.isChecked() or self.dlg.checkBox_addresses.isChecked()):
            self.check_form(2)

        else:
            QgsMessageLog.logMessage("05 Inicio de descarga", 'SICD', level=Qgis.Info)
            try:
                QApplication.setOverrideCursor(QCursor(WAIT_CURSOR))
                inecode_catastro = self.dlg.comboBox_municipality.currentText()

                zippath = self.dlg.lineEdit_path.text()
                # wd = os.path.join(zippath , inecode_catastro.replace(' ', "_"))
                # wd = os.path.join(zippath, CODMUNI)

                QgsMessageLog.logMessage(f'05.1 Genera variables zippath {zippath}', 'SICD', level=Qgis.Info)

                proxy_support = request.ProxyHandler({})
                opener = request.build_opener(proxy_support)
                request.install_opener(opener)

                # Estabelcemos un proxy si lo ha definido el usuario
                try:
                    if (_proxy is not None and _proxy != "") and (_port is not None and _port != ""):
                        self.set_proxy()
                    else:
                        self.unset_proxy()
                except Exception as e:
                    QApplication.restoreOverrideCursor()
                    txt = self.tr('Error setting proxy')
                    msg = f"{txt} : {str(e)}"
                    self.msgBar.pushMessage(msg, level=Qgis.Warning, duration=3)
                    raise

                self.manager_ATOM = QtNetwork.QNetworkAccessManager()

                self.manager_ATOM.sslErrors.connect(self.on_ssl_errors)
                self.manager_ATOM.finished.connect(self.generate_download_url)

                if self.dlg.checkBox_parcels.isChecked():
                    self.search_url(inecode_catastro, 'CadastralParcels', 'CP', zippath)

                if self.dlg.checkBox_buildings.isChecked():
                    self.search_url(inecode_catastro, 'Buildings', 'BU', zippath)

                if self.dlg.checkBox_addresses.isChecked():
                    self.search_url(inecode_catastro, 'Addresses', 'AD', zippath)

            except Exception as e:
                QApplication.restoreOverrideCursor()
                self.dlg.pushButton_add_layers.setEnabled(0)
                self.msgBar.pushMessage(self.tr("Failed!")  + str(e), level=Qgis.Warning, duration=3)
