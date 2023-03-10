# Contributing

If you are looking to contribute ideas or bug reports, please make an issue in the bot's
[issue tracker](https://github.com/EddieTheCubeHead/ClusterBot) using the appropriate issue template. The issue 
templates contain fields that should all be filled unless directly stated otherwise in the template. If you are 
looking to make a contribution in the form of code, please read the following section.

## Contributing code

If you would like to contribute code to the project feel free to make a pull request. Both pull requests about 
issues in the issue tracker and brand new features are considered. If the pull request is not about an issue marked 
with the "ready for development"-label, the board of Cluster ry, mainly represented by 
[Eetu Asikainen](https://github.com/EddieTheCubeHead), will decide whether the feature or bugfix is relevant to the 
bot development.

If your pull request is about an open issue, please start the pull request name with the issue number. (#1: Add 
contribution guidelines)

### Code style

Please make sure your code adheres to the [pep-8 standard](https://peps.python.org/pep-0008/) and is generally 
readable and neat, but don't stress too much. The worst that can happen is a change request by the bot developers.

### Testing

The bot does not currently have an automated testing suite. Please make sure to test your feature before making a 
pull request. A short description of test cases conducted manually helps a lot while reviewing pull requests.

## Running the bot (for local development)

To run the bot you need to create a "dev_secrets.json" -file in the root folder of the bot. There you should supply 
two key-value pairs. "GUILD_ID": int and "BOT_TOKEN": str. You can get the "GUILD_ID" by
[enabling deveoper mode in discord](https://beebom.com/how-enable-disable-developer-mode-discord/), right-clicking on
the guild you are using for testing your local version and selecting "Copy ID".

To get the "BOT_TOKEN" you need to
[create a bot account in discord developer portal](https://discordpy.readthedocs.io/en/stable/discord.html).

Once you have both values, the file should look something like this:

```
{
    "BOT_TOKEN": "my_cool_bot_token",
    "GUILD_ID": 314159265359
}
```

You also need to add a folder named "persistence" in the root folder of the bot.

After that you can run the bot by running bot.py with python.