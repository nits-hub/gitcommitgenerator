from atlassian import Bitbucket
from datetime import datetime
import re

class BitbucketService:
    """
    Service for working with Bitbucket repositories
    """
    
    def get_commits(self, repo_path, branch='main', username=None, email=None, 
                   start_date=None, end_date=None, auth_username=None, auth_token=None):
        """
        Get commits from a Bitbucket repository
        
        Args:
            repo_path: Path to the repository in format 'workspace/repo' or URL
            branch: Branch to fetch commits from
            username: Filter commits by author username
            email: Filter commits by author email
            start_date: Filter commits from this date
            end_date: Filter commits until this date
            auth_username: Bitbucket username for authentication
            auth_token: Bitbucket app password or token
            
        Returns:
            List of commit data dictionaries
        """
        try:
            # Clean up repo_path - handle different formats that might be provided
            
            # If it's a git clone command, extract just the URL
            if repo_path.startswith('git clone '):
                repo_path = repo_path.replace('git clone ', '')
            
            # Extract the bitbucket.org part from URL
            if 'bitbucket.org/' in repo_path:
                # Use regex to extract the workspace/repo part
                match = re.search(r'bitbucket\.org/([^/]+)/([^/.]+)', repo_path)
                if match:
                    workspace = match.group(1)
                    repo_slug = match.group(2)
                else:
                    # Fallback to string splitting
                    repo_path = repo_path.split('bitbucket.org/')[-1]
                    # Remove .git extension if present
                    if repo_path.endswith('.git'):
                        repo_path = repo_path[:-4]
                    
                    # Handle possible username in URL (username@bitbucket.org)
                    if '@' in repo_path:
                        repo_path = repo_path.split('@')[-1]
                    
                    # Extract workspace and repository name
                    parts = repo_path.split('/')
                    if len(parts) < 2:
                        raise ValueError("Invalid Bitbucket repository path. Format should be 'workspace/repo' or a valid Bitbucket URL")
                    
                    workspace = parts[0]
                    repo_slug = parts[1]
            else:
                # Direct workspace/repo format
                parts = repo_path.split('/')
                if len(parts) != 2:
                    raise ValueError("Invalid Bitbucket repository path. Format should be 'workspace/repo' or a valid Bitbucket URL")
                
                workspace = parts[0]
                repo_slug = parts[1]
            
            # For debugging
            print(f"Workspace: {workspace}, Repo: {repo_slug}")
            
            # Check if we should try a local Git repository approach first
            try:
                from git import Repo
                import tempfile
                import os
                import shutil
                
                # Try to fetch via Git directly
                temp_dir = tempfile.mkdtemp()
                repo_url = f"https://{auth_username}:{auth_token}@bitbucket.org/{workspace}/{repo_slug}.git" if auth_username and auth_token else f"https://bitbucket.org/{workspace}/{repo_slug}.git"
                
                try:
                    print(f"Attempting to clone: {repo_url}")
                    git_repo = Repo.clone_from(repo_url, temp_dir)
                    
                    # Get the correct branch
                    try:
                        if branch in [b.name for b in git_repo.branches]:
                            git_repo.git.checkout(branch)
                        elif f"origin/{branch}" in [r.name for r in git_repo.refs]:
                            git_repo.git.checkout(f"origin/{branch}")
                        elif "master" in [b.name for b in git_repo.branches]:
                            git_repo.git.checkout("master")
                        elif "main" in [b.name for b in git_repo.branches]:
                            git_repo.git.checkout("main")
                    except Exception as e:
                        print(f"Branch checkout failed: {str(e)}")
                        # Continue with whatever branch we cloned
                        
                    # Get commits
                    commits_list = []
                    for commit in git_repo.iter_commits():
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
                        
                        # Get list of files changed
                        files_changed = []
                        try:
                            if commit.parents:
                                diffs = commit.parents[0].diff(commit)
                                files_changed = [diff.a_path for diff in diffs]
                        except Exception:
                            pass
                        
                        commits_list.append({
                            'commit_hash': commit.hexsha,
                            'author_name': commit.author.name,
                            'author_email': commit.author.email,
                            'date': commit_date,
                            'message': commit.message,
                            'files_changed': files_changed
                        })
                    
                    # Clean up
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    if commits_list:
                        print(f"Successfully fetched {len(commits_list)} commits via Git directly")
                        return commits_list
                    
                except Exception as git_error:
                    print(f"Git approach failed: {str(git_error)}")
                    # Clean up
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    # Continue with API approach
            except ImportError:
                print("GitPython not available, using API approach only")
                
            # Initialize Bitbucket API client
            if auth_username and auth_token:
                bitbucket = Bitbucket(
                    url="https://api.bitbucket.org",
                    username=auth_username,
                    password=auth_token,
                    cloud=True
                )
            elif auth_username:
                # If only username is provided, use it from the URL
                bitbucket = Bitbucket(
                    url="https://api.bitbucket.org",
                    username=auth_username,
                    cloud=True
                )
            else:
                # Try to extract username from repo_path if it's in URL format
                extracted_username = None
                if '@bitbucket.org' in repo_path:
                    extracted_username = repo_path.split('://')[1].split('@')[0]
                
                if extracted_username:
                    bitbucket = Bitbucket(
                        url="https://api.bitbucket.org",
                        username=extracted_username,
                        cloud=True
                    )
                else:
                    # Anonymous access has strict rate limits
                    bitbucket = Bitbucket(
                        url="https://api.bitbucket.org",
                        cloud=True
                    )
            
            # Get commits
            commits_list = []
            
            # Bitbucket API pagination
            start = 0
            limit = 50
            
            while True:
                try:
                    # The correct format for the get_commits method
                    response = bitbucket.get_commits(
                        repository_slug=repo_slug,
                        workspace=workspace,
                        params={
                            'start': start,
                            'limit': limit,
                            'include': branch
                        }
                    )
                except Exception as api_error:
                    # Try with different branch names if the specified branch fails
                    try:
                        # Try with master branch if main fails
                        alt_branch = "master" if branch == "main" else "main"
                        response = bitbucket.get_commits(
                            repository_slug=repo_slug,
                            workspace=workspace,
                            params={
                                'start': start,
                                'limit': limit,
                                'include': alt_branch
                            }
                        )
                    except Exception:
                        # If both fail, try one more approach - direct API call
                        try:
                            # Direct API call without params
                            response = bitbucket.get_commits(
                                repository_slug=repo_slug,
                                workspace=workspace
                            )
                        except Exception:
                            # If all attempts fail, raise the original error
                            raise ValueError(f"Failed to access repository or branch. Error: {str(api_error)}. "
                                            f"Tried both '{branch}' and alternative branch.")
                
                if 'values' not in response or not response['values']:
                    break
                    
                for commit in response['values']:
                    # Get author information
                    author_name = "Unknown"
                    author_email = "unknown@email.com"
                    
                    if 'author' in commit and 'user' in commit['author'] and commit['author']['user']:
                        author_name = commit['author']['user'].get('display_name', 'Unknown')
                    
                    if 'author' in commit and 'raw' in commit['author']:
                        raw_author = commit['author']['raw']
                        if '<' in raw_author and '>' in raw_author:
                            author_email = raw_author.split('<')[1].split('>')[0]
                            if not author_name or author_name == "Unknown":
                                author_name = raw_author.split('<')[0].strip()
                    
                    # Apply filters
                    if username and author_name.lower() != username.lower():
                        continue
                    
                    if email and author_email.lower() != email.lower():
                        continue
                    
                    commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                    
                    if start_date and commit_date < start_date:
                        continue
                        
                    if end_date and commit_date > end_date:
                        continue
                    
                    # Get files changed
                    files_changed = []
                    
                    if 'hash' in commit:
                        try:
                            # Try to get files changed in this commit
                            files_response = bitbucket.get_diffstat(
                                repository_slug=repo_slug,
                                workspace=workspace,
                                revision=commit['hash']
                            )
                            files_changed = []
                            if 'values' in files_response:
                                files_changed = [diff['new']['path'] for diff in files_response['values'] if 'new' in diff and 'path' in diff['new']]
                        except Exception:
                            # If we can't get the files changed, just continue with empty list
                            pass
                    
                    commit_data = {
                        'commit_hash': commit['hash'],
                        'author_name': author_name,
                        'author_email': author_email,
                        'date': commit_date,
                        'message': commit['message'],
                        'files_changed': files_changed
                    }
                    
                    commits_list.append(commit_data)
                
                # Check if there are more commits to fetch
                if 'next' not in response:
                    break
                
                start += limit
            
            return commits_list
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise ValueError(f"Failed to fetch commits from Bitbucket: {str(e)}\nDetails: {error_details}")