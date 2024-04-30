# Discord Stalking Bot

## Description

The Discord Stalking Bot is a Python-based Discord bot designed to track and monitor League of Legends players' in-game activities. It allows users to stalk specific summoners, receive notifications when they start or finish games, and track various statistics such as win streaks, loss streaks, and time wasted in games.

## Features

- **Leaderboard Command**: Displays a list showing which player has the highest of certain stat
- **Stalk Command**: Allows users to start stalking a League of Legends summoner by providing their in-game name and tag.
- **Unstalk Command**: Allows users to stop stalking a summoner.
- **Stalklist Command**: Displays a list of all currently stalked summoners.
- **Start Command**: Initializes the bot and sets the current Discord channel for notifications.
- **Automatic Game Tracking**: The bot automatically checks the in-game status of stalked summoners at regular intervals.
- **Win/Loss Tracking**: Tracks consecutive win and loss streaks for each summoner.
- **Game Duration Tracking**: Tracks the duration of each game played by a summoner.
- **Displays game information**: Displays information about the game after it's done


## Installation

1. Clone this repository to your local machine.
2. Set up a Discord bot application and obtain its token.
3. Add the bot to your Discord server.
4. Inside a config.py file set up the tokens/regions.

## Usage

1. Start the bot by running `python StalkerRun.py`.
2. Use the various commands (`!leaderboard`,`!stalk`, `!unstalk`, `!stalklist`, `!start`) to interact with the bot in your Discord server.

## Contributors

- [MrChoppy](https://github.com/MrChoppy)

## License

This project is licensed under the MIT License
