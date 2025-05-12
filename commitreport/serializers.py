from rest_framework import serializers
from datetime import datetime

class CommitRequestSerializer(serializers.Serializer):
    """
    Serializer for request parameters to fetch git commits
    """
    repo_path = serializers.CharField(
        help_text="Path to repository (local path or remote URL)"
    )
    repo_type = serializers.ChoiceField(
        choices=['local', 'github', 'bitbucket'],
        default='github',
        help_text="Type of repository"
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Filter commits by username"
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Filter commits by email"
    )
    start_date = serializers.DateTimeField(
        required=False,
        help_text="Filter commits from this date (ISO format)"
    )
    end_date = serializers.DateTimeField(
        required=False,
        help_text="Filter commits until this date (ISO format)"
    )
    branch = serializers.CharField(
        required=False,
        default='main',
        help_text="Branch to fetch commits from"
    )
    # For remote repositories authentication
    auth_token = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Authentication token for GitHub/Bitbucket"
    )
    auth_username = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Authentication username for Bitbucket"
    )

class CommitSerializer(serializers.Serializer):
    """
    Serializer for git commit data
    """
    commit_hash = serializers.CharField()
    author_name = serializers.CharField()
    author_email = serializers.CharField()
    date = serializers.DateTimeField()
    message = serializers.CharField()
    files_changed = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )