import ast

import requests
from behave import given, then, when


# ----------------------------------------------------------------------------------------------------------------------
# Common 'given' steps
# ----------------------------------------------------------------------------------------------------------------------
# TODO: Basic test to see if OAuth server is running. Needs improving at some point!
@given('the Django OAuth2 server is running')
def step_impl(context):
    context.response = requests.get(
        context.oauth_domain + context.oauth_port + '/admin'
    )
    context.execute_steps(u'''
        then the response status code is 200
    ''')


@given('valid user and client credentials')
def step_impl(context):
    context.credentials = {
        'grant_type': 'password',
        'username': 'testuser@email.com',
        'password': 'password',
        'client_id': 'onc@onc.gov',
        'client_secret': 'password'
    }


@given('a {type} with a value of "{invalid_value}"')
def step_impl(context, attribute, invalid_value):
    context.execute_steps(u'''
        given valid user and client credentials
    ''')
    # Now alter the given key to the invalid value
    context.credentials[attribute] = invalid_value


@given('an existing user')
def step_impl(context):
    context.execute_steps(u'''
        given valid user and client credentials
    ''')


@given('an existing user with an invalid password')
def step_impl(context):
    context.execute_steps(u'''
        given a password with a value of "INVALID_PASSWORD"
    ''')


# ----------------------------------------------------------------------------------------------------------------------
# Common 'when' steps
# ----------------------------------------------------------------------------------------------------------------------
@when('a POST request is made to \'/api/v1/tokens/\'')
def step_impl(context):
    context.response = requests.post(
        context.token_url,
        data=context.credentials
    )


@when('a POST request is made to \'/api/v1/tokens/\' is repeated a total of {attempt_count} times')
def step_impl(context, attempt_count):
    for _ in range(int(attempt_count)):
        context.execute_steps(u'''
            when a POST request is made to \'/api/v1/tokens/\'
        ''')
        assert context.response


# ----------------------------------------------------------------------------------------------------------------------
# Common 'then' steps
# ----------------------------------------------------------------------------------------------------------------------
@then('the response returns "{property_name}" information')
def step_impl(context, property_name):
    assert context.response.headers['Content-Type'] == 'application/json'
    response_text = ast.literal_eval(context.response.text)
    assert response_text[property_name]


@then('the response status code is {status_code}')
def step_impl(context, status_code):
    assert context.response.status_code == int(status_code)


@then('information is returned saying "{text}"')
def step_impl(context, text):
    response_text = ast.literal_eval(context.response.text)
    assert response_text['detail'] == text
