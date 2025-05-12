from github import Github
from datetime import datetime

class GitHubService:
    """
    Service for working with GitHub repositories
    """
    
    def get_commits(self, repo_path, branch='main', username=None, email=None, 
                    start_date=None, end_date=None, auth_token=None):
        """
        Get commits from a GitHub repository
        
        Args:
            repo_path: Path to the repository in format 'username/repo'
            branch: Branch to fetch commits from
            username: Filter commits by author username
            email: Filter commits by author email
            start_date: Filter commits from this date
            end_date: Filter commits until this date
            auth_token: GitHub authentication token
            
        Returns:
            List of commit data dictionaries
        """
        try:
            # Initialize GitHub API client
            if auth_token:
                gh = Github(auth_token)
            else:
                gh = Github()
            
            # Format repo path correctly
            if 'github.com/' in repo_path:
                repo_path = repo_path.split('github.com/')[-1]
                # Remove .git extension if present
                if repo_path.endswith('.git'):
                    repo_path = repo_path[:-4]
            
            # Get repository
            repo = gh.get_repo(repo_path)
            
            # Get commits
            commits_list = []
            
            # Get commits from GitHub API
            commits = repo.get_commits(sha=branch)
            
            for commit in commits:
                # Get author information
                author_name = "Unknown"
                author_email = "unknown@email.com"
                
                if commit.author:
                    author_name = commit.author.login
                
                if commit.commit.author:
                    if not author_name or author_name == "Unknown":
                        author_name = commit.commit.author.name
                    author_email = commit.commit.author.email
                
                # Apply filters
                if username and author_name.lower() != username.lower():
                    continue
                
                if email and author_email.lower() != email.lower():
                    continue
                
                commit_date = commit.commit.author.date
                
                if start_date and commit_date < start_date:
                    continue
                    
                if end_date and commit_date > end_date:
                    continue
                
                # Get files changed
                files_changed = [file.filename for file in commit.files]
                
                commit_data = {
                    'commit_hash': commit.sha,
                    'author_name': author_name,
                    'author_email': author_email,
                    'date': commit_date,
                    'message': commit.commit.message,
                    'files_changed': files_changed
                }
                
                commits_list.append(commit_data)
            
            return commits_list
            
        except Exception as e:
            raise ValueError(f"Failed to fetch commits from GitHub: {str(e)}")