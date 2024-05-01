from django.contrib import admin
from django.urls import path, include
from myASD.views import *
from myASD.views import google_oauth_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('myASD/', include('myASD.urls')),
    path('home/', HomePageView.as_view(), name='home'),
    path('', LoginPageView.as_view(), name = 'login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('submit/', SubmissionView.as_view(), name='submit'),
    path('submitted/',SubmittedView.as_view(), name='submitted'),
    path('admin_page/', AdminPageView.as_view(), name='admin_page'),
    path('my_reviews/', MySubmissionsView.as_view(), name='my_reviews'),
    path('anonymous_all/', BlankPageView.as_view(), name='anonymous_all'),

    path('about_us/', AboutUsView.as_view(), name='about_us'),
    path('submission/update/<int:pk>/', UpdateSubmissionStatusView.as_view(), name='update_submission_status'),
    path('submission/resolve/<int:pk>/', ResolveSubmissionStatusView.as_view(), name='resolve_submission_status'),
    path('delete-submission/<int:submission_id>/', DeleteSubmissionView.as_view(), name='delete_submission'),
    path('mark-notification-read/<int:notification_id>/', mark_notification_read, name='mark-notification-read'),
    path('accounts/google/login/callback/', google_oauth_redirect, name='google_oauth_callback'),
    path('review_details/<int:pk>/', MySubmissionsExpandedView.as_view(), name='my_submission_expanded'),
    path('admin_review_details/<int:pk>/', AdminSubmissionExpandedView.as_view(), name='admin_reviews_expanded'),
    path('inbox/notifications/', include('notifications.urls')),
    path('generate_presigned_url/', GeneratePresignedUrlView.as_view(), name='generate_presigned_url')

]

