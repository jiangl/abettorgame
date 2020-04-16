from django.http import HttpResponseRedirect
import pdb

class AuthenticateUser(object):
    """
        Check if the user is logged in
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def check_is_authenticated(self, request):
        pdb.set_trace()
        is_authenticated = request.session.get('is_authenticated')

        if not is_authenticated:
            HttpResponseRedirect(reverse('index'))

        return None