import os
import random
import subprocess
import sys
from datetime import datetime, timedelta
from utils import generate_random_commit_message
import pathspec
import time

def initialize_git_repo(repo_path, remote_url=None):
    try:
        if not os.path.exists(os.path.join(repo_path, '.git')):
            subprocess.run(['git', 'init'], cwd=repo_path, check=True)
        if remote_url:
            subprocess.run(['git', 'remote', 'remove', 'origin'], cwd=repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=repo_path, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error initializing git repository: {e}")
        sys.exit(1)

def get_gitignore_patterns(root_path):
    default_patterns = [
        '**/node_modules/**',
        '**/.git/**',
        '**/dist/**',
        '**/build/**',
        '**/.cache/**',
        '**/__pycache__/**',
        '**/.env*',
        '**/.venv/**',
        '**/venv/**',
        '**/*.pyc'
    ]
    
    patterns = default_patterns.copy()
    gitignore_path = os.path.join(root_path, '.gitignore')
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r') as f:
                # Add non-empty, non-comment lines from .gitignore
                patterns.extend([
                    line.strip() 
                    for line in f.readlines() 
                    if line.strip() and not line.startswith('#')
                ])
        except IOError as e:
            print(f"Warning: Could not read .gitignore file: {e}")
    
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

def get_local_timezone_offset():
    # Get local timezone offset in format +0200 or -0500
    offset = time.localtime().tm_gmtoff
    hours = int(offset / 3600)
    minutes = int((abs(offset) % 3600) / 60)
    sign = '+' if offset >= 0 else '-'
    return f"{sign}{hours:02d}{minutes:02d}"

def generate_random_commit_history(folder_path, max_commits_per_day, max_gap, max_days_in_past, 
                                 remote_url=None, git_name=None, git_email=None, total_commits=None):
    try:
        initialize_git_repo(folder_path, remote_url)
        os.chdir(folder_path)
        
        # Get gitignore patterns
        gitignore_spec = get_gitignore_patterns(folder_path)
        
        # Collect files respecting gitignore
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            # Remove ignored directories from dirs list
            rel_root = os.path.relpath(root, folder_path)
            dirs[:] = [
                d for d in dirs 
                if not gitignore_spec.match_file(os.path.join(rel_root, d))
            ]
            
            for filename in filenames:
                rel_path = os.path.join(rel_root, filename)
                if not gitignore_spec.match_file(rel_path) and filename != os.path.basename(__file__):
                    files.append(os.path.join(root, filename))

        if not files:
            print("No files found in the specified folder (excluding ignored paths).")
            sys.exit(1)

        # Create sequential list of dates with random gaps
        date_list = []
        current_date = datetime.now() - timedelta(days=max_days_in_past)
        end_date = datetime.now()
        
        while current_date <= end_date:
            if random.random() > 0.5:  # 50% chance to add this date
                date_list.append(current_date)
                # Add a random gap between 1 and max_gap days
                gap = random.randint(0, max_gap)
                current_date += timedelta(days=gap + 1)
            else:
                current_date += timedelta(days=1)

        if not date_list:  # Ensure at least one date is selected
            date_list.append(end_date)

        # Recalculate minimum commits per day based on actual number of days
        min_commits_per_day = max(1, total_commits // len(date_list))
        remaining_commits = total_commits - (min_commits_per_day * len(date_list))

        # Distribute commits ensuring at least min_commits_per_day per date
        commits_per_date = []
        for date in date_list:
            # Start with minimum commits
            base_commits = min_commits_per_day
            
            # Add extra commits randomly if we have remaining
            if remaining_commits > 0:
                extra_commits = random.randint(0, min(
                    remaining_commits,
                    max_commits_per_day - min_commits_per_day
                ))
                base_commits += extra_commits
                remaining_commits -= extra_commits
            
            commits_per_date.append((date, base_commits))

        # If we still have remaining commits, distribute them randomly
        while remaining_commits > 0:
            for i in range(len(commits_per_date)):
                if remaining_commits <= 0:
                    break
                if commits_per_date[i][1] < max_commits_per_day:
                    commits_per_date[i] = (commits_per_date[i][0], commits_per_date[i][1] + 1)
                    remaining_commits -= 1

        commits_made = 0
        retry_files = []  # Store failed files for retry
        tz_offset = get_local_timezone_offset()  # Move this line here

        # Create commits according to our distribution
        for commit_date, num_commits in commits_per_date:
            daily_commits_made = 0
            while daily_commits_made < num_commits:
                if commits_made >= total_commits:
                    break

                # Ensure we have files to commit
                if not files and retry_files:
                    files.extend(retry_files)
                    retry_files.clear()
                elif not files and not retry_files:
                    # If we run out of files, reset the files list with all available files
                    for root, dirs, filenames in os.walk(folder_path):
                        rel_root = os.path.relpath(root, folder_path)
                        dirs[:] = [
                            d for d in dirs 
                            if not gitignore_spec.match_file(os.path.join(rel_root, d))
                        ]
                        
                        for filename in filenames:
                            rel_path = os.path.join(rel_root, filename)
                            if not gitignore_spec.match_file(rel_path) and filename != os.path.basename(__file__):
                                files.append(os.path.join(root, filename))
                    
                    if not files:
                        print("\nError: No files available to modify.")
                        sys.exit(1)

                # Random time during working hours (more realistic)
                commit_time = commit_date.replace(
                    hour=random.randint(9, 18),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )

                # Select 1-5 files for this commit
                num_files_in_commit = random.randint(1, min(len(files), 5))
                files_in_commit = random.sample(files, num_files_in_commit)
                for f in files_in_commit:
                    files.remove(f)
                for f in files_in_commit:
                    try:
                        with open(f, 'a') as file:
                            file.write('\n')
                    except IOError as e:
                        print(f"Error writing to file {f}: {e}")
                        continue
                for f in files_in_commit:
                    try:
                        subprocess.run(['git', 'add', f], check=True)
                    except subprocess.CalledProcessError:
                        print(f"Warning: Could not add file {f}, skipping...")
                        continue
                commit_message = generate_random_commit_message()
                commit_date_str = f"{commit_time.strftime('%Y-%m-%dT%H:%M:%S')}{tz_offset}"
                
                try:
                    env = os.environ.copy()
                    env['GIT_AUTHOR_DATE'] = commit_date_str
                    env['GIT_COMMITTER_DATE'] = commit_date_str
                    env['GIT_AUTHOR_NAME'] = git_name
                    env['GIT_AUTHOR_EMAIL'] = git_email
                    env['GIT_COMMITTER_NAME'] = git_name
                    env['GIT_COMMITTER_EMAIL'] = git_email
                    
                    subprocess.run(['git', 'commit', '-m', commit_message], env=env, check=True)
                    commits_made += 1
                    print(f"\rProgress: {commits_made}/{total_commits} commits", end="")
                except subprocess.CalledProcessError:
                    retry_files.extend(files_in_commit)
                    print(f"\nFailed to commit files, will retry later.")
                    continue
                daily_commits_made += 1

        print(f"\nCompleted: {commits_made}/{total_commits} commits created")
        
        # Push changes if remote URL provided
        if remote_url and commits_made > 0:
            print("\nPushing changes to remote repository...")
            subprocess.run(['git', 'push', '-u', 'origin', 'master'], cwd=folder_path, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def get_user_input():
    print("\n=== GitGamer Configuration ===")
    while True:
        try:
            total_commits = int(input("Enter total number of commits you want: ").strip())
            if total_commits > 0:
                break
            print("Error: Please enter a positive number.")
        except ValueError:
            print("Error: Please enter a valid number.")

    while True:
        folder_path = input("Enter the folder path: ").strip()
        if os.path.exists(folder_path):
            break
        print("Error: The folder path does not exist. Please try again.")

    while True:
        try:
            max_commits = int(input("Enter maximum commits per day (default 5): ") or "5")
            if max_commits > 0:
                break
            print("Error: Please enter a positive number.")
        except ValueError:
            print("Error: Please enter a valid number.")

    while True:
        try:
            max_gap = int(input("Enter maximum gap between commits in days (default 2): ") or "2")
            if max_gap >= 0:
                break
            print("Error: Please enter a non-negative number.")
        except ValueError:
            print("Error: Please enter a valid number.")

    while True:
        try:
            max_days = int(input("Enter maximum days in past (default 30): ") or "30")
            if max_days > 0:
                break
            print("Error: Please enter a positive number.")
        except ValueError:
            print("Error: Please enter a valid number.")

    remote_url = input("Enter remote repository URL (optional, press Enter to skip): ").strip() or None

    print("\n=== Git Author Configuration ===")
    git_name = input("Enter your Git name (default from git config): ").strip()
    git_email = input("Enter your Git email (default from git config): ").strip()
    
    # If user didn't provide values, try to get from git config
    if not git_name:
        try:
            git_name = subprocess.check_output(['git', 'config', 'user.name'], text=True).strip()
        except:
            git_name = "Unknown"
    if not git_email:
        try:
            git_email = subprocess.check_output(['git', 'config', 'user.email'], text=True).strip()
        except:
            git_email = "unknown@example.com"

    return {
        'folder_path': folder_path,
        'max_commits_per_day': max_commits,
        'max_gap': max_gap,
        'max_days_in_past': max_days,
        'remote_url': remote_url,
        'git_name': git_name,
        'git_email': git_email,
        'total_commits': total_commits
    }

if __name__ == '__main__':
    config = get_user_input()
    generate_random_commit_history(**config)
