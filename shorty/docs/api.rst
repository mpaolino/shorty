API
===

Schema
------
All API access is over HTTP/S. All data is serialized as JSON.
All data that's required to create or modify resources must be send in a 
HTML form encoded manner, this will be shown in the documentation as
"Input". All optional data that is needed to customize requests,
as in filtering data must be sent as GET arguments. This will be
shown as "Parameters" in the documentation.


All timestamps are returned in ISO 8601 format::

    YYYY-MM-DD HH:MM:SSZ



Status Code Definitions
=======================
Each Status-Code is described below, including a description of which method(s)
it can follow and any metainformation required in the response.


Successful 2xx
--------------

------
200 OK
------
The request has succeeded. The information returned with the response is
dependent on the method used in the request, for example:

GET an entity corresponding to the requested resource is sent in the response::

	HTTP/1.1 200 OK

	{
	   "id": ...
	   ...
	}

-----------
201 Created
-----------
The request has been fulfilled and resulted in a new resource being created::

	HTTP/1.1 201 Created

----------------
Client Error 4xx
----------------
There are four possible types of client errors on API calls that receive
request bodies:


-------------
404 Not Found
-------------
Sending invalid Request-URI will result in a 404 Not Found::

	HTTP/1.1 404 Not Found



----------------------
405 Method Not Allowed
----------------------
Sending invalid method will result in a 405 Method Not Allowed. 
The response must include an Allow header containing a list of valid
methods for the requested resource::

   HTTP/1.1 405 Method Not Allowed
   Content-Lenght: 41 
   Allow: PUT, GET, HEAD, DELETE
   


------------------------
422 Unprocessable Entity
------------------------
Sending invalid data will result in a 422 Unprocessable Entity response::

   HTTP/1.1 422 Unprocessable Entity
   Content-Length: 149

   { 
     "message": "Validation Failed",
     "errors": [
                {
                  "resource": "someresource",
                  "field": "title",
                  "code": "missing_field"
                }
               ]
   }



All error objects have resource and field properties so that your client can
tell what the problem is. There’s also an error code to let you know what is
wrong with the field. These are the possible validation error codes:

missing
    This means a resource does not exist.
missing_field
    This means a required field on a resource has not been set.
invalid
    This means the formatting of a field is invalid. The documentation for that resource should be able to give you more specific information.
already_exists
     This means another resource has the same value as this field. This can happen in resources that must have some unique key.
   
If resources have custom validation errors, they will be documented with the resource.


----------------
Server Error 5xx
----------------
Response status codes beginning with the digit "5" indicate cases in which the
server is incapable of performing the request.

-------------------------
500 Internal Server Error
-------------------------
The server encountered an unexpected condition which prevented it from fulfilling
the request.


HTTP Verbs
==========
Where possible, this API strives to use appropriate HTTP verbs for each action.


GET
    Used for retrieving resources.
POST
    Used for creating and updating resources, or performing custom actions. 
DELETE
    Used for deleting resources.


Resources
=========

Expand (and redirect) URL
-------------------------

[GET] /:encoded

----------
Parameters
----------
encoded
    *string* short URL token to decode an redirect to URL target

--------
Response
--------
| Status: 302 Found
| Location: http://longurltoshorten.com/path/to/some/resource


URL register
------------

[POST] - /api/:user/url

----------
Parameters
----------
user
    *string* Username, owner of URL

-----
Input
-----
target
    *string* Long URL to shorten

--------
Response
--------
Status: 200 OK

::

    {
        "url": "http://127.0.0.1:5000/api/ideal/url/2Bkmh3", 
        "user": "ideal", 
        "short": "2Bkmh3", 
        "target": "http://longurltoshorten.com/path/to/some/resource", 
        "creation_date": "2012-10-06 18:26:40.900545"
    }



Get all URLs for user
---------------------
[GET] /api/:user/url

----------
Parameters
----------
page
    *integer* Page number of paginated results

--------
Response
--------
Status: 200 OK

