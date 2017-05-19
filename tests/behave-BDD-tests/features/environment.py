def before_feature(context, feature):
    """Set up context variables in Behave step files before a feature file is executed.

    # TODO: This should be moved to some sort of environmental config file.

    :param context: Behave object used in scope of feature
    :param feature: Behave mandatory param
    :return: None
    """
    # Dev endpoint setup
    context.oauth_domain = 'http://127.0.0.1:'
    context.oauth_port = '8000'
    oauth_token_endpoint = '/api/v1/tokens/'
    oauth_authorization_endpoint = '/web/authorize/'

    context.token_url = context.oauth_domain + context.oauth_port + oauth_token_endpoint
    context.authorization_url = context.oauth_domain + context.oauth_port + oauth_authorization_endpoint

    context.client_id = 'onc@onc.gov'
    context.client_secret = 'password'
    context.username = 'testuser@email.com'
    context.password = 'password'
