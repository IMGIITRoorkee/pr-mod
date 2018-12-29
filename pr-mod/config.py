class Config(object):

    # To set to environment variable for Oauth
    GITHUB_CLIENT_ID = 'a423dd70490484392542'
    GITHUB_CLIENT_SECRET = 'ace15039e4ee39d7c7db50c11435545677ef5777'
    GITHUB_USER = "Dragneel7"
    SECRET_KEY = 'can_you_guess_it_?'

    # For GitHub Enterprise
    GITHUB_BASE_URL = 'https://api.github.com/'
    GITHUB_AUTH_URL = 'https://github.com/login/oauth/'

    # OAuth Scope/Permissions
    # more info on scopes https://developer.github.com/v3/oauth/#scopes
    scope = "user, repo"
