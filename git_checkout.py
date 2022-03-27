import gitlab
import time
import git
import os
import shutil

gitlab_host = os.getenv('GITLAB_HOST', "http://gitlab.example.com")
gitlab_token = os.getenv('GITLAB_TOKEN', "wefULxCmohHSGA6o9Rz6")
gitlab_username = os.getenv('GITLAB_USERNAME', "root")
gitlab_password = os.getenv('GITLAB_PASSWORD', "PRINCOprinco$9")
repositories_root_dir = os.getenv('REPOSITORIES_ROOT_DIR', 'a')
cloning_mode = os.getenv('CLONING_MODE', 'http').lower()
repo_name = os.getenv('REPO_NAME', 'gwms')

gl = gitlab.Gitlab(gitlab_host, private_token=gitlab_token, ssl_verify=False, api_version=4)
gl.auth()

project_id = '2'
branch_name = 'main'

project = gl.projects.get(project_id)
print(project)

if os.path.exists(repo_name):
        print('Deleting source code directory...')
        shutil.rmtree(repo_name)
else:
        print('Source Code is Empty')

print('Now checkout gwms source code....')
git.Git(repositories_root_dir).clone(f'http://{gitlab_username}:{gitlab_password}@{project.http_url_to_repo.split("http://")[1]}')
print('Checkout completed')
