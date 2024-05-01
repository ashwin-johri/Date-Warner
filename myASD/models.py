from django.db import models
from django.conf import settings
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
import json

class Submission(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    PLATFORM_CHOICES = [
        ('bumble', 'Bumble'),
        ('hinge', 'Hinge'),
        ('tinder', 'Tinder'),
        ('other', 'Other'),
    ]


    reporter_username = models.CharField(max_length=255, editable=False)
    dating_platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    other_dating_platform = models.CharField(max_length=255, blank=True, null=True)
    reported_username = models.CharField(max_length=255)
    experience_rating = models.IntegerField()
    situation_explanation = models.TextField()
    uploaded_file_urls = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, null=True)

    def set_uploaded_files(self, urls):
        self.uploaded_file_urls = json.dumps(urls)
        self.save()
        print("Saving URLs:", self.uploaded_file_urls)  # Debug print

    def get_uploaded_file_paths(self):
        print("Uploaded file keys in model from view: ", self.uploaded_file_urls)
        try:
            file_keys = json.loads(self.uploaded_file_urls) if self.uploaded_file_urls else []
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return []

        print("File keys to process:", file_keys)

        return file_keys

    def __str__(self):
        return f"Submission by {self.reporter_username} - {self.reported_username} on {self.dating_platform}"



    class Meta:
        permissions = [
            ("can_access_admin_page", "Can access admin page"),
        ]