# Sharelatex Diff And Backup

This script connects to your sharelatex instance, retrieves the projects you
listed in `config.py`, and saves them to a git repository.

It also generates the diff since last commit, using latexdiff.

What it does in more details:

* connect to your sharelatex instance
* retrieve the last version of the projects listed in `config.py` (source and
  pdf)
* make a copy of the existing repo, so that it can latexdiff it later
* extract the source in the repo
* commit the changes
* push them if possible
* latexdiff the old and new version
* email the latexdiff using the provided command

To setup the script:

```sh
cp config_example.py config.py
$EDITOR config.py
```

To execute the script: `./sdab.py`

The output pdf diff is located in `{TMP_DIR}/{project_name}/diff.pdf`, available
for you to share it however you like.

Note: I have not tested this on the official Sharelatex website.
