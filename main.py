import discord
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic
from dotenv import load_dotenv
import requests
import os
import urllib.parse
import logging


class iTunes:
    ENDPOINT_URL = "https://itunes.apple.com/search"

    def search(self, query):
        # extract track id from urls
        url = urllib.parse.urlparse(query)
        q = (
            urllib.parse.parse_qs(url.query).get("i")
            if url.netloc == "music.apple.com"
            else None
        )
        query = q if q else query

        r = requests.get(self.ENDPOINT_URL, params={"term": query}).json()

        if not r.get("results"):
            return None

        return r["results"]


# Load SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and DISCORD_TOKEN
load_dotenv()

yt = YTMusic()
YOUTUBE_BASE_URL = "youtube.com"

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
SPOTIFY_BASE_URL = "open.spotify.com"

itunes = iTunes()
APPLE_MUSIC_BASE_URL = "music.apple.com"


def parse_spotify(tracks):

    results = [
        {
            "id": result["id"],
            "url": result["external_urls"]["spotify"],
            "title": result["name"],
            "album": result["album"]["name"],
            "artist": ", ".join(artist["name"] for artist in result["artists"]),
        }
        for result in tracks
    ]

    return results


def parse_youtube(body):

    results = [
        {
            "id": result["videoId"],
            "url": f"https://music.youtube.com/watch?v={result['videoId']}",
            "title": result["title"],
            "album": result["album"]["name"] if "album" in result else None,
            "artist": ", ".join(artist["name"] for artist in result["artists"]),
        }
        for result in body
        if result["resultType"] == "song" or result["resultType"] == "video"
    ]

    return results


def parse_apple_music(body):
    if not body:
        return []

    results = [
        {
            "id": result["trackId"],
            "url": result["trackViewUrl"],
            "title": result["trackName"],
            "album": result["collectionName"],
            "artist": result["artistName"],
        }
        for result in body
        if "kind" in result and result["kind"] == "song"
    ]

    return results


def find_track(url):
    if SPOTIFY_BASE_URL in url:
        tracks = [spotify.track(url)]
        results = parse_spotify(tracks)
    elif YOUTUBE_BASE_URL in url:
        body = yt.search(url)
        results = parse_youtube(body)
    elif APPLE_MUSIC_BASE_URL in url:
        body = itunes.search(url)
        results = parse_apple_music(body)
    else:
        results = []

    return results[0] if results else None


def find_others(result):
    query_string = f"{result['title']} by {result['artist']}"

    tracks = spotify.search(q=query_string)["tracks"]["items"]
    spotify_result = parse_spotify(tracks)
    spotify_url = spotify_result[0]["url"] if spotify_result else None

    body = yt.search(query_string)
    youtube_result = parse_youtube(body)
    youtube_url = youtube_result[0]["url"] if youtube_result else None

    body = itunes.search(query_string)
    apple_music_result = parse_apple_music(body)
    apple_music_url = apple_music_result[0]["url"] if apple_music_result else None

    return (spotify_url, youtube_url, apple_music_url)


class MusicLinkClient(discord.Client):
    async def on_ready(self):
        print("Logged on as", self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if "http://" in message.content or "https://" in message.content:
            url = message.content

            results = find_track(url)

            if results:
                print(results)

                async with message.channel.typing():

                    spotify_url, youtube_url, apple_music_url = find_others(results)

                    response = f"""Found {results['title']} by {results['artist']} from their album {results['album']}
{spotify_url or "Couldn't find on Spotify"}
{youtube_url or "Couldn't find on YouTube"}
{apple_music_url or "Couldn't find on Apple Music"}
"""

                    print(response)

                    await message.channel.send(
                        response,
                        reference=message,
                        mention_author=False,
                        suppress_embeds=False,
                    )


intents = discord.Intents.default()
intents.message_content = True
client = MusicLinkClient(intents=intents)

token = os.environ.get("DISCORD_TOKEN")
client.run(token)
