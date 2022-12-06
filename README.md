# Music Link
Music Link is a Discord bot that responds to music links with more music links

Anyone can paste a link to a song from any supported platform and it will be automagically translated to the same song on other platforms.

It currently supports Spotify, YouTube Music, YouTube, and Apple Music

# API keys
It uses unauthenticated apis for YouTube Music and Apple Music, but requires api keys for Spotify and Discord.

You can find instructions for getting credentials from [Spotipy](https://spotipy.readthedocs.io/en/2.21.0/#getting-started) and [discordpy](https://discordpy.readthedocs.io/en/stable/discord.html)

# Usage

Create a .env file in the root of the repository that looks like this:
```
SPOTIPY_CLIENT_ID=<insert your spotify client id here>
SPOTIPY_CLIENT_SECRET=<insert your spotify client secret here>

DISCORD_TOKEN=<insert your discord bot token here>
```

Install dependencies and run using [PDM](https://pdm.fming.dev/latest/)
```
git clone https://github.com/platipus25/discord-music-link.git
cd discord-music-link
pdm install
pdm run python main.py
```
