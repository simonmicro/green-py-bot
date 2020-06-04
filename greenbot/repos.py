import os
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
    for repoName, repoUrl in greenbot.config.repos.items():
        repoPath = os.path.join(reposPath, repoName)
        if os.path.isdir(repoPath):
            # Dir is already there -> just update it
            logging.info('Updating ' + repoName + ' ' + repoUrl)
            git.Git(repoPath).pull()
        else:
            logging.info('Cloning ' + repoName + ' ' + repoUrl)
            os.mkdir(repoPath)
            git.Git().clone(repoUrl, repoPath)
    logging.debug('Updated repos')
