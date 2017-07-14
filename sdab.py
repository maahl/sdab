#!/usr/bin/env python

import git
import os
import requests
import subprocess
import shutil
import zipfile
from bs4 import BeautifulSoup

from config import *


def login_to_sharelatex(session):
    '''
    Get a session cookie for sharelatex
    '''
    # retrieve the csrf token from the login form
    url = SHARELATEX_URL + 'login'
    response = session.get(url, timeout=TIMEOUT)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': '_csrf'})['value']

    # send the login info
    data = {
        '_csrf': csrf_token,
        'email': SHARELATEX_EMAIL,
        'password': SHARELATEX_PASSWORD
    }
    session.post(url, data=data, timeout=TIMEOUT)


def cmd(cmd, cwd='/'):
    '''
    Call the command cmd in the directory cwd
    '''
    p = subprocess.Popen(cmd, cwd=cwd, shell=True)
    p.wait()


def get_tmp_dir(project_name):
    return os.path.join(TMP_DIR, project_name)

def get_tmp_old_dir(project_name):
    return os.path.join(TMP_DIR, project_name + '-old')

def get_archive_path(project_name):
    return os.path.join(TMP_DIR, project_name + '.zip')

def get_repo_dir(project_name):
    return os.path.join(BACKUP_DIR, project_name)

def backup_projects(session, project_id):
    '''
    Retrieve the projects from sharelatex, and update the corresponding git
    repository
    '''
    project_name = PROJECTS[project_id]

    print('Backup project ' + project_name + '... ', end='')

    archive = get_archive_path(project_name)
    tmp_old = get_tmp_old_dir(project_name)
    repo_dir = get_repo_dir(project_name)

    # remove the tmp_old dir if necessary
    if os.path.isdir(tmp_old):
        shutil.rmtree(tmp_old)

    new_repo = False
    # init the git repo if necessary
    if not os.path.isdir(repo_dir):
        repo = git.Repo.init(repo_dir)
        new_repo = True
    else:
        repo = git.Repo(repo_dir)

    # download the new version of the project
    response = session.get(SHARELATEX_URL + 'project/' + project_id + '/download/zip')
    filename = os.path.join(TMP_DIR, project_name + '.zip')
    with open(filename, 'wb') as f:
        f.write(response.content)

    # copy the old files in tmp to latexdiff them later
    shutil.copytree(repo_dir, tmp_old)

    # extract the downloaded archive in the repo
    with zipfile.ZipFile(archive, 'r') as archive:
        archive.extractall(repo_dir)

    # True if there have been changes since last commit
    repo_has_changed = repo.is_dirty() or repo.untracked_files

    if repo_has_changed:
        # download the corresponding pdf
        response = session.get(SHARELATEX_URL + 'project/' + project_id + '/output/output.pdf')

        # write the pdf file
        with open(os.path.join(repo_dir, 'output.pdf'), 'wb') as f:
            f.write(response.content)

        # add all untracked files
        repo.index.add(repo.untracked_files)

        # add all changed files
        repo.git.add(update=True)

        # commit
        repo.index.commit(GIT_COMMIT)

        # attempt to push if a remote exists
        if PUSH_ENABLED and repo.remotes:
            # make git use the provided id file
            os.environ['GIT_SSH_COMMAND'] = 'ssh -i ' + SSH_ID_FILE
            repo.git.push()

        print('OK')
    else:
        print('no change since last commit')

    return repo_has_changed and not new_repo


def generate_diffs(project_id):
    '''
    Generate pdf diffs using latexdiff
    '''
    project_name = PROJECTS[project_id]

    tmp = get_tmp_dir(project_name)
    tmp_old = get_tmp_old_dir(project_name)
    repo = get_repo_dir(project_name)

    # remove the tmp dir if necessary
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)

    # copy the repo where sharelatex container can find it
    shutil.copytree(repo, tmp)

    # generate the diff and compile it
    cmd(LATEXDIFF_COMMAND.format(
        project_name=project_name,
        project_name_old=project_name + '-old'
    ))

    # send the diff file by email
    cmd(EMAIL_COMMAND.format(
        project_name=project_name,
        attachment=os.path.join(tmp, 'diff.pdf')
    ))


if __name__ == '__main__':
    with requests.Session() as session:
        print('Connecting... ', end='')
        login_to_sharelatex(session)
        print('OK')

        for project_id  in PROJECTS:
            project_has_changed = backup_projects(session, project_id)
            if project_has_changedt:
                generate_diffs(project_id)
