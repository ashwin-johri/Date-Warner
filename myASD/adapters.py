from allauth.account.adapter import DefaultAccountAdapter

class MyCustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Directly utilize the 'login_redirect_url' session variable for redirection,
        with a fallback to '/home/' if not set.
        """
        return request.session.get('login_redirect_url', '/home/')