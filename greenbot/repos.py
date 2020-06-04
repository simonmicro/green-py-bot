import os
import hashlib
import greenbot.config
import git
import logging

reposPath = 'repos'

def update():
    global reposPath
    logging.debug('Updating repos')
    try:
        os.mkdir(reposPath)
    except FileExistsError:
        pass
    # Update all copies of the remote repos
    for repoUrl in greenbot.config.repos:
        # Generate the repo name based on the URI
        m = hashlib.sha256()
        m.update(repoUrl.encode())
        repoName = m.hexdigest()
        repoPath = os.path.join(reposPath, repoName)
        if os.path.isdir(repoPath):
            # Dir is already there -> just update it
            logging.info('Updating ' + repoUrl)
            git.Git(repoPath).pull()
        else:
            logging.info('Cloning ' + repoUrl)
            os.mkdir(repoPath)
            git.Git().clone(repoUrl, repoPath)
    logging.debug('Updated repos')
