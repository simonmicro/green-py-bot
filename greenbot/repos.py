import os
import greenbot.config
import git
import logging
import importlib
logger = logging.getLogger('greenbot.repos')

reposPath = 'repos'
# Make sure the repos path exists
os.makedirs(reposPath, exist_ok=True)

def update():
    global reposPath
    logger.debug('Updating repos')
    # Update all copies of the remote repos
    for repoName, repoUrl in greenbot.config.repos.items():
        if len(repoUrl) == 0:
            continue
        repoPath = os.path.join(reposPath, repoName)
        if os.path.isdir(repoPath):
            # Dir is already there -> just update it
            logger.info('Updating repo ' + repoName + ' from ' + repoUrl)
            try:
                # ...but first make sure the dir is really a git dir (otherwise ignore)
                git.Repo(repoPath).git_dir
                git.Git(repoPath).pull()
            except git.exc.GitCommandError as e:
                logger.error('Could not update ' + repoName + ': ' + str(e))
            except git.exc.InvalidGitRepositoryError:
                logger.warn('The local copy of ' + repoName + ' is not a Git repo!')
        else:
            logger.info('Cloning repo ' + repoName + ' from ' + repoUrl)
            os.mkdir(repoPath)
            try:
                git.Git().clone(repoUrl, repoPath)
            except git.exc.GitCommandError as e:
                logger.error('Could not initial clone ' + repoName + ': ' + str(e))
    logger.debug('Updated repos')

def getRepos():
    repos = []
    for name, url in greenbot.config.repos.items():
        repos.append(name)
    return repos

def getScripts(repoName):
    global reposPath
    logger.debug('Checking for scripts in ' + repoName)
    scripts = []
    for root, dirs, files in os.walk(os.path.join(reposPath, repoName)):
        for filename in files:
            if filename.endswith('.py'):
                scripts.append(os.path.splitext(filename)[0])
        break
    return scripts

def getModule(identifier):
    global reposPath
    (repoName, scriptName) = resolveIdentifier(identifier)
    modulePath = '.'.join(reposPath.split('/')) + '.' + '.'.join([repoName, scriptName])
    logger.debug('Importing ' + modulePath)
    return importlib.import_module(modulePath)

def makeIdentifier(repoName, scriptName = None):
    if scriptName is None:
        return repoName
    return repoName + '/' + scriptName

def resolveIdentifier(identifier):
    parts = identifier.split('/')
    if len(parts) < 1:
        return [None, None]
    elif len(parts) < 2:
        return [parts[0], None]
    else:
        return [parts[0], parts[1]]

def validateIdentifier(identifier):
    parts = resolveIdentifier(identifier)
    # Verify that all parts are there
    if parts[0] is None or parts[1] is None:
        return False
    # Make sure the repo is valid
    if not parts[0] in getRepos():
        return False
    # Make sure the script is valid
    if not parts[1] in getScripts(parts[0]):
        return False
    return True
