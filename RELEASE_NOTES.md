Django OAuth2 Server
====================

Author: Nicholas Herriot
Version: 0.1.1

Changes For Ras-OAuth2-Server
=============================

This is the first formal release of the OAuth2 server. Changes from the default server are:

* The 'info' endpoint to find out what the node supports and what version is available.
 
Known Issues For Ras-OAuth2-Server
==================================

* Not able to reset or set failed login attempts via the admin REST endpoint.
* Missing tests for admin REST endpoint.
* A potential issue while populating the DB via fixtures on CF deployment. This needs further research.
* Client ID and Client secret are ignored in curl requests for obtaining a token
 

