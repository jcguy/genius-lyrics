#!/usr/bin/env python3
from bs4 import BeautifulSoup

import requests
import sys


API_TOKEN = "Bearer [redacted]"
HEADER = {"Authorization": API_TOKEN}
ARTIST_NAME = "Fall Out Boy"


def get_song_api(song_name):
    """
        Given a song title, returns the full url for the song's page.
    """

    # Grab the JSON object corresponding to search results for the song name
    base_api = "http://api.genius.com"
    search_url = "{}/search".format(base_api)
    query = {"q": song_name}
    r = requests.get(search_url, params=query, headers=HEADER)
    j = r.json()

    # Check through the search results for the first song by our artist
    song_api = None
    for hit in j["response"]["hits"]:
        if hit["result"]["primary_artist"]["name"] == ARTIST_NAME:
            song_api = hit["result"]["api_path"]
            break

    # The for/else construct only runs the 'else' part if the for loop was not explicitly broken out of.
    # In this case, we break out of the for loop when we find the song
    else:
        print("Song {} not found on first page of results.".format(song_name), file=sys.stderr)

        if ARTIST_NAME in song_name:
            return None

        return get_song_api("{} {}".format(song_name, ARTIST_NAME))

    song_url = "{}{}".format(base_api, song_api)
    return song_url


def get_lyrics(song_name):
    """
        Given a song title, returns the text of the lyrics, including section tags
    """
    # Grab the JSON object from the API
    base_url = "http://genius.com"
    song_url = get_song_api(song_name)

    if song_url is None:
        return None

    r = requests.get(song_url, headers=HEADER)
    j = r.json()

    # Extract the song's page from the JSON object
    path = j["response"]["song"]["path"]
    page_url = "{}{}".format(base_url, path)
    page = requests.get(page_url)

    # Find the div with the lyrics class and grab the lyrics
    soup = BeautifulSoup(page.text, "html.parser")
    lyrics = soup.find("div", class_="lyrics").get_text()

    return lyrics


def strip_lyrics(lyrics):
    # Convert the lyrics to a list, with each line as a single element
    # Drop any empty lines
    lyrics = [line for line in lyrics.split("\n") if len(line) > 0]

    # Remove the section annotations
    lyrics = [line for line in lyrics if line[0] != "["]

    # Join the lyrics back together with newlines
    return "\n".join(lyrics)


def print_lyrics(song_name):
    """
        Given a song title, prints the lyrics.
    """
    lyrics = get_lyrics(song_name)

    if lyrics is None:
        return

    lyrics = strip_lyrics(get_lyrics(song_name))
    print(lyrics)


def main():
    """
        Iterates through each line in the input file and
    """
    if len(sys.argv) < 2:
        print("Usage: {} <input file>".format(sys.argv[0]))
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file) as f:
        # for loops on a file handle are iterated line-by-line, including the line ending character
        try:
            for line in f:
                print_lyrics(line.replace("\n", ""))
        except KeyboardInterrupt:
            print("\rQuitting...", file=sys.stderr)


if __name__ == "__main__":
    main()
