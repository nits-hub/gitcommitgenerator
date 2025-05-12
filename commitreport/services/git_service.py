import os
import shutil
import git
import tempfile
from datetime import datetime
from django.conf import settings

class GitService:
    """
    Service for working with local git repositories
    """
    
    def __init__(self):
        self.temp_dir = settings.GIT_TEMP_CLONE_DIR
    
    def _get_repo(self, repo_path):
        """
        Get a git repository object either from a local path or by cloning a remote URL
        """
        if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, '.git')):
            # Local repository
            return git.Repo(repo_path)
        else:
            # Remote repository needs to be cloned
            temp_dir = tempfile.mkdtemp(dir=self.temp_dir)
            try:
                return git.Repo.clone_from(repo_path, temp_dir)
            except git.GitCommandError as e:
                shutil.rmtree(temp_dir, ignore_errors=True)
                raise ValueError(f"Failed to clone repository: {str(e)}")
    
    def get_commits(self, repo_path, branch='main', username=None, email=None, start_date=None, end_date=None):
        """
        Get commits from a git repository
        
        Args:
            repo_path: Path to the repository (local or remote URL)
            branch: Branch to fetch commits from
            username: Filter commits by author username
            email: Filter commits by author email
            start_date: Filter commits from this date
            end_date: Filter commits until this date
            
        Returns:
            List of commit data dictionaries
        """
        temp_dir = None
        try:
            repo = self._get_repo(repo_path)
            
            # Check if the specified branch exists
            if branch not in [ref.name.split('/')[-1] for ref in repo.references]:
                # Try with origin/branch_name
                origin_branch = f"origin/{branch}"
                if origin_branch not in [ref.name for ref in repo.references]:
                    # If branch doesn't exist, use the default branch
                    branch = repo.active_branch.name
            
            # Get commits
            commits = []
            try:
                for commit in repo.iter_commits(branch):
                    # Apply filters
                    if username and commit.author.name.lower() != username.lower():
                        continue
                    
                    if email and commit.author.email.lower() != email.lower():
                        continue
                    
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    
                    if start_date and commit_date < start_date:
                        continue
                        
                    if end_date and commit_date > end_date:
                        continue
                    
                    # Get list of files changed in this commit
                    files_changed = []
                    try:
                        if commit.parents:
                            diffs = commit.parents[0].diff(commit)
                            files_changed = [diff.a_path for diff in diffs]
                    except Exception:
                        # If we can't get the files changed, just continue
                        pass
                    
                    commits.append({
                        'commit_hash': commit.hexsha,
                        'author_name': commit.author.name,
                        'author_email': commit.author.email,
                        'date': commit_date,
                        'message': commit.message,
                        'files_changed': files_changed
                    })
            except git.GitCommandError as e:
                raise ValueError(f"Failed to fetch commits: {str(e)}")
                
            return commits
            
        finally:
            # Clean up temporary directory if it was created
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)