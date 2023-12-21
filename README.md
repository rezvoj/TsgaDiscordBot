# Twitch Streamer Game Alerts Discord Bot

> ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python Version](https://img.shields.io/badge/python-3.10-blue)

## Table of Contents

> - [Introduction](#introduction)
> - [Commands](#commands)
> - [Installation](#installation)
> - [Configuration](#configuration)
> - [Usage](#usage)
> - [Development](#development)
> - [License](#license)

## Introduction

> The Twitch Streamer Game Alerts Discord Bot is a Discord bot designed to notify users when a specified Twitch streamer starts streaming a game they are interested in. Users can manage their watched streamers and games using a set of intuitive commands, receiving direct messages whenever the streamers they follow go live with the specified games.

## Commands

> Here are the commands available for the bot:
>
> - `!tsga list`: Show a list of streamers and watched games.
> - `!tsga list <streamer>`: Show a list of watched games for the specified streamer.
> - `!tsga watch <streamer> <game>`: Register a game to watch for when the specified streamer streams it.
> - `!tsga unwatch <streamer> <game>`: Unregister a watched game for the specified streamer.
> - `!tsga unwatch <streamer>`: Unregister all watched games for the specified streamer.
> - `!tsga unwatch`: Unregister all watched games of all streamers.
> - `!tsga help`: Display a list of commands and their descriptions.

## Installation

### Requirements

> - **Python 3.10** or later

### Setup

> 1. **Clone the Repository**
>
>    ```bash
>    git clone https://github.com/rezvoj/TsgaDiscordBot.git
>    cd TsgaDiscordBot
>    ```
>
> 2. **Install Dependencies**
>
>    Make sure you have Python installed, and then install the required packages using pip:
>
>    ```bash
>    pip install -r requirements.txt
>    ```
>
> 3. **Setup Environment Variables**
>
>    Make sure the following environment variables are accessible in your operating system:
>
>    ```plaintext
>    TWITCH_ID=<your-twitch-client-id>
>    TWITCH_SECRET=<your-twitch-client-secret>
>    DISCORD_TOKEN=<your-discord-bot-token>
>    ```

## Configuration

> Make sure to configure your Discord and Twitch credentials properly.
>
> - **Twitch API Credentials:**
>
>   - Obtain your Twitch client ID and secret from the [Twitch Developer Portal](https://dev.twitch.tv/console/apps).
>   - Set the `TWITCH_ID` and `TWITCH_SECRET` in your environment.
>
> - **Discord Bot Token:**
>
>   - Create a Discord bot via the [Discord Developer Portal](https://discord.com/developers/applications).
>   - Set the `DISCORD_TOKEN` in your environment.

## Usage

> To start the bot, run the following command:
>
> ```bash
> python main.py [update_interval_in_seconds]
> ```
>
> - **update_interval_in_seconds**: You can specify the delay in seconds for the update loop. The default is 30 seconds if not provided.
>
> For example, to run the bot with a 60-second update interval, use:
>
> ```bash
> python main.py 60
> ```
>
> The bot will connect to Discord and start monitoring Twitch streamers based on user requests. It will check for updates and notify users at the specified interval.

## Development

### Code Structure

> - **main.py**: Entry point for running the bot.
> - **database.py**: Handles all database operations.
> - **twitch_api.py**: Interacts with the Twitch API.
> - **update.py**: Periodically updates streamer status.
> - **tests.py**: Contains unit tests for the bot functionality.

### Database Structure

> The bot utilizes a simple SQLite database with the following schema:
>
> - **Streamer Table:**
>
>   | Column  | Type    | Description                           |
>   | ------- | ------- | ------------------------------------- |
>   | id      | BIGINT  | Unique identifier for the streamer    |
>   | status  | BIGINT  | Current status of the streamer (game) |
>
> - **WatchedStatus Table:**
>
>   | Column     | Type    | Description                             |
>   | ---------- | ------- | --------------------------------------- |
>   | streamerId | BIGINT  | ID of the streamer                      |
>   | userId     | BIGINT  | Discord user ID                         |
>   | status     | BIGINT  | ID of the game being watched            |
>

### Running Tests

> To run tests, use:
>
> ```bash
> python tests.py
> ```

## License

> This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
