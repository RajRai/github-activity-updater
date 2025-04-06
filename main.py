import os
import datetime
import shutil
import time
import git
import requests
from dotenv import load_dotenv

load_dotenv()

github_repo = os.getenv("GITHUB_REPO")
repo_path = os.path.join(os.path.dirname(__file__), 'repo')
commit_msg = "Automated commit for GitHub contribution art"
git_user_name = os.getenv("GIT_USER_NAME")
git_user_email = os.getenv("GIT_USER_EMAIL")
github_token = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com"

# Define "HELLO" in a 7-row contribution grid
HELLO = [
    "#   #  #####  #      #       ###  ",
    "#   #  #      #      #      #   # ",
    "#   #  #      #      #      #   # ",
    "#####  #####  #      #      #   # ",
    "#   #  #      #      #      #   # ",
    "#   #  #      #      #      #   # ",
    "#   #  #####  #####  #####   ###  "
]

if os.path.exists(repo_path):
    shutil.rmtree(repo_path)


def ensure_repo_exists():
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Extract the owner and repo name from github_repo
    repo_owner, repo_name = github_repo.split('/')[-2:]

    # Check if repository exists
    repo_url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name.replace('.git', '')}"
    response = requests.get(repo_url, headers=headers)

    if response.status_code == 404:  # Repo not found, create it
        print(f"Repository {repo_name} not found. Creating it...")
        create_url = f"{GITHUB_API_URL}/user/repos"
        create_payload = {"name": repo_name, "private": False}  # Modify privacy if needed
        create_response = requests.post(create_url, json=create_payload, headers=headers)

        if create_response.status_code == 201:
            print(f"Repository {repo_name} created successfully.")
        else:
            print(f"Failed to create repository: {create_response.json()}")
            return

    repo = git.Repo.clone_from(f"https://{github_token}@{github_repo}", repo_path)

    repo.config_writer().set_value("user", "name", git_user_name).release()
    repo.config_writer().set_value("user", "email", git_user_email).release()
    return repo


# Ensure start_date aligns with a Sunday
def get_current_sunday():
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday() + 1)


def clear_repo():
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    repo_owner, repo_name = github_repo.split('/')[-2:]

    # Delete the repository
    delete_url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name.replace('.git', '')}"
    delete_response = requests.delete(delete_url, headers=headers)

    if delete_response.status_code == 204:
        print(f"Repository {repo_name} deleted successfully.")
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
    else:
        print(f"Failed to delete repository: {delete_response.json()}")


def create_commits_for_day():
    start_date = get_current_sunday() - datetime.timedelta(weeks=51-(51-len(HELLO[0]))//2)

    clear_repo()
    repo = ensure_repo_exists()

    for row in range(len(HELLO)):
        for col in range(len(HELLO[row])):
            if HELLO[row][col] == "#":
                commit_date = (start_date + datetime.timedelta(weeks=col, days=row)).strftime("%Y-%m-%dT12:00:00")

                file_path = os.path.join(repo_path, f'file{row}{col}.txt')
                with open(file_path, 'w') as file:
                    file.write('data')

                repo.index.add([file_path])
                repo.index.commit(commit_msg, author_date=commit_date, commit_date=commit_date)

    repo.remotes.origin.push()


def main():
    while True:
        create_commits_for_day()
        time.sleep(86400)  # Sleep for one day


if __name__ == "__main__":
    main()
