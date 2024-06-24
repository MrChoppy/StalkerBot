# Stalker Bot

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
3. Set up a Riot Games developer account and obtain a key.
4. Create a config.py file at the root.
5. Inside the config.py file set up the tokens and regions (example below).
6. Install the required libraries.
7. Add the bot to your Discord server.
8. Start the bot by typing !start in the desired Discord channel.
9. Use !stalk Name#Tag to stalk your friends.
10. Make fun of them when they lose.
  

config.py should look like this:

```
riot_api_key = 'xxxxxxxxxxxxxxxxxx'
region = "na1" #Your options: na1, eun1, euw1, la1, la2, br1, tr1, ru, jp1, oc1, kr
region_wide = "americas" #Your options: americas, europe, asia
discord_bot_token = 'xxxxxxxxxxxxxxxxxxxxx'
```

## Usage

1. Start the bot by running `python StalkerRun.py`.
2. Use the various commands (`!leaderboard`,`!stalk`, `!unstalk`, `!stalklist`, `!start`) to interact with the bot in your Discord server.

## Examples of what the bot does
![image](https://github.com/MrChoppy/StalkerBot/assets/89551180/7072c318-7470-4da2-ae94-d89e514471c3)
![image](https://github.com/MrChoppy/StalkerBot/assets/89551180/ee8689a1-e938-4e92-be5b-20d3a7a546ad)
![image](https://github.com/MrChoppy/StalkerBot/assets/89551180/11f285e8-1b37-4124-b08e-299812a52541)


## Contributors

- [MrChoppy](https://github.com/MrChoppy)

## License

This project is licensed under the MIT License
