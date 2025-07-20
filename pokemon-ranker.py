# https://chatgpt.com/c/6759e13a-1d30-8007-8986-81a4828bbe90
import json
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO


DATA_FILE = 'pokemon_data.json'
K_FACTOR = 32

def load_data():
    """
    Load Pokémon data from JSON file and initialize match-up stats if missing.
    """
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    # Ensure every Pokémon has wins and losses fields
    for pokemon in data.values():
        if 'wins' not in pokemon:
            pokemon['wins'] = 0
        if 'losses' not in pokemon:
            pokemon['losses'] = 0
    
    return data

def save_data(data):
    """
    Save Pokémon data to JSON file.
    """
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def expected_score(rating_a, rating_b):
    """
    Calculate expected score of player A against player B using the ELO formula.
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(data, winner, loser):
    """
    Update the ELO ratings and match-up stats for two Pokémon after a match.
    """
    Ra = data[winner]['rating']
    Rb = data[loser]['rating']

    Ea = expected_score(Ra, Rb)
    Eb = expected_score(Rb, Ra)

    # Winner gets 1 point, loser gets 0
    Ra_new = Ra + K_FACTOR * (1 - Ea)
    Rb_new = Rb + K_FACTOR * (0 - Eb)

    data[winner]['rating'] = Ra_new
    data[loser]['rating'] = Rb_new

    # Update wins and losses
    data[winner]['wins'] += 1
    data[loser]['losses'] += 1

def get_two_pokemon(data):
    """
    Select two Pokémon for a matchup.
    Semi-random: biased towards similar ELO ratings with occasional random pairings.
    """
    keys = list(data.keys())
    # Sort keys by rating for competitive pairing
    keys_sorted = sorted(keys, key=lambda k: data[k]['rating'])

    # Choose one Pokémon as a seed
    chosen = random.choice(keys_sorted)
    chosen_rating = data[chosen]['rating']

    # Find candidates with similar ELO ratings
    candidates = [k for k in keys_sorted if k != chosen and abs(data[k]['rating'] - chosen_rating) < 200]

    # Randomly decide if this will be a completely random match
    if random.random() < 0.2 or not candidates:
        chosen2 = random.choice([k for k in keys if k != chosen])
    else:
        chosen2 = random.choice(candidates)

    return chosen, chosen2

def calculate_total_votes(data):
    """
    Calculate the total number of votes by summing up the wins of all Pokémon.
    """
    return sum(pokemon['wins'] for pokemon in data.values())

class PokemonRankingApp:
    def __init__(self, master, data):
        self.master = master
        self.data = data

        self.master.title("Pokémon Ranking")
        self.frame = tk.Frame(self.master, padx=20, pady=20)
        self.frame.pack()

        # Pokémon A
        self.pokemon_a_frame = tk.Frame(self.frame)
        self.pokemon_a_frame.pack(side=tk.LEFT, padx=20)
        self.label_a = tk.Label(self.pokemon_a_frame, text="", font=("Helvetica", 16))
        self.label_a.pack(pady=10)
        self.img_label_a = tk.Label(self.pokemon_a_frame, cursor="hand2")
        self.img_label_a.pack(pady=10)
        self.info_a = tk.Label(self.pokemon_a_frame, text="", font=("Helvetica", 12))
        self.info_a.pack(pady=10)

        self.button_a = ttk.Button(self.pokemon_a_frame, text="Choose", command=self.choose_a)
        self.button_a.pack(pady=10)

        # Pokémon B
        self.pokemon_b_frame = tk.Frame(self.frame)
        self.pokemon_b_frame.pack(side=tk.LEFT, padx=20)
        self.label_b = tk.Label(self.pokemon_b_frame, text="", font=("Helvetica", 16))
        self.label_b.pack(pady=10)
        self.img_label_b = tk.Label(self.pokemon_b_frame, cursor="hand2")
        self.img_label_b.pack(pady=10)
        self.info_b = tk.Label(self.pokemon_b_frame, text="", font=("Helvetica", 12))
        self.info_b.pack(pady=10)

        self.button_b = ttk.Button(self.pokemon_b_frame, text="Choose", command=self.choose_b)
        self.button_b.pack(pady=10)

        # Leaderboard Buttons
        leaderboard_button = ttk.Button(self.master, text="View Leaderboard", command=self.show_leaderboard)
        leaderboard_button.pack(pady=10)

        top10_button = ttk.Button(self.master, text="View Top 10 Pokémon", command=self.show_top_10)
        top10_button.pack(pady=10)

        # Bind keys for voting
        self.master.bind("<Left>", lambda event: self.choose_a())
        self.master.bind("<Right>", lambda event: self.choose_b())

        # Bind images for voting
        self.img_label_a.bind("<Button-1>", lambda event: self.choose_a())
        self.img_label_b.bind("<Button-1>", lambda event: self.choose_b())

        self.current_pair = None
        self.next_match()

    def display_pokemon(self, side, name):
        """
        Display a Pokémon's details on the given side ('a' or 'b').
        """
        p = self.data[name]

        # Main Image
        resp = requests.get(p['image_url'])
        img = Image.open(BytesIO(resp.content))
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        text = f"{p['name']} (#{p['pokedex_number']})"
        info = f"Generation: {p['generation']}\nRegion: {p['region']}\nType: {', '.join(p['types'])}"

        if side == 'a':
            self.label_a.config(text=text)
            self.img_label_a.config(image=img_tk)
            self.img_label_a.image = img_tk
            self.info_a.config(text=info)
        else:
            self.label_b.config(text=text)
            self.img_label_b.config(image=img_tk)
            self.img_label_b.image = img_tk
            self.info_b.config(text=info)

    def next_match(self):
        """
        Select the next pair of Pokémon and display them.
        """
        p1, p2 = get_two_pokemon(self.data)
        self.current_pair = (p1, p2)
        self.display_pokemon('a', p1)
        self.display_pokemon('b', p2)

    def choose_a(self):
        """
        Handle choice of Pokémon A.
        """
        winner, loser = self.current_pair[0], self.current_pair[1]
        update_elo(self.data, winner, loser)
        save_data(self.data)
        self.next_match()

    def choose_b(self):
        """
        Handle choice of Pokémon B.
        """
        winner, loser = self.current_pair[1], self.current_pair[0]
        update_elo(self.data, winner, loser)
        save_data(self.data)
        self.next_match()

    def show_leaderboard(self):
        """
        Display a leaderboard sorted by ELO rankings.
        """
        sorted_pokemon = sorted(self.data.items(), key=lambda x: x[1]['rating'], reverse=True)
        leaderboard_window = tk.Toplevel(self.master)
        leaderboard_window.title("Leaderboard")
        tree = ttk.Treeview(leaderboard_window, columns=('Name', 'ELO', 'Wins', 'Losses', 'Types', 'Generation', 'Region', 'Pokedex'), show='headings')
        tree.heading('Name', text='Name')
        tree.heading('ELO', text='ELO')
        tree.heading('Wins', text='Wins')
        tree.heading('Losses', text='Losses')
        tree.heading('Types', text='Types')
        tree.heading('Generation', text='Generation')
        tree.heading('Region', text='Region')
        tree.heading('Pokedex', text='Pokedex Number')
        for name, details in sorted_pokemon:
            tree.insert('', 'end', values=(name, int(details['rating']), details['wins'], details['losses'], ', '.join(details['types']), details['generation'], details['region'], details['pokedex_number']))
        tree.pack(fill=tk.BOTH, expand=True)

    def show_top_10(self):
        """
        Display the top 10 Pokémon with detailed information in a scrollable, two-column layout.
        """
        # Sort and limit to the top 10 Pokémon
        sorted_pokemon = sorted(self.data.items(), key=lambda x: x[1]['rating'], reverse=True)[:10]
        
        # Create a new scrollable window
        top10_window = tk.Toplevel(self.master)
        top10_window.title("Top 10 Pokémon")
        
        # Create a canvas and a scrollbar
        canvas = tk.Canvas(top10_window)
        scrollbar = ttk.Scrollbar(top10_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable scrolling with mouse wheel/touchpad
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Add Pokémon details to the scrollable frame (two-column layout)
        column = 0
        for idx, (name, details) in enumerate(sorted_pokemon, start=1):
            # Create a frame for each Pokémon entry
            frame = ttk.Frame(scrollable_frame, padding=10)
            frame.grid(row=(idx - 1) // 2, column=column, padx=20, pady=10)

            # Fetch artwork and sprite
            art_resp = requests.get(details['image_url'])
            art_img = Image.open(BytesIO(art_resp.content)).resize((100, 100), Image.Resampling.LANCZOS)
            art_tk = ImageTk.PhotoImage(art_img)

            sprite_resp = requests.get(details['sprite_url'])
            sprite_img = Image.open(BytesIO(sprite_resp.content)).resize((50, 50), Image.Resampling.LANCZOS)
            sprite_tk = ImageTk.PhotoImage(sprite_img)

            # Display Pokémon information
            tk.Label(frame, text=f"{idx}. #{details['pokedex_number']} {name}", font=("Helvetica", 14)).pack()
            tk.Label(frame, image=art_tk).pack(side="left", padx=5)  # Official Artwork
            tk.Label(frame, image=sprite_tk).pack(side="right", padx=5)  # Sprite Image
            tk.Label(frame, text=f"Height: {details['height']} m | Weight: {details['weight']} kg", font=("Helvetica", 12)).pack()
            tk.Label(frame, text=f"Abilities: {', '.join(details['abilities'])}", font=("Helvetica", 12)).pack()

            # Store references to images to prevent garbage collection
            frame.image_refs = [art_tk, sprite_tk]

            # Alternate columns for the two-column layout
            column = 1 - column

if __name__ == "__main__":
    data = load_data()
    root = tk.Tk()
    app = PokemonRankingApp(root, data)
    root.mainloop()