:: 

    {
      "page_number": 1, 
      "page_count": 1, 
      "results_per_page": 500, 
      "user": "ideal", 
      "urls": [
        {
          "url": "http://127.0.0.1:5000/api/ideal/url/dc8tvV", 
          "short": "dc8tvV", 
          "target": "http://cosa.ideal.com.uy", 
          "creation_date": "2012-10-06 14:19:25.165651"
        }, 
        {
          "url": "http://127.0.0.1:5000/api/ideal/url/2Bkmh3", 
          "short": "2Bkmh3", 
          "target": "http://longurltoshorten.com/path/to/some/resource", 
          "creation_date": "2012-10-06 18:26:40.900545"
        }
      ]



Get URL details
---------------

[GET] /api/:user/url/:short

--------
Response
--------
Status: 200 OK

::

    {
      "url": "http://127.0.0.1:5000/api/ideal/url/2Bkmh3", 
      "user": "ideal", 
      "short": "2Bkmh3", 
      "target": "http://longurltoshorten.com/path/to/some/resource", 
      "creation_date": "2012-10-06 18:26:40.900545"
    }



URL Expansion reports
---------------------

[GET|POST] /api/:user>/url/:short>/expansions

----------------
Parameters/Input
----------------
page
    *integer* Page of paginated results
from
    *iso8601 date* Only show expansions that happened before this date, inclusive.
to
    *iso8601 date*. Only show expansions that happened until date, inclusive.

--------
Response
--------

::

    {
      "short": "2Bkmh3", 
      "target": "http://longurltoshorten.com/path/to/some/resource", 
      "url": "http://127.0.0.1:5000/2Bkmh3", 
      "page_count": 1,
      "creation_date": "2012-10-06 18:26:40.900545", 
      "page_number": 1, 
      "user": "ideal", 
      "results_per_page": 500
      "expansions": [
        {
          "ua_name": "cURL 7.21.6", 
          "detection_date": "2012-10-06 18:56:30.662412", 
          "ua_family": "cURL", 
          "ua_string": "curl/7.21.6 (x86_64-pc-linux-gnu) libcurl/7.21.6 OpenSSL/1.0.0e zlib/1.2.3.4 libidn/1.22 librtmp/2.3", 
          "ua_company": "team Haxx", 
          "os_family": "Linux", 
          "ua_type": "Library"
        }, 
        {
          "ua_name": "cURL 7.21.6", 
          "detection_date": "2012-10-06 18:56:34.797673", 
          "ua_family": "cURL", 
          "ua_string": "curl/7.21.6 (x86_64-pc-linux-gnu) libcurl/7.21.6 OpenSSL/1.0.0e zlib/1.2.3.4 libidn/1.22 librtmp/2.3", 
          "ua_company": "team Haxx", 
          "os_family": "Linux", 
          "ua_type": "Library"
        } 
      ] 
    }



Get QR for short URL
--------------------

[GET|POST] /api/:user/url/:short/qr

----------------
Parameters/Input
----------------
Note::

      All the parameters can be encoded en the request URL or in the POST form.
      For a more detailed information on each parameter please refer to the qrlib
      documentation.

application
    Application intended for generated QR, 'interior' or 'exterior'. Defaults to 'interior'.
appsize
    Application size intented for generated QR, 'small', 'medium' or 'small'. Defaults to 'small'.
style
    String with style to apply to QR modules. Defaults to 'default'.
stylecolor
    6 digit hex color to apply to main style. Defaults to '#000000' (pure black)
innereyestyle
    String with style to apply to inner eyes of QR. Defaults to 'default'.
outereyestyle
    String with style to apply to outer eyes of QR. Defaults to 'default'.
innereyecolor
    6 digit hex color to apply to inner eyes of QR. Defaults to '#000000' (pure black) 
outereyecolor
    6 digit hex color to apply to outer eyes of QR. Defaults to '#000000' (pure black)
bgcolor
    6 digit hex color to apply to QR background. Defaults to '#FFFFFF' (pure white)
qrformat 
    String with QR format to generated. Supportin 'GIF', 'PNG', 'JPEG' and 'PDF'. Defaults to 'PDF'.

--------
Response
--------
| Status: 200 OK
| Content-Type: application/pdf
| <binary data>
|
| Status: 200 OK
| Content-Type: image/gif 
| <binary data>
|
| Status: 200 OK
| Content-Type: image/png
| <binary data>
| 
| Status: 200 OK
| Content-Type: image/jpeg
| <binary data>
