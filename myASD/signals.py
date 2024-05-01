from django.dispatch import receiver
from allauth.account.signals import user_logged_in

@receiver(user_logged_in)
def handle_user_logged_in(request, user, **kwargs):
    print("User logged in signal received for user: %s", user.email)
    if user.has_perm('myASD.can_access_admin_page'):
        request.session['login_redirect_url'] = '/admin_page/'
    else:
        request.session['login_redirect_url'] = '/home/'
    print("login_redirect_url set to:", request.session.get('login_redirect_url'))