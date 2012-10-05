======
Shorty
======

Webservice para acortado de URLs y generación de QRs.


Metodos
=======


[GET|POST] /api/getqr
---------------------
Un acceso a esta ruta dará de alta una URL (si no está ya creada) utilizando
en el referrer HTTP de la consulta.

El referrer por ahora esta limitado al Portal Ceibal, por lo que sólo
se aceptarán URLs que comiencen con:

http://ceibal.edu.uy 
https://ceibal.edu.uy 
http://www.ceibal.edu.uy 
https://www.ceibal.edu.uy


[GET|POST] /api/reports
-----------------------
A travéz de esta ruta de podrán obtener reportes de accesos a los QRs
con algunos detalles de las consultas.


Párametros
----------
url
short_token
