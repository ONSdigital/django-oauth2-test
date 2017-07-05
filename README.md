[![Codeship Status for RichardKnop/go-oauth2-server](https://codeship.com/projects/38e5cdb0-71b0-0133-b926-06b1c29ec1d7/status?branch=master)](https://codeship.com/projects/116440)

[![Travis Status for RichardKnop/django-oauth2-server](https://travis-ci.org/RichardKnop/django-oauth2-server.svg?branch=master)](https://travis-ci.org/RichardKnop/django-oauth2-server)

Django OAuth2 Server
====================

Implementation of OAuth2 Server for Django. Feel free to fork this repository and contribute.

This code is taken from a git clone of: https://github.com/RichardKnop/django-oauth2-server/blob/master/README.md#scope



Written for Django 1.9 :)
* [Changes For Ras-OAuth2-Server](#Changes-For-Ras-OAuth2-Server)
    * [Basic Starting on Localhost](#Basic-Starting-Procedure-on-Local-Machine)
    * [Data fill Default Test Data](#Setup-Default-Data-for-ONS)
    * [Admin API](#Admin-API)
* [Grant Types](#grant-types)
    * [Authorization Code](#authorization-code)
    * [Implicit](#implicit)
    * [Client Credentials](#client-credentials)
    * [User Credentials](#user-credentials)
    * [Refresh Token](#refresh-token)
* [Scope](#scope)
* [Authentication](#authentication)
* [Contributing](#contributing)
    * [Installation](#installation)
    * [Configuration](#configuration)
    * [Running Tests](#running-tests)



Changes For Ras-OAuth2-Server
=============================

This documents changes implemented for the Ras-OAuth2-Server that allow this solution to be used with the microservice
framework at ONS.

Basic Starting Procedure on Local Machine
-----------------------------------------

* Migrate Tables. You need to have your settings setup to a valid DB which are in /prot/settings/default.py
```
    /> python manage.py migrate
```

* Add default data using Django fixtures. See next section for details.
```
    /> python manage.py loaddata apps/credentials/fixtures/ons_credentials.json
```

* Create your super user for the Django server. Note this is done automatically on Cloud Foundry
```
    /> python manage.py createsuperuser
```

* Start the server on your dev default port
```
    /> python manage.py runserver
```

Setup Default Data for ONS
--------------------------

Above and beyond what we do for the original setup there is a django fixtures file that can be run to populate the
database with 3 test client's and 1 test user. To run the fixture from the oauth2server directory do:

```
python manage.py loaddata apps/credentials/fixtures/ons_credentials.json
```

This sets up 3 clients which are:

* partyService@ons.gov.uk
* frontstageService@ons.gov.uk
* collectionInstrumentService@ons.gov.uk

And one test user which is:

* testuser@email.com

All with password 'password'.


Admin API
----------

The OAuth2 server now has an admin interface. This has it's own REST endpoint to allow a client with the correct
client_id and client_secret to interact with the Interface.

The endpoint is at /api/account/create and accepts [POST], but will accept a [GET] and query parameters.

* Mandatory Parameters

HTTP Basic Authentication  username: password
username:       This should be the username to populate the users of the OAuth2 server. It should be in an email format and will be checked to be unique
password:       This is a password for that user.
client_id:      This is the client_id making the request to use the admin interface API. This should be the same as the user in the authentication header
client_secret:  This is the password of the client_id.

```

curl -X POST http://localhost:8040/api/account/create/ -u ons@ons.gov:password -d 'username=testuser4@email.com&password=password&client_id=ons@ons.gov@client_secret=password'

```

* Optional Parameters

scope:          This is a list of coma delimited scopes used to provision this user. This would look like:

"scope": "foo bar respondent.read respondent.write"

```
-d 'username=testuser4@email.com&password=password&scope=foo&scope=bar&scope=respondent.read&scope=respondent.wirte ....
```


Good Version of CURL for grant_type = password
-------------------

curl -X POST  localhost:8000/api/v1/tokens/ -d 'grant_type=password&username=testuser@email.com&password=password&client_id=onc@onc.gov&client_secret=password'

For this to work you need to populate tables in admin to have :
client_id
client_secret
username
userpassword



Good Version of CURL for grant_type = authorization_code
-------------------

curl  localhost:8000/api/v1/tokens/ -d 'grant_type=authorization_code&client_id=onc@onc.gov&client_secret=password&code=263c9414-4709-4964-8ba1-91782cde6335'

For this to work you need to populate tables in admin to have :
client_id
client_secret
username
userpassword

You also need a valid access code to get your token. You could get this with:

http://localhost:8000/web/authorize/?response_type=code&client_id=onc%40onc.gov&redirect_uri=https://www.example.com&state=somestate


Cloud Foundry
=============

The application has manifest, Procfile and an init_db.sh script to allow it to be pushed to cloud foundry easily.

The manifest_develop_cloudfoundry.yml defines a basic server which needs a bouNd service called oauth-db. This will
dynamically pick a DB config from Cloud Foundry which are environment variables exposed at run time. You will need to
create a CF postgres service with this name.

The Procfile will migrate the database and on first load the init_db.sh script will create a super user. This shell
script is idempotent so can be deployed multiple times to the same system. The profile will then call up the runserver
command and run the system on default port 8080.

The manifest file also sets the DJANGO_SETTINGS_MODULE to the cloud_foundry_settings.py file which pics up all the
dynamic variables.

*TODO - To productionize this the server has to be bound to a WSGI server. e.g. [NGINX]( https://www.nginx.com/resources/wiki/)



Grant Types
===========

Authorization Code
------------------

http://tools.ietf.org/html/rfc6749#section-4.1

Insert test data:

```
$ python oauth2server/manage.py loaddata test_credentials
$ python oauth2server/manage.py loaddata test_scopes
```

Run the development web server:

```
$ python oauth2server/manage.py runserver
```

And you can now go to this page in your web browser:

```
http://localhost:8000/web/authorize/?response_type=code&client_id=testclient&redirect_uri=https://www.example.com&state=somestate
```

You should see a screen like this:

![Authorization page screenshot](https://raw.githubusercontent.com/RichardKnop/assets/master/django-oauth2-server/authorize_screenshot.png)

Click yes, you will be redirected to the redirect_uri and the authorization code will be in the query string. For example:

```
https://www.example.com/?code=cd45169cf6575f76d789f55764cb751b4d08274d&state=somestate
```

You can use it to get access token:

http://tools.ietf.org/html/rfc6749#section-4.1.3

```
$ curl -u testclient:testpassword localhost:8080/api/v1/tokens/ -d 'grant_type=authorization_code&code=cd45169cf6575f76d789f55764cb751b4d08274d'
```

You should get a response like:

```json
{
    "id": 1,
    "access_token": "00ccd40e-72ca-4e79-a4b6-67c95e2e3f1c",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "foo bar qux",
    "refresh_token": "6fd8d272-375a-4d8a-8d0f-43367dc8b791"
}
```

Implicit
--------

http://tools.ietf.org/html/rfc6749#section-4.2

Very similar to the authorization code but the token is returned in URL fragment.

Insert test data:

```
$ python oauth2server/manage.py loaddata test_credentials
$ python oauth2server/manage.py loaddata test_scopes
```

Run the development web server:

```
$ python oauth2server/manage.py runserver
```

And you can now go to this page in your web browser:

```
http://localhost:8080/web/authorize/?response_type=token&client_id=testclient&redirect_uri=https://www.example.com&state=somestate
```

You should see a screen like this:

![Authorization page screenshot](https://raw.githubusercontent.com/RichardKnop/assets/master/django-oauth2-server/authorize_screenshot.png)

Click yes, you will be redirected to the redirect_uri and the access token code will be in the URL fragment. For example:

```
https://www.example.com#access_token=66b80fb9d6630705bcea1c9be0df2a5f7f7a52bf&expires_in=3600&token_type=Bearer&state=somestate
```

User Credentials
----------------

http://tools.ietf.org/html/rfc6749#section-4.3

Insert test data:

```
$ python oauth2server/manage.py loaddata test_credentials
$ python oauth2server/manage.py loaddata test_scopes
```

Run the development web server:

```
$ python oauth2server/manage.py runserver
```

And you can now get a new access token:

```
$ curl -u testclient:testpassword localhost:8080/api/v1/tokens/ -d 'grant_type=password&username=testuser@example.com&password=testpassword'
```

You should get a response like:

```json
{
    "id": 1,
    "access_token": "00ccd40e-72ca-4e79-a4b6-67c95e2e3f1c",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "foo bar qux",
    "refresh_token": "6fd8d272-375a-4d8a-8d0f-43367dc8b791"
}
```

Client Credentials
------------------

http://tools.ietf.org/html/rfc6749#section-4.4

Insert test data:

```
$ python oauth2server/manage.py loaddata test_credentials
$ python oauth2server/manage.py loaddata test_scopes
```

Run the development web server:

```
$ python oauth2server/manage.py runserver
```

And you can now get token either using HTTP Basic Authentication:

```
$ curl -u testclient:testpassword localhost:8080/api/v1/tokens/ -d 'grant_type=client_credentials'
```

Or using POST body:

```
$ curl localhost:8000/api/v1/tokens/ -d 'grant_type=client_credentials&client_id=testclient&client_secret=testpassword'
```

You should get a response like:

```json
{
    "id": 1,
    "access_token": "00ccd40e-72ca-4e79-a4b6-67c95e2e3f1c",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "foo bar qux",
    "refresh_token": "6fd8d272-375a-4d8a-8d0f-43367dc8b791"
}
```

Refresh Token
-------------

Let's say you have created a new access token using the user credentials grant type. The response included a refresh token which you can use to get a new access token before your current access token expires.

```
$ curl -u testclient:testpassword localhost:8080/api/v1/tokens/ -d 'grant_type=refresh_token&refresh_token=55697efd4b74c980f2c638602556115bc14ca931'
```

And you get a new access token:

```json
{
    "id": 1,
    "access_token": "00ccd40e-72ca-4e79-a4b6-67c95e2e3f1c",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "foo bar qux",
    "refresh_token": "6fd8d272-375a-4d8a-8d0f-43367dc8b791"
}
```

Scope
=====

http://tools.ietf.org/html/rfc6749#section-3.3

Scope is quite arbitrary. Basically it is a space delimited case-sensitive string where each part defines a specific access range.

You can define your scopes and insert them into tokens_oauthscope table, is_default flag can be used to specify default scope.

Authentication
==============

Now that you have obtained an access token, you can make requests to protected resources.

In order to require authentication for a view, wrap it in the authentication_required decorator:

```python
from apps.tokens.decorators import authentication_required

@authentication_required("some_scope")
def some_view(request, *args, **kwargs):
    ...
```

Contributing
============

In order to contribute to this project, fork it and make a pull request. I will review and accept it.

All tests must be passing in order for the pull request to be accepted.

Installation
------------

Clone the repository:

```
$ git clone https://github.com/RichardKnop/django-oauth2-server.git
```

Create a virtual environment and install requirements:

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Create a local.py file and insert correct configuration details:

```
$ cp oauth2server/proj/settings/local.example.py oauth2server/proj/settings/local.py
$ nano cp oauth2server/proj/settings/local.py
```

Sync the database:

```
$ python oauth2server/manage.py syncdb
```

Configuration
-------------

These are the current configuration options:

```python
OAUTH2_SERVER = {
    'ACCESS_TOKEN_LIFETIME': 3600,
    'AUTH_CODE_LIFETIME': 3600,
    'REFRESH_TOKEN_LIFETIME': 1209600,
    'IGNORE_CLIENT_REQUESTED_SCOPE': False,
}
```

* ACCESS_TOKEN_LIFETIME: lifetime of an access token in seconds
* AUTH_CODE_LIFETIME: lifetime of an authorization code in seconds
* REFRESH_TOKEN_LIFETIME: lifetime of a refresh token in seconds
* IGNORE_CLIENT_REQUESTED_SCOPE: if true, client requested scope will be ignored

Running Tests
-------------

```
$ python oauth2server/manage.py test
```
