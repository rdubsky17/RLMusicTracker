import csv
import os
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from zoneinfo import ZoneInfo
import os
import sys

def get_runtime_path(filename_or_folder):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename_or_folder)
    return os.path.abspath(filename_or_folder)

CLIENT_ID = "9783d7914a9844c281c64548e1eb3ae3" # ← Replace with yours
CLIENT_SECRET = "28ba6ef15d5b40eea1cf5e9779c6fa9b" # ← Replace with yours


def last_logged_track(csv_file):
    if os.path.exists(csv_file):
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            if reader:
                return reader[-1]
    return None


def log_tracks(csv_file= get_runtime_path("spotify_log.csv"), limit=20): # Limit is the amount of songs per api call, does not have much effect unless < 5
    SPOTIFY_SCOPE = "user-read-recently-played user-read-playback-state"
    REDIRECT_URI = "http://127.0.0.1:8888/callback"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id= CLIENT_ID,   
        client_secret= CLIENT_SECRET, 
        redirect_uri=REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    ))


    logged = set()
    if os.path.exists(csv_file):
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                logged.add(row["Played At"])

    entries = {}
    recent = sp.current_user_recently_played(limit)


    for item in recent["items"]:
        played_at = item["played_at"]
        if played_at in logged:
            continue
        
        track = item["track"]
        artist = track["artists"][0]["name"]
        name = track["name"]

        entries[played_at] = {
            "timestamp": datetime.fromisoformat(played_at.replace("Z", "+00:00")).astimezone(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M:%S"),
            "artist": artist,
            "track": name
        }

    try: # tries to get currently playing track
        current = sp.current_user_playing_track()
        if current and current["is_playing"]:
            track = current["item"]
            artist = track["artists"][0]["name"]
            name = track["name"]

            last_entry = last_logged_track(csv_file)
            if last_entry is None or not (last_entry["Artist"] == artist and last_entry["Track"] == name):
                played_at = datetime.utcnow().isoformat(timespec='milliseconds') + "Z"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entries[played_at] = {"timestamp": timestamp, "artist": artist, "track": name}
    except spotipy.exceptions.SpotifyException as e:
        print(" Could not fetch current song:", e)


    with open(csv_file, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if os.stat(csv_file).st_size == 0:
            writer.writerow(["Played At", "Timestamp", "Artist", "Track"])

        for played_at, data in sorted(entries.items()):
            writer.writerow([played_at, data["timestamp"], data["artist"], data["track"]])

    return (f"Logged {len(entries)} track(s) to {csv_file}")




    
