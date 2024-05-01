from django.contrib.auth.models import User
from django.urls import reverse


from django.test import TestCase

class UserInfoTestCase(TestCase):
    def test_user_email_exists_on_screen(self):
        test_user = User.objects.create(username = 'test_user', email= 'test_user@gmail.com')
        self.client.force_login(test_user)
        response = self.client.get(reverse('home'))
        self.assertContains(response, test_user.email)


class NavigationTest(TestCase):
    def test_button_redirect(self):
        response = self.client.get(reverse('home'))  
        self.assertEqual(response.status_code, 200)

# class HomeViewTest(TestCase):
#     def test_home_view_render(self):
#         response = self.client.get(reverse('home'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, '<h1>Welcome, user!</h1>')
#         self.assertContains(response, '<form action="{% url \'submit\' %}" method="post">')
#         self.assertContains(response, '<select name="dating_platform">')

        # # Check if the select element is within the form
        # self.assertContains(response, '<form action="{% url \'submit\' %}" method="post">')
        # self.assertContains(response, '<select name="dating_platform">')

class FormValidationTest(TestCase):
    def test_invalid_form_data(self):
        invalid_data = {
            'dating_platform': '', 
            'reported_username': 'example_user',
            'experience_rating': 20, #out of bounds
            'situation_explanation': '', 
        }

        response = self.client.post(reverse('submitted'), data=invalid_data)
        self.assertEqual(response.status_code, 405)
 
class UrlNamesTest(TestCase):
    def test_admin_url(self):
        url = reverse('admin:index')
        self.assertEqual(url, '/admin/')

    def test_accounts_url(self):
        url = reverse('account_login')
        self.assertEqual(url, '/accounts/login/')
    
    def test_home_url_name(self):
        url = reverse('home')
        self.assertEqual(url, '/home/')
    
    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(url, '/')

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(url, '/logout/')

    def test_submit_url(self):
        url = reverse('submit')
        self.assertEqual(url, '/submit/')

    def test_submitted_url_name(self):
        url = reverse('submitted')
        self.assertEqual(url, '/submitted/')

    def test_admin_page_url(self):
        url = reverse('admin_page')
        self.assertEqual(url, '/admin_page/')

    def test_my_reviews_url(self):
        url = reverse('my_reviews')
        self.assertEqual(url, '/my_reviews/')

    def test_update_submission_status_url(self):
        url = reverse('update_submission_status', args=[1])
        self.assertEqual(url, '/submission/update/1/')

    def test_google_oauth_callback_url(self):
        url = reverse('google_oauth_callback')
        self.assertEqual(url, '/accounts/google/login/callback/')
