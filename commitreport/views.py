from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommitRequestSerializer, CommitSerializer
from .services.git_service import GitService
from .services.github_service import GitHubService
from .services.bitbucket_service import BitbucketService

class CommitsView(APIView):
    """
    API endpoint to fetch git commits from repositories
    """
    
    def post(self, request):
        """
        Fetch commits based on request parameters
        
        Request body parameters:
        - repo_path: Path to repository (local path or remote URL)
        - repo_type: Type of repository (local, github, bitbucket)
        - username: Filter commits by username (optional)
        - email: Filter commits by email (optional)
        - start_date: Filter commits from this date (optional)
        - end_date: Filter commits until this date (optional)
        - branch: Branch to fetch commits from (optional, defaults to 'main')
        - auth_token: Authentication token for GitHub/Bitbucket (optional)
        - auth_username: Authentication username for Bitbucket (optional)
        """
        serializer = CommitRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        repo_path = data['repo_path']
        repo_type = data['repo_type']
        username = data.get('username')
        email = data.get('email')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        branch = data.get('branch', 'main')
        auth_token = data.get('auth_token')
        auth_username = data.get('auth_username')
        
        try:
            commits = []
            
            if repo_type == 'local':
                # Use GitService for local repositories
                git_service = GitService()
                commits = git_service.get_commits(
                    repo_path=repo_path,
                    branch=branch,
                    username=username,
                    email=email,
                    start_date=start_date,
                    end_date=end_date
                )
            elif repo_type == 'github':
                # Use GitHubService for GitHub repositories
                github_service = GitHubService()
                commits = github_service.get_commits(
                    repo_path=repo_path,
                    branch=branch,
                    username=username,
                    email=email,
                    start_date=start_date,
                    end_date=end_date,
                    auth_token=auth_token
                )
            elif repo_type == 'bitbucket':
                # Use BitbucketService for Bitbucket repositories
                bitbucket_service = BitbucketService()
                commits = bitbucket_service.get_commits(
                    repo_path=repo_path,
                    branch=branch,
                    username=username,
                    email=email,
                    start_date=start_date,
                    end_date=end_date,
                    auth_username=auth_username,
                    auth_token=auth_token
                )
            else:
                return Response(
                    {"error": f"Unsupported repository type: {repo_type}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Serialize the commit data
            commits_serializer = CommitSerializer(commits, many=True)
            
            return Response({
                "repository": repo_path,
                "branch": branch,
                "filters": {
                    "username": username,
                    "email": email,
                    "start_date": start_date,
                    "end_date": end_date
                },
                "commits_count": len(commits),
                "commits": commits_serializer.data
            })
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )