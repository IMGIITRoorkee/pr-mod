class Config(object):
    # To set to environment variable for Oauth
    GITHUB_CLIENT_ID = '<GITHUB_CLIENT_ID>'
    GITHUB_CLIENT_SECRET = '<GITHUB_CLIENT_SECRET>'
    GITHUB_USER = "<ADMIN_GITHUB_HANDLE>"
    SECRET_KEY = 'can_you_guess_it_?'

    # For GitHub Enterprise
    GITHUB_BASE_URL = 'https://api.github.com/'
    GITHUB_AUTH_URL = 'https://github.com/login/oauth/'

    # OAuth Scope/Permissions
    # more info on scopes https://developer.github.com/v3/oauth/#scopes
    scope = "user, repo"

    # Allow Deny rules for github users
    # Default (for anonymous users) - allow or deny
    # If deny, then we will check for allowed users
    users = {
        "default": "deny",
        "allow": [""],
        "deny": []
    }

    # Server IP address. eg, https://localhost, https://192.168.0.0
    SERVER_IP = "<SERVER_IP>"
