
import tkinter as tk
from tkinter import ttk
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import StatReader, spotify_logger
import sys, os, time, threading


def get_runtime_path(filename_or_folder):
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller EXE
        return os.path.join(os.path.dirname(sys.executable), filename_or_folder)
    return os.path.abspath(filename_or_folder)

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        global df
        if not event.is_directory:
            
            scanSongs()
            
            refresh_table()
        
USERNAME = 'Goku SSJGSS'
GAMESTATS_PATH = get_runtime_path("GameStats")
SPOTIFYLOG_PATH = get_runtime_path("spotify_log.csv")

gamestats_path = (
    os.path.join(os.path.dirname(sys.executable), GAMESTATS_PATH)
    if getattr(sys, 'frozen', False) else GAMESTATS_PATH
)

df = StatReader.getStats(USERNAME)
backup_df = df.copy()
sortAscending = False
WatchdogStatus = False
observer = None

def refresh_table():
    global df, backup_df
    df = pd.read_csv(get_runtime_path("CompleteStats.csv"))  # reload the latest version
    backup_df = df.copy()
    display_dataframe(df)

def scanSongs():
    global df
    text = spotify_logger.log_tracks(SPOTIFYLOG_PATH,  10)
    textbox.config(state="normal")           # Enable editing
    textbox.delete("1.0", "end")             # Clear previous text
    textbox.insert("end", text + "\n")   # Insert new text
    textbox.config(state="disabled")
    df = StatReader.getStats(USERNAME)
    df.to_csv(get_runtime_path("CompleteStats.csv"))
    refresh_table()

def startWatchdog():
    global observer
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, GAMESTATS_PATH, recursive=False)
    observer.start()

    textbox.config(state="normal")           # Enable editing
    textbox.delete("1.0", "end")             # Clear previous text
    textbox.insert("end", "Watchdog scanning "+ GAMESTATS_PATH + " for new files" + "\n")   # Insert new text
    textbox.config(state="disabled")
    while observer.is_alive():
        time.sleep(1)

def toggleWatchdog():
    global WatchdogStatus
    WatchdogStatus = not WatchdogStatus

    watchdog_button.config(
    text="Watchdog Enabled" if WatchdogStatus else "Watchdog Disabled",
    background="Green" if WatchdogStatus else "Red")

    if WatchdogStatus:
        thread = threading.Thread(target=startWatchdog, daemon=True)
        thread.start()
    else:
        if observer:
            observer.stop()
            observer.join()
            
def toggleSortOrder():
    global sortAscending
    sortAscending = not sortAscending
    ascButton.config(text="Ascending" if sortAscending else "Descending")
    sortDF(selected_sortOption.get())

def load_csv():
    display_dataframe(backup_df)

def sortDF(sort_by):
    global df
    df = df.sort_values(by=sort_by, ascending=sortAscending)
    display_dataframe(df)

def mergeDF(key):
    global df
    df = backup_df.copy() # resets df

    numeric_cols = ['Score', 'Goals', 'Assists', 'Saves', 'Shots', 'Demolishes', 'BoostUsage', 'Wins', 'Count']
    df = df.groupby([key], as_index=False)[numeric_cols].sum()
    
    if key == 'Track':
        artist_lookup = backup_df.drop_duplicates(subset=['Track'])[['Track', 'Artist']]
        df = df.merge(artist_lookup, on='Track', how='left')

    df['Score_Average'] = (df['Score'] / df['Count']).round(2)
    df['Goals_Average'] = (df['Goals'] / df['Count']).round(2)
    df['Wins_Average'] = (df['Wins'] / df['Count']).round(2)
    df['Saves_Average'] = (df['Saves'] / df['Count']).round(2)
    df['Shots_Average'] = (df['Shots'] / df['Count']).round(2)
    df['Assists_Average'] = (df['Assists'] / df['Count']).round(2)
    df['Demolishes_Average'] = (df['Demolishes'] / df['Count']).round(2)
    df['BoostUsage_Average'] = (df['BoostUsage'] / df['Count']).round(2)
    df['BoostUsage'] = df['BoostUsage'].round(2)
    
    display_dataframe(df)

def display_dataframe(df):
    tree.delete(*tree.get_children())

    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor='w')

    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

