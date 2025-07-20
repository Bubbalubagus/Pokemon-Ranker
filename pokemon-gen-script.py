import os
import json
import requests

DATA_FILE = 'pokemon_data.json'
POKEMON_LIMIT = 1025  # Total Pokémon

def fetch_pokemon_data(limit=POKEMON_LIMIT):
    """
    Fetch all Pokémon data from the PokeAPI and update an existing JSON file with additional details.
    Preserves existing voting data (wins, losses) and ELO rankings.
    """
    # Load existing data if the file exists
    if os.path.exists(DATA_FILE):
        print(f"Loading existing data from {DATA_FILE}...")
        with open(DATA_FILE, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    print("Fetching Pokémon list...")
    url = f"https://pokeapi.co/api/v2/pokemon?limit={limit}&offset=0"
    resp = requests.get(url)
    resp.raise_for_status()
    results = resp.json()['results']

    updated_data = {}
    for idx, p in enumerate(results, start=1):
        print(f"Fetching details for Pokémon {idx}/{limit}: {p['name']}...")
        p_resp = requests.get(p['url'])
        p_resp.raise_for_status()
        p_details = p_resp.json()

        name = p_details['name'].capitalize()
        pokedex_number = p_details['id']
        types = [t['type']['name'].capitalize() for t in p_details['types']]

        # Get official artwork and sprite URLs
        artwork_url = p_details['sprites']['other']['official-artwork']['front_default']
        sprite_url = p_details['sprites']['front_default']

        # Height and weight
        height_in_meters = p_details['height'] / 10  # Convert dm to meters
        weight_in_kg = p_details['weight'] / 10  # Convert hg to kg

        # Abilities
        abilities = [a['ability']['name'].capitalize() for a in p_details['abilities']]

        # Base stats
        stats = {s['stat']['name'].capitalize(): s['base_stat'] for s in p_details['stats']}

        # Fetch species data for generation and additional details
        species_resp = requests.get(p_details['species']['url'])
        species_resp.raise_for_status()
        species_data = species_resp.json()

        generation_name = species_data['generation']['name'].replace("generation-", "").capitalize()
        region = infer_region_from_generation(generation_name)

        # Preserve existing data if it exists
        existing_entry = existing_data.get(name, {})
        updated_data[name] = {
            'name': name,
            'pokedex_number': pokedex_number,
            'types': types,
            'image_url': artwork_url,
            'sprite_url': sprite_url,  # Sprite image
            'rating': existing_entry.get('rating', 1200.0),  # Preserve rating
            'generation': generation_name,
            'region': region,
            'wins': existing_entry.get('wins', 0),  # Preserve wins
            'losses': existing_entry.get('losses', 0),  # Preserve losses
            'height': height_in_meters,  # Height in meters
            'weight': weight_in_kg,  # Weight in kilograms
            'abilities': abilities,  # List of abilities
            'stats': stats  # Base stats
        }

    # Save the merged data to the JSON file
    print(f"Saving {len(updated_data)} Pokémon to {DATA_FILE}...")
    with open(DATA_FILE, 'w') as f:
        json.dump(updated_data, f, indent=4)

    print("Data updated successfully!")

def infer_region_from_generation(generation):
    """
    Map generations to regions. Adjust based on the specific generations you want to support.
    """
    gen_to_region = {
        "I": "Kanto",
        "Ii": "Johto",
        "Iii": "Hoenn",
        "Iv": "Sinnoh",
        "V": "Unova",
        "Vi": "Kalos",
        "Vii": "Alola",
        "Viii": "Galar",
        "Ix": "Paldea",
    }
    return gen_to_region.get(generation, "Unknown")

if __name__ == "__main__":
    fetch_pokemon_data()
