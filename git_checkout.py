import gitlab
import time
import git
import os

gitlab_host = os.getenv('GITLAB_HOST', "http://gitlab.example.com")
gitlab_token = os.getenv('GITLAB_TOKEN', "wefULxCmohHSGA6o9Rz6")
gitlab_username = os.getenv('GITLAB_USERNAME', "admin")
gitlab_password = os.getenv('GITLAB_PASSWORD', "admin")
repositories_root_dir = os.getenv('REPOSITORIES_ROOT_DIR', 'a')
cloning_mode = os.getenv('CLONING_MODE', 'http').lower()

gl = gitlab.Gitlab(gitlab_host, private_token=gitlab_token, ssl_verify=False, api_version=4)
gl.auth()

project_name = '2'
branch_name = 'main'

project = gl.projects.get(project_name)

git.Git(repositories_root_dir).clone(f'http://{gitlab_username}:{gitlab_password}@{project.http_url_to_repo.split("http://")[1]}')

