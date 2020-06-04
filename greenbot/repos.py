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

def getScripts(repoName):
    global reposPath
    logging.debug('Checking for scripts in ' + repoName)
    scripts = []
    for root, dirs, files in os.walk(os.path.join(reposPath, repoName)):
        for filename in files:
            if filename.endswith('.py'):
                scripts.append(os.path.splitext(filename)[0])
        break
    return scripts

def getRepos():
    repos = []
    for name, url in greenbot.config.repos.items():
        repos.append(name)
    return repos
