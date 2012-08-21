======
Shorty
======

URL shortening service.


How it works
============

This service works by storing long URLs in a database and assigning an unique
integer to it. Then a short URL for that integer is generated using a prime
length alphabet and a hash function that reverses some of the first bits of the
number (to provide some obscurity) and then converts it to the alphabet base.


How many URLs can you short?
============================
Short answer, as much as you like.

With and alphabet of 53 chars to encode numbers, and let's say
35 maximum chars on the short URL key, there's 53^35=2.23x10^60 different
codes you can generate. 
Since the algorithm feeds from a database auto incremented
integer (assuring atomicity operation and uniqueness), we can
encode more URLs than there are in Internet in the forseable future.
As of 12 of September 2011 there's an estimate of 1 trillion webpages
or 1x10^12 pages.

Another example to be less dramtic, with 6 chars-long keys there are 
22164361129 possible URLs that can be shortened, more than enough
to comply with the demand of the reachable audience using the service.

Also if URLs can expire, numbers can be reused to further increase the
total number of URLs encoded. Also the lenght of the key can be extended
as much as we like, limited only by the maximum number of integers the database
or counter can come up with.
