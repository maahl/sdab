import os

################################################################################
# Customize these variables                                                    #
################################################################################

SHARELATEX_URL = 'https://domain.tld/'
TIMEOUT = 30 # seconds

# map sharelatex projects ids to names
# only include projects you want to backup
PROJECTS = {
    '0123456789': 'project_name',
}

# Where the git repositories will be stored
BACKUP_DIR = os.path.join(os.environ['HOME'], 'projects', 'sharelatex_projects')

# Where the old files will be stored (used for latexdiff).
# This directory must be accessible by the sharelatex container, so that it can
# execute latexdiff
TMP_DIR = os.path.abspath(os.path.join(os.sep, 'tmp', 'sdab'))

# sharelatex credentials
SHARELATEX_EMAIL = 'user@domain.tld'
SHARELATEX_PASSWORD = 'password'

# commit message used for each commit
GIT_COMMIT = 'Automatic commit with content gathered from sharelatex'

# if enabled, will attempt to run "git push" after committing
PUSH_ENABLED = True

# the ssh private key to use when pushing the git repo.
# Note that the authentication must be passwordless if you want to run this
# script in a cron job, use at your own risks.
# Requires git >= 2.3.0
SSH_ID_FILE = '~/.ssh/id_rsa_sharelatex'

# command executed for latexdiff'ing the files before and after commit.
# Update the paths to the mount point on your sharelatex container.
# The command will be formatted with the relative path to the old and new
# version of the projects. It also assumes the main file is called main.tex
# (sharelatex's default).
LATEXDIFF_COMMAND = 'docker exec sharelatex sh -c "latexdiff --flatten /root/sdab/{project_name_old}/main.tex /root/sdab/{project_name}/main.tex > /root/sdab/{project_name}/diff.tex && xelatex --output-directory /root/sdab/{project_name}/ /root/sdab/{project_name}/diff.tex > /dev/null"'
# alternatively, compile it locally
#LATEXDIFF_COMMAND = 'latexdiff --flatten ' + TMP_DIR + '/{project_name_old}/main.tex ' + TMP_DIR + '/{project_name}/main.tex'

# if enabled, will attempt to send an email with the diff file
EMAIL_ENABLED = True

# Body of the email that will be sent. Make sure to escape it properly so that
# it is properly interpreted in the variable EMAIL_COMMAND below.
EMAIL_BODY = '''Hi,

Find enclosed the recent changes that happened in your project on sharelatex.
'''

# command used for sending the email. It will be formatted with the project
# name, and the filename of the diff file.
# The following syntax requires heirloom-mailx.
EMAIL_COMMAND = 'echo "' + EMAIL_BODY + '" | mailx -a "{attachment}" -r "sharelatex@domain.tld" -s "[{project_name}] PDF diff file" -S smtp="domain.tld:587" -S smtp-use-starttls -S smtp-auth=login -S smtp-auth-user="sharelatex@domain.tld" -S smtp-auth-password="password" recipient@domain.tld'
