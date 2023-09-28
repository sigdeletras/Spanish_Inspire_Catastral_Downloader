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
#from PyQt5 import QtCore, QtGui, QtWidgets
import os
import shutil
#TimeOut para la descarga de 5 segundos
import socket
import subprocess
import urllib
import urllib.request
from urllib.parse import parse_qs, urlparse
import xml.etree.ElementTree as ET
import zipfile
from urllib import parse, request

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import Qt

#from PyQt5.QtWidgets import QDialog
#For Debug
try:
	from pydevd import *
except ImportError:
	None
 
try:
	from PyQt5 import QtNetwork, uic
	from PyQt5.QtCore import *
	from PyQt5.QtGui import *
	from PyQt5.QtWidgets import *
	from qgis.core import Qgis
	QT_VERSION=5
	os.environ['QT_API'] = 'pyqt5'
except:
	from PyQt4 import QNetwork, uic
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
	from qgis.core import QGis as Qgis
	from qgis.core import QgsMapLayerRegistry
	from qgis.gui import QgsMessageBar
	QT_VERSION=4

import os.path

from qgis.core import *

# from .listamuni import *
#import resources
from .resources import *
from .Spanish_Inspire_Catastral_Downloader_dialog import \
    Spanish_Inspire_Catastral_DownloaderDialog

codprov = ''
codmuni = ''

from .Config import _port, _proxy


