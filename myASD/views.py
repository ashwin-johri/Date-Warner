import json
import logging
import requests
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LogoutView
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from notifications.signals import notify
from storages.backends.s3boto3 import S3Boto3Storage
import boto3

from django.http import HttpResponseBadRequest

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from asdProject import settings
from myASD.models import Submission

# Create your views here.


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

logger = logging.getLogger('myApp')


@login_required
def google_oauth_redirect(request):
    if request.user.groups.filter(name='site admin').exists():
        # If user is admin, redirect to admin screen
        return redirect(reverse('admin_page'))
    else:
        # If user is not admin, redirect to regular screen
        return redirect(reverse('home'))


class HomePageView(TemplateView):
    template_name = 'home.html'

    def dispatch(self, request, *args, **kwargs):
        login_redirect_url = request.session.pop('login_redirect_url', None)
        print(f"HOME PAGE RAN! {login_redirect_url}")
        logging.info(f"HOME PAGE {login_redirect_url}")
        if login_redirect_url and not request.user.is_superuser:
            return redirect(login_redirect_url)

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return redirect('/home/')


class LoginPageView(TemplateView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        logger.debug(f"Dispatch called for user: {request.user}")
        if request.user.is_superuser:
            logger.debug(f"User {request.user.email} does not have permission, redirecting to home")
            logger.info(f"Logged into home")
            print("Logged into home")
            return redirect('/home/')
        if request.user.is_authenticated:
            logger.debug(f"User {request.user.email} is authenticated")
            login_redirect_url = request.session.pop('login_redirect_url', None)
            if login_redirect_url:
                return redirect(login_redirect_url)
            # If there's no dynamic redirect URL, proceed with permission-based redirection.
            if request.user.has_perm('myASD.can_access_admin_page'):
                print("Logged into admin")
                logger.debug(f"User {request.user.email} has permission, redirecting to admin_page")
                return redirect('/admin_page/')
            else:
                logger.debug(f"User {request.user.email} does not have permission, redirecting to home")
                return redirect('/home/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated or user.is_superuser:
            google_account = SocialAccount.objects.filter(user=user, provider='google').first()
            if google_account:
                data['google_username'] = google_account.extra_data.get('name')
                data['google_email'] = google_account.extra_data.get('email')
        return data




class CustomLogoutView(LogoutView):
    """
    Custom logout view that adds a logout message.
    """
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class SubmissionView(View):
    def post(self, request, *args, **kwargs):
        # Common method to handle data extraction and saving
        print("Request FILES:", request.FILES)  # Debug output to inspect files in the request
        dating_platform = request.POST.get('dating_platform')
        other_dating_platform = request.POST.get('other_dating_platform', '')
        reported_username = request.POST.get('reported_username')
        experience_rating = request.POST.get('experience_rating')
        situation_explanation = request.POST.get('situation_explanation')
        uploaded_files = request.FILES.getlist('uploaded_files')
        file_keys = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    file_name = uploaded_file.name
                    saved_path = default_storage.save(file_name, uploaded_file)
                    print("key being stored: " + saved_path)
                    file_keys.append(saved_path)
                except Exception as e:
                    print("Error saving file:", e)
        else:
            print("No files found in the request.")

        for file_key in file_keys:
            print("key from views: " + file_key)

        keys_json = json.dumps(file_keys)

        # urls = []
        # if uploaded_files:
        #     for uploaded_file in uploaded_files:
        #         try:
        #             file_name = default_storage.save(uploaded_file.name, uploaded_file)
        #             file_url = default_storage.url(file_name)
        #             urls.append(file_url)
        #         except Exception as e:
        #             print("Error saving file:", e)
        #             continue
        # else:
        #     print("No files found in the request.")

        # print("Generated URLs:", urls)
        #urls_json = json.dumps(urls)
        # print("JSON URLs:", urls_json)

        # Use transaction.atomic to ensure all or nothing is saved
        with transaction.atomic():
            submission = Submission(
                reporter_username=request.user.username,
                dating_platform=dating_platform,
                other_dating_platform=other_dating_platform,
                reported_username=reported_username,
                experience_rating=experience_rating,
                situation_explanation=situation_explanation,
                uploaded_file_urls=keys_json
            )
            submission.save()
            #print("Saved submission with URLs:", submission.get_uploaded_files())
            print("Saved submission with URLs:", submission.get_uploaded_file_paths())

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            #return JsonResponse({'message': 'Files uploaded successfully', 'urls': urls}, status=200)
            return JsonResponse({'message': 'Files uploaded successfully', 'keys': file_keys}, status=200)
        else:
            # Redirect for non-AJAX requests
            return redirect('submitted')


class SubmittedView(TemplateView):
    template_name = 'submitted.html'

    def dispatch(self, request, *args, **kwargs):
        login_redirect_url = request.session.pop('login_redirect_url', None)
        if login_redirect_url:
            return redirect(login_redirect_url)
        return super().dispatch(request, *args, **kwargs)


def mark_notification_read(request, notification_id):
    notification = request.user.notifications.get(id=notification_id)
    notification.mark_as_read()
    return JsonResponse({'success': True})


class MySubmissionsView(TemplateView):
    template_name = 'my_reviews.html'
    context_object_name = 'submissions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submissions = Submission.objects.filter(reporter_username=self.request.user.username)
        username_not_none = self.request.user.username != ''
        if self.request.user.is_authenticated:
            notifications = self.request.user.notifications.unread()
            context['notifications'] = notifications

        # Filter submissions based on form data
        status = self.request.GET.get('status')
        platform = self.request.GET.get('platform')
        reported_username = self.request.GET.get('reported_username')

        if status:
            submissions = submissions.filter(status=status)
        if platform:
            submissions = submissions.filter(dating_platform=platform)
        if reported_username:
            submissions = submissions.filter(reported_username__icontains=reported_username)

        context['submissions'] = submissions
        context['username_not_none'] = username_not_none

        return context


class BlankPageView(TemplateView):
    template_name = 'anonymous_all.html'


class AboutUsView(TemplateView):
    template_name = 'about_us.html'


class DeleteSubmissionView(View):
    def post(self, request, submission_id):
        if 'delete_submission' in request.POST:
            try:
                submission = Submission.objects.get(id=submission_id)
                # Check if the user is authorized to delete the submission
                if submission.reporter_username == request.user.username:
                    submission.delete()
                    return redirect('my_reviews')  # Redirect to a suitable page after deletion
                else:
                    return HttpResponseBadRequest("You are not authorized to delete this submission.")
            except Submission.DoesNotExist:
                return HttpResponseBadRequest("Submission does not exist.")
        else:
            return HttpResponseBadRequest("Invalid form data.")


class MySubmissionsExpandedView(DetailView):
    model = Submission
    template_name = 'review_details.html'
    context_object_name = 'submission'

    def get(self, request, *args, **kwargs):
        # Handle GET requests
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        submission_id = kwargs['pk']
        return HttpResponseRedirect(reverse('my_submission_expanded', kwargs={'pk': submission_id}))


class AdminPageView(UserPassesTestMixin, ListView):
    model = Submission
    template_name = 'admin_page.html'
    context_object_name = 'submissions'
    permission_required = 'myASD.can_access_admin_page'

    def test_func(self):
        return self.request.user.has_perm('myASD.can_access_admin_page')

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply filtering based on form data
        reporter_username = self.request.GET.get('reporter_username')
        reported_username = self.request.GET.get('reported_username')
        dating_platform = self.request.GET.get('dating_platform')
        status = self.request.GET.get('status')

        if reporter_username:
            queryset = queryset.filter(reporter_username__icontains=reporter_username)
        if reported_username:
            queryset = queryset.filter(reported_username__icontains=reported_username)
        if dating_platform:
            queryset = queryset.filter(dating_platform=dating_platform)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class AdminSubmissionExpandedView(UserPassesTestMixin, ListView):
    model = Submission
    template_name = 'admin_review_details.html'
    context_object_name = 'submission'
    permission_required = 'myASD.can_access_admin_page'

    def test_func(self):
        return self.request.user.has_perm('myASD.can_access_admin_page')

    def get(self, request, *args, **kwargs):
        # Handle GET requests
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("good things?")
        submission_id = kwargs['pk']
        url = reverse('update_submission_status', kwargs={'pk': submission_id})

        return HttpResponseRedirect(reverse('update_submission_status', kwargs={'pk': submission_id}))


class UpdateSubmissionStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'myASD.can_access_admin_page'  # Ensure the user has the appropriate permission

    def get(self, request, *args, **kwargs):
        # Handle GET requests here if needed
        submission_id = kwargs.get('pk')
        submission = get_object_or_404(Submission, pk=submission_id)
        # Extract new status and admin notes from the POST request
        new_status = submission.status
        re_admin_notes = submission.admin_notes

        if new_status == Submission.STATUS_CHOICES[0][0]:
            submission.status = 'in_progress'
            submission.save()
            try:
                user = User.objects.get(username=submission.reporter_username)
                notify.send(

                    sender=request.user,
                    recipient=user,
                    verb='Submission status updated',
                    description='Your submission\'s status has been updated from new to in progress.'
                )
                messages.success(request, 'Submission status updated and user notified.')
            except User.DoesNotExist:
                messages.error(request, "User does not exist")
        # Render a template or perform any necessary actions for GET requests
        return render(request, 'admin_review_details.html', {'submission': submission})

    def post(self, request, *args, **kwargs):
        submission_id = kwargs.get('pk')
        submission = get_object_or_404(Submission, pk=submission_id)
        # Extract new status and admin notes from the POST request
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        old_status = submission.status

        status_changed = old_status != new_status
        notes_changed = submission.admin_notes != admin_notes and admin_notes != ''

        submission.admin_notes = admin_notes
        submission.save()
        if status_changed or notes_changed:
            if status_changed:
                submission.status = new_status
            if notes_changed:
                submission.admin_notes = admin_notes
            submission.save()

            # Construct notification message
            message = f"Your submission's status has been updated."
            if status_changed:
                message += f" Status changed from {old_status} to {new_status}."
            if notes_changed:
                message += f" Admin notes: {admin_notes}"
            try:
                user = User.objects.get(username=submission.reporter_username)
                notify.send(
                    sender=request.user,
                    recipient=user,
                    verb='Submission status updated',
                    description=message
                )
                messages.success(request, 'Submission status updated and user notified.')
            except User.DoesNotExist:
                messages.error(request, "User does not exist")
        else:
            messages.info(request, 'No changes detected in submission status or admin notes.')

        return redirect('admin_page')

        # Don't Redirect back to the admin page after processing


class ResolveSubmissionStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'myASD.can_access_admin_page'  # Ensure the user has the appropriate permission

    def get(self, request, *args, **kwargs):
        # Handle GET requests here if needed
        submission_id = kwargs.get('pk')
        submission = get_object_or_404(Submission, pk=submission_id)
        # Render a template or perform any necessary actions for GET requests
        return render(request, 'admin_review_details.html', {'submission': submission})

    def post(self, request, *args, **kwargs):
        submission_id = kwargs.get('pk')
        submission = get_object_or_404(Submission, pk=submission_id)

        # Extract new status and admin notes from the POST request
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        # Update the submission object if the new status is valid
        submission.status = 'resolved'
        submission.admin_notes = admin_notes
        submission.save()
        try:
            user = User.objects.get(username=submission.reporter_username)
            notify.send(
                sender=request.user,
                recipient=user,
                verb='Submission status updated',
                description=f'Your submission {submission} status changed from {new_status} to resolved. '
                            f'Admin notes:{admin_notes}'
            )
            messages.success(request, 'Submission status updated and user notified.')
        except User.DoesNotExist:
            messages.error(request, "User does not exist")

        return redirect('admin_page')


class GeneratePresignedUrlView(View):
    def get(self, request, *args, **kwargs):
        file_key = request.GET.get('file_key')
        print("key from presignedurlview: " + file_key)
        if not file_key:
            return JsonResponse({'error': 'Missing file key'}, status=400)

        s3_client = boto3.client('s3',
                                 region_name=settings.AWS_S3_REGION_NAME,
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        try:
            presigned_url = s3_client.generate_presigned_url('get_object',
                                                             Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                     'Key': file_key},
                                                             ExpiresIn=3600)  # Link expires in 1 hour
            return JsonResponse({'url': presigned_url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
