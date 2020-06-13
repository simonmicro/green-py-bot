# What is this? #
![repo-size](https://img.shields.io/github/repo-size/simonmicro/green-py-bot)
![open-issues](https://img.shields.io/github/issues/simonmicro/green-py-bot)
![last-commit](https://img.shields.io/github/last-commit/simonmicro/green-py-bot/master)

This is a easy-to-use Telegram bot. Its main task is to execute trusted Python scripts by a schedule. Useful e.g. to fetch RSS feeds or monitor or... Just everything you can do with Python.
You are missing a script? Just contribute and enjoy the community using it!

## Official docker image ##
![build-howto](https://img.shields.io/docker/cloud/automated/realsimonmicro/green-py-bot)
![build-state](https://img.shields.io/docker/cloud/build/realsimonmicro/green-py-bot)
![build-pulls](https://img.shields.io/docker/pulls/realsimonmicro/green-py-bot)
![build-size](https://img.shields.io/docker/image-size/realsimonmicro/green-py-bot)

Check it out on [https://hub.docker.com/r/realsimonmicro/green-py-bot](https://hub.docker.com/r/realsimonmicro/green-py-bot). To use it, just download the `docker-compose.yml` file and start the bot with `docker-compose up`. Thats it!

## Manual startup ##
You don't want to use docker? Okay, then make sure to have all packages from the `requirements.txt` installed and start the bot with `python3 main.py`

## Add own repositories ##
You have a self-hosted instance and want to add some of your own (private) scripts? No problem! Just open the `config/config.json` and expand the `repo` section as needed. The key is the name, the value is e.g. the Git URL. Example? Here you go:
```
"repos": {
    "myownrepo": "https://github.com/user/goodstuff.git"
}
```
Your repo will be automatically cloned and regulary updated (every 24h). Its content will be directly stored into `repo/[name]`, so make sure the scripts are stored inside the root of the repo!

## Visit the bot over on Telegram! ##
A copy of this repo is running always reachable on [https://t.me/green_py_bot](https://t.me/green_py_bot). Just start a conversation and look where it goes...