class Spanish_Inspire_Catastral_Downloader:
	"""QGIS Plugin Implementation."""

	def __init__(self , iface):
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
			self.plugin_dir ,
			'i18n' ,
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

		socket.setdefaulttimeout(5)

	# noinspection PyMethodMayBeStatic
	def tr(self , message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('Spanish_Inspire_Catastral_Downloader' , message)

	def add_action(
			self ,
			icon_path ,
			text ,
			callback ,
			enabled_flag=True ,
			add_to_menu=True ,
			add_to_toolbar=True ,
			status_tip=None ,
			whats_this=None ,
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
		action = QAction(icon , text , parent)
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
				self.menu ,
				action)

		self.actions.append(action)

		return action

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/Spanish_Inspire_Catastral_Downloader/icon.png'
		self.add_action(
			icon_path ,
			text=self.tr(u'&Spanish Inspire Catastral Downloader') ,
			callback=self.run ,
			parent=self.iface.mainWindow())

		self.dlg.pushButton_select_path.clicked.connect(self.select_output_folder)
		self.dlg.pushButton_run.clicked.connect(self.download)


	def unload(self):
		"""Removes the plugin menu item and icon from QGIS GUI."""
		for action in self.actions:
			self.iface.removePluginMenu(
				self.tr(u'&Spanish Inspire Catastral Downloader') ,
				action)
			self.iface.removeToolBarIcon(action)
		# remove the toolbar
		del self.toolbar

	def select_output_folder(self):
		"""Select output folder"""

		self.dlg.lineEdit_path.clear()
		folder = QFileDialog.getExistingDirectory(self.dlg , "Select folder")
		self.dlg.lineEdit_path.setText(folder)

	def not_data(self):
		"""Message for fields without information"""
		try:
			self.msgBar.pushMessage('Completar datos de municipio o indicar la ruta de descarga' , level=Qgis.Info, duration=3)
		except:
			self.msgBar.pushMessage('Completar datos de municipio o indicar la ruta de descarga' , level=QgsMessageBar.INFO, duration=3)

	#Progress Download
	def reporthook(self,blocknum, blocksize, totalsize):
		readsofar = blocknum * blocksize
		if totalsize > 0:
			percent = readsofar * 1e2 / totalsize
			self.dlg.progressBar.setValue(int(percent))

	#Set Proxy
	def set_proxy(self):
		proxy_handler = request.ProxyHandler({
			'http': '%s:%s' % (_proxy,_port),
			'https': '%s:%s' % (_proxy,_port)
		})
		opener = request.build_opener(proxy_handler)
		request.install_opener(opener)
		return

	#Unset Proxy
	def unset_proxy(self):
		proxy_handler = request.ProxyHandler({})
		opener = request.build_opener(proxy_handler)
		request.install_opener(opener)
		return

	#Encode URL Download
	def EncodeUrl(self,url):
		url = parse.urlsplit(url)
		url = list(url)
		url[2] = parse.quote(url[2])
		encoded_link = parse.urlunsplit(url)
		return encoded_link

	def formatFolderName(self,foldername):
		foldernameformat = foldername.replace(' ', "_")
		return foldernameformat

	def gml2geojson(self, input, output):
		""" Convert a GML to a GeoJSON file """
		try:
			connect_command = """ogr2ogr -f GeoJSON {} {} -a_srs EPSG:25830""".format(output, input)
			print ("\n Executing: ", connect_command)
			process = subprocess.Popen(connect_command, shell=True)
			process.communicate()
			process.wait()
			print ("GML", input, "converted to", output + ".geojson")
		except Exception as err:
			print ("Failed to convert to GeoJSON from GML")
			raise
		return

	def download(self):
		"""Dowload data funtion"""

		if self.dlg.comboBox_municipality.currentText() == '' or self.dlg.lineEdit_path.text() == '':
			self.not_data()

		else:

			try:
				QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
				inecode_catastro = self.dlg.comboBox_municipality.currentText()

				zippath = self.dlg.lineEdit_path.text()

				# wd = os.path.join(zippath , inecode_catastro.replace(' ', "_"))
				wd = os.path.join(zippath , codmuni)
				

				proxy_support = urllib.request.ProxyHandler({})
				opener = urllib.request.build_opener(proxy_support)
				urllib.request.install_opener(opener)

				#Estabelcemos un proxy si lo ha definido el usuario
				try:
					if (_proxy!= None and _proxy!= "") and (_port!= None and _port!= ""):
						self.set_proxy()
					else:
						self.unset_proxy()
				except Exception as e:
					QApplication.restoreOverrideCursor()
					try:
						self.msgBar.pushMessage("Error estableciendo el proxy : "+ str(e) , level=Qgis.Warning, duration=3)
					except:
						self.msgBar.pushMessage("Error estableciendo el proxy : "+ str(e) , level=QgsMessageBar.WARNING, duration=3)
					raise


				self.manager_ATOM = QtNetwork.QNetworkAccessManager()
				self.manager_ATOM.finished.connect(self.genera_url_descarga)
				# download de Cadastral Parcels
				if self.dlg.checkBox_parcels.isChecked():
					self.busca_url(inecode_catastro, 'CadastralParcels','CP', wd)

				# download de Buildings
				if self.dlg.checkBox_buildings.isChecked():
					self.busca_url(inecode_catastro, 'Buildings', 'BU', wd)
					

				# download de Addresses
				if self.dlg.checkBox_addresses.isChecked():
					self.busca_url(inecode_catastro, 'Addresses', 'AD', wd)

				try:
					self.msgBar.pushMessage("Finished!" , level=Qgis.Success, duration=3)
				except:
					self.msgBar.pushMessage("Finished!" , level=QgsMessageBar.SUCCESS, duration=3)

			except Exception as e:
				QApplication.restoreOverrideCursor()
				try:
					self.msgBar.pushMessage("Failed! "+ str(e) , level=Qgis.Warning , duration=3)
				except:
					self.msgBar.pushMessage("Failed! "+ str(e) , level=QgsMessageBar.WARNING , duration=3)
				return

	def busca_url(self, inecode_catastro, tipo, codtipo, wd):	
		inecode_catastro = inecode_catastro.split(' - ')[0]
		codprov = inecode_catastro[0:2]

		ATOM = 'https://www.catastro.minhap.es/INSPIRE/{}/{}/ES.SDGC.{}.atom_{}.xml?tipo={}&wd={}'.format(tipo, codprov, codtipo, codprov, tipo, wd)
		req = QtNetwork.QNetworkRequest(QUrl(ATOM))
		self.manager_ATOM.get(req)


	def genera_url_descarga(self, reply):
		inecode_catastro = self.dlg.comboBox_municipality.currentText().split(' - ')[0]
		er = reply.error()
		if er == QtNetwork.QNetworkReply.NetworkError.NoError:
			bytes_string = reply.readAll()
			response = str(bytes_string, 'iso-8859-1')
			root = ET.fromstring(response)
			for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
				try:
					url = entry.find('{http://www.w3.org/2005/Atom}id').text
				except:
					try:
						self.msgBar.pushMessage("No se ha encontrado el conjunto de datos." , level=Qgis.Info, duration=3)
					except:
						self.msgBar.pushMessage("No se ha encontrado el conjunto de datos." , level=QgsMessageBar.INFO, duration=3)

				if url is not None and url.endswith('{}.zip'.format(inecode_catastro)):
						params = parse_qs(urlparse(reply.request().url().toString()).query)
						tipo = params['tipo'][0]
						wd = params['wd'][0]
						self.crea_fichero_descarga(inecode_catastro, tipo, url, wd)
						break
				else:
					try:
						self.msgBar.pushMessage("No se ha encontrado el conjunto de datos." , level=Qgis.Info, duration=3)
					except:
						self.msgBar.pushMessage("No se ha encontrado el conjunto de datos." , level=QgsMessageBar.INFO, duration=3)


	def crea_fichero_descarga(self, inecode_catastro, tipo, url, wd):
		try:
			os.makedirs(wd)
			print('Crea fichero', wd)
		except OSError:
			pass

		zip = os.path.join(wd , "{}_{}.zip".format(inecode_catastro, tipo))  # poner fecha
		
		if not os.path.exists(zip):
			e_url=self.EncodeUrl(url)
			try:
				urllib.request.urlretrieve(e_url , zip, self.reporthook)
				self.descomprime_ficheros(wd)
			except:
				shutil.rmtree(wd)
				raise
		else:
			try:
				self.msgBar.pushMessage("El conjunto de datos ya existe en la carpeta de descarga." , level=Qgis.Info, duration=3)
			except:
				self.msgBar.pushMessage("El conjunto de datos ya existe en la carpeta de descarga." , level=QgsMessageBar.INFO, duration=3)


	def descomprime_ficheros(self, wd):
		## Descomprime los zips
		if os.path.isdir(wd):
			for zipfilecatastro in os.listdir(wd):
				if zipfilecatastro.endswith('.zip'):
					with zipfile.ZipFile(os.path.join(wd , zipfilecatastro) , "r") as z:
						z.extractall(wd)

			#Convert gml2geojson
			for geojsonfile in os.listdir(wd):
				if geojsonfile.endswith('.gml'):
					input = os.path.join(wd, geojsonfile)
					output, ext = os.path.splitext(input)
					output = output + '.geojson'
					self.gml2geojson(input, output)
		else:
			try:
				self.msgBar.pushMessage("Seleccione al menos un dataset para descargar." , level=Qgis.Info)
			except:
				self.msgBar.pushMessage("Seleccione al menos un dataset para descargar." , level=QgsMessageBar.INFO)
			return

		if self.dlg.checkBox_load_layers.isChecked() and os.path.isdir(wd):
			try:
				## Descomprime los zips
				try:
					self.msgBar.pushMessage(u"Convirtiendo GML a GeoJSON. Según el peso de los archivos esto puede llevarse su tiempo..." , level=Qgis.Info, duration=4)
				except:
					self.msgBar.pushMessage(u"Convirtiendo GML a GeoJSON. Según el peso de los archivos esto puede llevarse su tiempo..." , level=QgsMessageBar.INFO, duration=4)	   
				## Carga los GeoJSON
				for geojsonfile in os.listdir(wd):
					if geojsonfile.endswith('.geojson'):
						layer = self.iface.addVectorLayer(os.path.join(wd , geojsonfile) , "" ,
														"ogr")

				try:
					self.msgBar.pushMessage("Ficheros descomprimido correctamente." , level=Qgis.Info, duration=3)
				except:
					self.msgBar.pushMessage("Fichero descomprimido correctamente." , level=QgsMessageBar.INFO, duration=3)

			except:
				try:
					self.msgBar.pushMessage("Error descomprimiendo el fichero." , level=Qgis.Warning , duration=3)
				except:
					self.msgBar.pushMessage("Error descomprimiendo el fichero." , level=QgsMessageBar.WARNING , duration=3)
				QApplication.restoreOverrideCursor()
		self.dlg.progressBar.setValue(100)#No llega al 100% aunque lo descargue,es random

		QApplication.restoreOverrideCursor()


	def run(self):
		"""Run method that performs all the real work"""

		self.dlg.lineEdit_path.clear()

		self.dlg.comboBox_province.clear()
		self.dlg.comboBox_municipality.clear()
		self.obtener_provincias()

		self.dlg.checkBox_parcels.setChecked(0)
		self.dlg.checkBox_buildings.setChecked(0)
		self.dlg.checkBox_addresses.setChecked(0)

		# show the dialog
		self.dlg.progressBar.setValue(0)
		self.dlg.setWindowIcon(QIcon (':/plugins/Spanish_Inspire_Catastral_Downloader/icon.png')); 
		self.dlg.show()

		# Run the dialog event loop
		result = self.dlg.exec_()

		# See if OK was pressed
		if result:pass


	def obtener_provincias(self):
		self.manager_provincias = QtNetwork.QNetworkAccessManager()
		self.manager_provincias.finished.connect(self.rellenar_provincias)
		
		url = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json/ObtenerProvincias'
		req = QtNetwork.QNetworkRequest(QUrl(url))
		self.manager_provincias.get(req)
	

	def rellenar_provincias(self, reply):
		er = reply.error()
		if er == QtNetwork.QNetworkReply.NetworkError.NoError:
			bytes_string = reply.readAll()
			response = str(bytes_string, 'utf-8')
			response_json = json.loads(response)
			provincias = response_json['consulta_provincieroResult']['provinciero']['prov']

			listProvincias = ['Seleccione una provincia...']
			for provincia in provincias:
				listProvincias.append('{} - {}'.format(provincia['cpine'], provincia['np']) )

			self.dlg.comboBox_province.addItems(listProvincias)
			self.dlg.comboBox_province.currentIndexChanged.connect(self.obtener_municipos)

	def obtener_municipos(self):
		try:
			self.manager_municipios = QtNetwork.QNetworkAccessManager()
			self.manager_municipios.finished.connect(self.rellenar_municipios)
			provincia = self.dlg.comboBox_province.currentText()
			provincia = provincia.split(' - ')[0]
			url = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejeroCodigos.svc/json/ObtenerMunicipiosCodigos?CodigoProvincia=' + str(provincia)
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
			listMunicipios = []
			try:
				municipios = response_json['consulta_municipieroResult']['municipiero']['muni']
				for municipio in municipios:
					codigo_provincia = str(municipio['locat']['cd']).zfill(2)
					codigo_municipio = str(municipio['locat']['cmc']).zfill(3)
					codigo = codigo_provincia + codigo_municipio
					listMunicipios.append(codigo + ' - ' + municipio['nm'])
			except:
				pass

			self.dlg.comboBox_municipality.clear()
			self.dlg.comboBox_municipality.addItems(listMunicipios)
