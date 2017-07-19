# Spanish Inspire Catastral Downloader <img src="icon.png" height="42" width="42">

Plugin de QGIS para la descarga de datos catastrales de parcelas, edificios y direcciones de España. La descarga usa el servicio ATOM según la Directiva Inspire. (<a href='http://www.catastro.minhap.gob.es/webinspire/index.html'>http://www.catastro.minhap.gob.es/webinspire/index.html</a>)

QGIS Plugin for the download of cadastral data of parcels, buildings and addresses of Spain. The download uses the ATOM service according to the Inspire Directive. (<a href='http://www.catastro.minhap.gob.es/webinspire/index_eng.html'>http://www.catastro.minhap.gob.es/webinspire/index_eng.html</a>)

## Instalar plugin

El complemento puede ser instalado desde el menú <b>Complementos>Administrar e instalar complementos</b> de QGIS. Para localizar de forma rápida el complemento puede introducirse el término <i>"catastro"</i> en la herramienta de búsqueda.

Igualmente puede descargarse el archivo zip desde este repositorio y descomprimirlo en la carpeta de plugins de QGIS según el sistema operativo.

<ul>
<li>Windows: <i>c:\Users\username\.qgis2\python\plugins</i></li>
<li>Mac: <i>/Users/username/.qgis2/python/plugins</i></li>
<li>Linux: <i>/home/username/.qgis2/python/plugins</i></li>
</ul>
Donde tendremos que reemplazar “username” por nuestro usuario.

## Uso

Tras su instalación el plugin puede ser ejecutado desde la barra de herramientas o bien desde el menú <b>Complementos>Descarga Catrastro Inspire</b>

Una vez ejecutado el complemento se debe <b>obligatoriamente</b>:
<ul>
<li>Seleccionar la provincia</li>
<li>Seleccionar el municipio</li>
<li>Indicar la ruta local de descarga</li>
<li>Indicar el conjunto de capas a descargar: Parcelas Catastrales, Edificios y/o Direcciones</li>
</ul>

Si se desea añadir las capas GML descargardas al proyecto QGIS activo se debe marcar la casilla correspondiente.
