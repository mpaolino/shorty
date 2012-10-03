shorty API
==========

There are onlky two levels of permissions, public or private. 
Restrictions are enforced at HTTP/IP level.


Decode short URL (public) 
==========================
[GET|POST] /:encoded

Input
=====
encoded = JhgnK8 (short url token)

Response
--------
Redirection to long URL 


Register short URL (private)
============================

POST /api/register

Input
-----
{
  "url": "http://so.me/long/url/that/is/to/be/shorten",
  "owner": "one-owner",
}

Response
--------
Status: 200 OK


Reports (private)
=================

POST /api/reports

Input
-----
{
  "short-token": "JhgnK8",
  "owner": "one-owner",
  ["page": 1]
}


Response
--------
Status: 200 OK
<Protocolbuffer serialized object with results as described in .proto in
 libs/protobuffer/reports.proto>


QR generation
=============

Accepts an URL and returns a PDF with a QR, if the URL is not registered 
it will previously register it.

[POST|GET] /api/generateqr


Input
-----
{
  "url": "http://so.me/long/url/that/is/to/be/shorten",
  "owner": "one-owner",
}

Response
--------
HTTP binary transfer with PDF file.