def searchDB(event=None):
    global df, backup_df
    df = backup_df.copy()

    searchQuery = searchtextbox.get("1.0", "end").strip()
    if selected_mergeOption.get() == "Artist":
        mergeDF('Artist')
        df = df[df['Artist'].str.lower().str.contains(searchQuery.lower())]
    elif selected_mergeOption.get() == "Track":
        mergeDF('Track')
        df = df[df['Track'].str.lower().str.contains(searchQuery.lower())]
    else:
        print("poopfart")

    countFloor = countFloorTextbox.get().strip()
    if countFloor.isdecimal():
        df = df[df['Count'] >= int(countFloor)]


    searchtextbox.delete("1.0", "end")

    display_dataframe(df)

window = tk.Tk()
window.title("RL - Spotify Stat Tracker")
window.geometry("900x800")
window.configure(bg="#3C3D37")

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview",
                background="#1e1e1e",
                foreground="white",
                fieldbackground="#1e1e1e",
                rowheight=25)

style.configure("Treeview.Heading",
                background="#333333",
                foreground="white",
                font=("Arial", 10, "bold"))

header = tk.Label(
    window,
    text="Ryker's Sickass RL Tracker",
    font=("Helvetica", 20, "bold"),
    pady=10,
    background="#3C3D37",
    fg="#ECDFCC"
)
header.pack(anchor="n")

sortOptions = ["Score", "Score_Average",
           "Goals", "Goals_Average",
           "Assists", "Assists_Average",
           "Saves", "Saves_Average",
           "Shots", "Shots_Average",
           "Demolishes", "Demolishes_Average",
           "BoostUsage", "BoostUsage_Average",
           "Wins", "Wins_Average",
           "Count"]
mergeOptions = ["Track", "Artist"]

selected_sortOption = tk.StringVar()
selected_mergeOption = tk.StringVar()

watchdog_button = tk.Button(window, text="Watchdog Disabled", background= "Red", command=toggleWatchdog)
watchdog_button.pack(anchor="nw", padx=10, pady=10)


right_panel = tk.Frame(window)
right_panel.pack(side="right", anchor="n", padx=10, pady=10)
right_panel.configure(bg="#697565")
# Scan Spotify button
scan_button = tk.Button(right_panel, text="Scan Spotify", command=scanSongs)
scan_button.pack(anchor="ne", pady=(0, 10))
scan_button.configure(bg="#ECDFCC")
# Log/display box right under the button
textbox = tk.Text(right_panel, height=4, width=30, state="disabled", wrap="word")
textbox.pack(anchor="ne")
textbox.configure(bg="#ECDFCC")

# Create a frame to hold the dropdown and the textbox
top_frame = tk.Frame(window)
top_frame.pack(padx=20, pady=10)
top_frame.configure(bg="#697565")

# Dropdown inside the frame
mergeDropdown = tk.OptionMenu(top_frame, selected_mergeOption, *mergeOptions, command=mergeDF)
mergeDropdown.pack(side="left", padx=10)
mergeDropdown.configure(bg="#ECDFCC")

sortButton = tk.Button(top_frame, text="Search", command=searchDB)
sortButton.pack(side="left", padx=5)
sortButton.configure(bg="#ECDFCC")

searchtextbox = tk.Text(top_frame, height=1, width=18, padx= 10)
searchtextbox.pack(side="left")
searchtextbox.bind("<Return>", searchDB)
searchtextbox.configure(bg="#ECDFCC")

countTextbox = tk.Text(top_frame, height=1, width=13, padx= 10, border=0)
countTextbox.insert('end',  "Where Count ≥")
countTextbox.pack(side="left", padx= 20 )
countTextbox.configure(bg="#ECDFCC", state="disabled")

countFloorTextbox = tk.Entry(top_frame, width=5)
countFloorTextbox.pack(side="left", padx= 10)
countFloorTextbox.configure(bg="#ECDFCC")

# Bind Enter key
countFloorTextbox.bind("<Return>", searchDB)





sortDropdown = tk.OptionMenu(window, selected_sortOption, *sortOptions, command=sortDF)
sortDropdown.pack(padx=20, pady=5)
sortDropdown.configure(bg="#ECDFCC")

ascButton = tk.Button(window, text="Descending", command=toggleSortOrder)
ascButton.pack(padx=60, pady=10)
ascButton.configure(bg="#ECDFCC")

load_button = tk.Button(window, text="Load CSV", command=load_csv)
load_button.pack(padx=100, pady=10)
load_button.configure(bg="#ECDFCC")

tree_frame = tk.Frame(window)
tree_frame.pack(fill="both", expand=True)

tree = ttk.Treeview(tree_frame)
tree.pack(side="left", fill="both", expand=True)


scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")


window.mainloop()
