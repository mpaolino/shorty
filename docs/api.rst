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

POST /register

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

POST /reports

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

