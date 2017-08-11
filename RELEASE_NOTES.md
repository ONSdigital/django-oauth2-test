Django OAuth2 Server
====================

Author: Nicholas Herriot
Version: 0.1.0

Changes For Ras-OAuth2-Server
=============================

This is the first formal release of the OAuth2 server. Changes from the default server are:

* An admin interface to allow adding, deleting and updating a user.
* Ability to set the verification of a user via the admin REST endpoint.

 
Known Issues For Ras-OAuth2-Server
==================================

* Not able to reset or set failed login attempts via the admin REST endpoint.
* Missing tests for admin REST endpoint.
* A potential issue while populating the DB via fixtures on CF deployment. This needs further research. 

