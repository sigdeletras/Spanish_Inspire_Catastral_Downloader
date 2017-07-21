# Spanish Inspire Catastral Downloader <img src="icon.png" height="42" width="42">

Plugin de QGIS para la descarga de datos catastrales de parcelas, edificios y direcciones de España. La descarga usa el servicio ATOM según la Directiva Inspire. (<a href='http://www.catastro.minhap.gob.es/webinspire/index.html'>http://www.catastro.minhap.gob.es/webinspire/index.html</a>)

<i>QGIS Plugin for the download of cadastral data of parcels, buildings and addresses of Spain. The download uses the ATOM service according to the Inspire Directive. (<a href='http://www.catastro.minhap.gob.es/webinspire/index_eng.html'>http://www.catastro.minhap.gob.es/webinspire/index_eng.html</a>)</i>

Para más información puede consultarse la entrada en [http://www.sigdeletras.com/2017/plugin-de-qgis-para-descarga-de-datos-catastrales-inspire](SIGdeletras.com)

## Instalar plugin

El complemento puede ser instalado desde el menú <b>Complementos>Administrar e instalar complementos</b> de QGIS. Para localizar de forma rápida el complemento puede introducirse el término <i>"catastro"</i> en la herramienta de búsqueda.

<img src="help/search.PNG" width="70%">

Igualmente, puede descargarse el archivo zip desde este repositorio y <b>descomprimirlo en la carpeta de plugins de QGIS</b> según el sistema operativo.

<ul>
<li>Windows: <i>c:\Users\username\.qgis2\python\plugins</i></li>
<li>Mac: <i>/Users/username/.qgis2/python/plugins</i></li>
<li>Linux: <i>/home/username/.qgis2/python/plugins</i></li>
</ul>
Donde tendremos que reemplazar “username” por nuestro usuario.

## Uso

Tras su instalación el plugin puede ser ejecutado desde la barra de herramientas o bien desde el menú <b>Complementos>Descarga Catrastro Inspire</b> o bien <b>Spanish Inspire Catastral Downloader</b> si tenemos instalado QGIS en otro idioma.

<img src="help/ui.PNG" width="50%">

Una vez ejecutado el complemento se debe <b>obligatoriamente</b>:
<ul>
<li>Seleccionar la provincia</li>
<li>Seleccionar el municipio</li>
<li>Indicar la ruta local de descarga</li>
<li>Indicar el conjunto de capas a descargar: Parcelas Catastrales, Edificios y/o Direcciones</li>
</ul>

Si se desea añadir las capas GML descargardas al proyecto QGIS activo se debe marcar la casilla correspondiente.

### Conjunto de datos INSPIRE de la Dirección General de Catastro

Los archivos geográficos (GML) contenidos en cada conjunto de datos son:

- **Conjunto de Datos de Parcela Catastral** (CP Cadastral Parcel)
  - *CadastralParcel*. Parcela catastral.
  - *CadastralZoning*. Manzanas en suelo urbano o a los polígonos en suelo rústico.
- **Conjunto de Datos de Edificios** (BU Buildings)
  - *Building*. Edificio. 
  - *BuildingPart*. Cada una de las construcciones de una parcela catastral que tiene volumen homogéneo, y pueden ser sobre y bajo rasante.
  - *OtherConstructions*. Piscinas que contienen el atributo OtherConstructionNatureValue calificado cómo openAirPool.
- **Conjunto de Datos de Direcciones** (AD Addresses)
  - *Address*. Geometría del punto donde georreferencia la dirección física (centroide de la parcela o entrada del portal)

El PDF con la descripción completa de la estructura de datos puede consultarse en el siguiente [enlace](http://www.catastro.minhap.es/webinspire/documentos/Conjuntos%20de%20datos.pdf)

<img src="help\cadastral_layers.PNG" width="95%">

## 2DO

- Añadir barra de proceso que avise de la descarga.
- Probar en Linux y revisar el tema del PATH
- Posibilidad de applicar simbología a las capas
- ¿Traducir campos?
- Preparlo para QGIS3
- Ordenar el listado de municipios por código
