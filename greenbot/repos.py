import os
import greenbot.config
import git
import logging
import importlib

reposPath = 'data/repos'

def update():
    global reposPath
    logging.debug('Updating repos')
    os.makedirs(reposPath, exist_ok=True)
    # Update all copies of the remote repos
    for repoName, repoUrl in greenbot.config.repos.items():
        repoPath = os.path.join(reposPath, repoName)
        if os.path.isdir(repoPath):
            # Dir is already there -> just update it
            logging.info('Updating ' + repoName + ' ' + repoUrl)
            try:
                git.Git(repoPath).pull()
            except git.exc.GitCommandError as e:
                logging.error('Could not update ' + repoName + ': ' + str(e))
        else:
            logging.info('Cloning ' + repoName + ' ' + repoUrl)
            os.mkdir(repoPath)
            try:
                git.Git().clone(repoUrl, repoPath)
            except git.exc.GitCommandError as e:
                logging.error('Could not initial clone ' + repoName + ': ' + str(e))
    logging.debug('Updated repos')

def getRepos():
    repos = []
    for name, url in greenbot.config.repos.items():
        repos.append(name)
    return repos

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

def getModule(repoName, scriptName):
    global reposPath
    modulePath = '.'.join([reposPath, repoName, scriptName])
    logging.debug('Importing ' + modulePath)
    return importlib.import_module(modulePath)
