# RLMusicTracker
Combines and merges statistics for Spotify and Rocket League, allowing you to monitor which songs impact different styles of play. Requires use of an external BakkesMod plugin for now.


--Does not function without use of GameStats plugin from BakkesMod--


Setup:

In spotify_logger.py: Assign client_id and client_secret with your own token, obtained though https://developer.spotify.com/

In StatReader.py: In GameStats Plugin Menu, assign the statistics to be downloaded to the same folder as GAMESTATS_PATH

In watchdoggy.py: Change username to your platform display name, set SPOTIFY_PATH and GAMESTATS_PATH accordingly.

