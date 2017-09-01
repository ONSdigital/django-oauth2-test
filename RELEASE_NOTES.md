Django OAuth2 Server
====================

Author: Nicholas Herriot
Version: 0.1.2

Changes For Ras-OAuth2-Server
=============================

Changes from release 0.1.1 server are:

* Failed login and unverified account messages are returned when obtaining a token for a user if they have a blocked account or a non
verified account.
* A user who does not have a verified account will not get a token. This is set via the admin interface or from the admin UI.
 
Known Issues For Ras-OAuth2-Server
==================================

* Not able to reset or set failed login attempts via the admin REST endpoint.
* Missing tests for admin REST endpoint.
* A potential issue while populating the DB via fixtures on CF deployment. This needs further research.
* Client ID and Client secret are ignored in curl requests for obtaining a token. They are passed as part of HTTP basic authentication.
 

