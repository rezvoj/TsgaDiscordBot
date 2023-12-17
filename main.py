import discord_bot, update, sys


if __name__ == '__main__':
    try:
        update.updateDelay = int(sys.argv[1])
    except Exception:
        pass
    discord_bot.run()
