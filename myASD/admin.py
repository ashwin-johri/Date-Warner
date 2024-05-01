from django.contrib import admin
from .models import Submission
from django.utils.html import format_html
from django.template.defaultfilters import truncatechars


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('reported_username', 'dating_platform', 'experience_rating', 'file_link','short_situation_explanation')

    def file_link(self, obj):
        if obj.uploaded_file_urls:
            return format_html("<a href='{url}' target='_blank'>Download File</a>", url=obj.uploaded_file_urls)
        return "No file"
    file_link.short_description = 'Uploaded File'

    def short_situation_explanation(self, obj):
        return truncatechars(obj.situation_explanation, 100)

    short_situation_explanation.short_description = 'Experience Explanation'


admin.site.register(Submission, SubmissionAdmin)
