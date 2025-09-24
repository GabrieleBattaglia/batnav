# BATNAV by Gabriele Battaglia (IZ4APU) and Gemini
# Versione 1.1.2 - Data refactor 24/09/2025
import random, sys, json # <-- AGGIUNTO json
from datetime import date

# --- Costanti ---
VERSIONE="2.0.1 - 24 settembre 2025 by Gabriele Battaglia (IZ4APU) and Gemini"
CLASSIFICA_FILE = "batnav_charts.json" # <-- NUOVA costante per il file della classifica
CLASSIFICA_MAX_VOCI = 15 # <-- NUOVA costante per il numero massimo di voci

# --- Costanti di Stato Interno ---
INTERNAL_HIT = 'x'
INTERNAL_SUNK = '#'

# --- Costanti di Visualizzazione ---
MAP_UNKNOWN = '.'
MAP_MISS = 'o'
TARGET_HIT = 'X'
TARGET_SUNK = 'A'
FLEET_SHIP = 'S'
FLEET_HIT = 'c'
FLEET_SUNK = 'F'

# --- Classi ---
class Ship:
    def __init__(self, length):
        self.length = length
        self.coordinates = []
        self.hits = []

    def is_sunk(self):
        return len(self.hits) == self.length

# --- Funzioni di Gestione Classifica (NUOVE) ---

def load_classifica():
    """Carica la classifica dal file JSON. Ritorna un dizionario vuoto se il file non esiste."""
    try:
        with open(CLASSIFICA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_classifica(classifica):
    """Salva il dizionario della classifica nel file JSON."""
    with open(CLASSIFICA_FILE, 'w') as f:
        json.dump(classifica, f, indent=4)

def generate_ai_name():
    """Genera un nome casuale per l'IA secondo lo schema IA-c1v1c2v2c2v2."""
    consonanti = "BCDFGHJKLMNPQRSTVWXYZ"
    vocali = "AEIOU"
    c1 = random.choice(consonanti)
    c2 = random.choice(consonanti)
    v1 = random.choice(vocali)
    v2 = random.choice(vocali)
    return f"IA-{c1}{v1}{c2}{v2}{c2}{v2}"

def update_and_display_classifica(classifica, size, winner_name, shots, accuracy):
    """Aggiorna la classifica con il nuovo risultato, la ordina, la limita e la stampa."""
    size_key = str(size) # Le chiavi JSON devono essere stringhe
    
    # Crea la nuova voce per la classifica
    new_entry = {
        "nome": winner_name,
        "colpi": shots,
        "perc_colpi": accuracy,
        "data": date.today().strftime("%d/%m/%Y") # <-- NUOVO: Aggiunge la data di oggi
    }
    
    # Prende la classifica per la dimensione corrente, o una lista vuota se non esiste
    chart_for_size = classifica.get(size_key, [])
    chart_for_size.append(new_entry)
    
    # Ordina la classifica per numero di colpi (meno è meglio)
    chart_for_size.sort(key=lambda x: x['colpi'])
    
    # Mantiene solo le prime N voci (definite da CLASSIFICA_MAX_VOCI)
    classifica[size_key] = chart_for_size[:CLASSIFICA_MAX_VOCI]
    
    # Stampa la classifica
    print(f"\n--- CLASSIFIICA per griglia {size}x{size} ---")
    # MODIFICATO: Aggiunta la colonna "Data" all'intestazione
    print(f"{'Pos.':<5}{'Nome':<18}{'Colpi':<8}{'% Colpiti':<12}{'Data'}")
    print("-" * 58) # MODIFICATO: Allungata la linea di separazione
    for i, entry in enumerate(classifica[size_key], 1):
        pos = f"{i}."
        nome = entry['nome']
        colpi = entry['colpi']
        perc = f"{entry['perc_colpi']:.1f}%"
        # NUOVO: Recupera la data (con un valore di default per i vecchi punteggi)
        data = entry.get('data', 'N/D') 
        # MODIFICATO: Aggiunta la data alla riga stampata
        print(f"{pos:<5}{nome:<18}{colpi:<8}{perc:<12}{data}")
    print("-" * 58) # MODIFICATO: Allungata la linea di separazione
    
    return classifica
# --- Funzioni di Setup e Utility ---

def initialize_grid(size):
    return [[MAP_UNKNOWN for _ in range(size)] for _ in range(size)]

def generate_fleet_config(size):
    if size <= 9: return [4, 3, 2, 2]
    elif size <= 12: return [5, 4, 3, 3, 2]
    elif size <= 16: return [6, 5, 4, 3, 3, 2]
    elif size <= 20: return [7, 6, 5, 4, 4, 3, 2]
    else: return [8, 7, 6, 5, 4, 4, 3, 3]

def parse_coordinate(coord_str, size):
    if len(coord_str) < 2 or not coord_str[0].isalpha() or not coord_str[1:].isdigit():
        raise ValueError("Formato non valido. Usa una lettera e un numero (es. A1).")
    col = ord(coord_str[0]) - ord('A')
    row_input = int(coord_str[1:])
    row = size - row_input
    if not (0 <= row < size and 0 <= col < size and 1 <= row_input <= size):
        raise ValueError("Coordinate fuori dalla griglia.")
    return row, col

def can_place_ship(grid, size, length, is_vertical, start_row, start_col):
    if is_vertical:
        if start_row + length > size: return False
        end_row, end_col = start_row + length - 1, start_col
    else:
        if start_col + length > size: return False
        end_row, end_col = start_row, start_col + length - 1
    for r in range(max(0, start_row - 1), min(size, end_row + 2)):
        for c in range(max(0, start_col - 1), min(size, end_col + 2)):
            if grid[r][c] != MAP_UNKNOWN:
                return False
    return True

def place_ships_randomly(player_grid, ships_lengths, size):
    fleet = []
    for length in ships_lengths:
        ship = Ship(length)
        placed = False
        while not placed:
            is_vertical = random.choice([True, False])
            if is_vertical:
                start_row = random.randint(0, size - length)
                start_col = random.randint(0, size - 1)
            else:
                start_row = random.randint(0, size - 1)
                start_col = random.randint(0, size - length)
            if can_place_ship(player_grid, size, length, is_vertical, start_row, start_col):
                if is_vertical:
                    for i in range(length):
                        row, col = start_row + i, start_col
                        player_grid[row][col] = ship
                        ship.coordinates.append((row, col))
                else:
                    for i in range(length):
                        row, col = start_row, start_col + i
                        player_grid[row][col] = ship
                        ship.coordinates.append((row, col))
                fleet.append(ship)
                placed = True
    return fleet

def place_ships_manually(player_grid, ships_lengths, size):
    fleet = []
    for i, length in enumerate(ships_lengths):
        placed = False
        while not placed:
            print("\nLa tua flotta:")
            print_grid_setup(player_grid, size)
            print(f"Posiziona la tua nave da {length} caselle.")
            coord_str = input(f"Inserisci coordinata (es. A1), 'ia' (auto) o 'q' (esci): ").strip().upper()
            if coord_str == 'Q':
                print("Uscita dal gioco in corso...")
                sys.exit()
            if coord_str == 'IA':
                print("Posizionamento automatico per le navi rimanenti...")
                remaining_lengths = ships_lengths[i:]
                temp_grid_for_random = [row[:] for row in player_grid]
                remaining_fleet = place_ships_randomly(temp_grid_for_random, remaining_lengths, size)
                fleet.extend(remaining_fleet)
                for r in range(size):
                    for c in range(size):
                        player_grid[r][c] = temp_grid_for_random[r][c]
                return fleet
            try:
                start_row, start_col = parse_coordinate(coord_str, size)
                orientation = input("Inserisci l'orientamento ('V' per verticale, 'O' per orizzontale): ").strip().upper()
                if orientation not in ['V', 'O']:
                    print("Errore: l'orientamento deve essere 'V' o 'O'.")
                    continue
                is_vertical = (orientation == 'V')
                if can_place_ship(player_grid, size, length, is_vertical, start_row, start_col):
                    ship = Ship(length)
                    if is_vertical:
                        for j in range(length):
                            row, col = start_row + j, start_col
                            player_grid[row][col] = ship; ship.coordinates.append((row, col))
                    else:
                        for j in range(length):
                            row, col = start_row, start_col + j
                            player_grid[row][col] = ship; ship.coordinates.append((row, col))
                    fleet.append(ship)
                    placed = True
                    print(f"Nave da {length} posizionata con successo!")
                else:
                    print("Posizione non valida! La nave uscirebbe dalla griglia o toccherebbe un'altra nave.")
            except ValueError as e:
                print(f"Errore: {e}. Riprova.")
    return fleet

# --- Funzioni di Logica del Gioco ---

def take_shot(opponent_grid, opponent_fleet, hits_grid, row, col):
    if hits_grid[row][col] != MAP_UNKNOWN:
        return "Posizione già colpita!", None
    target = opponent_grid[row][col]
    if isinstance(target, Ship):
        hits_grid[row][col] = INTERNAL_HIT
        target.hits.append((row, col))
        if target.is_sunk():
            for r_ship, c_ship in target.coordinates:
                hits_grid[r_ship][c_ship] = INTERNAL_SUNK
            return "Colpito e affondato!", target
        else:
            return "Colpito!", target
    else:
        hits_grid[row][col] = MAP_MISS
        return "Mancato!", None

def all_ships_sunk(fleet):
    return all(ship.is_sunk() for ship in fleet)

def calculate_stats(hits_grid): # <-- NUOVA funzione di utilità
    """Calcola colpi totali e precisione da una griglia di colpi."""
    hits, misses = 0, 0
    for row in hits_grid:
        hits += row.count(INTERNAL_HIT) + row.count(INTERNAL_SUNK)
        misses += row.count(MAP_MISS)
    total_shots = hits + misses
    accuracy = (hits / total_shots * 100) if total_shots > 0 else 0.0
    return total_shots, accuracy

# --- Intelligenza Artificiale (IA) ---

def _calculate_hunt_probabilities(hits_grid, size, ship_lengths):
    prob_map = [[0 for _ in range(size)] for _ in range(size)]
    for length in ship_lengths:
        for r in range(size):
            for c in range(size):
                if c + length <= size:
                    if all(hits_grid[r][c+i] == MAP_UNKNOWN for i in range(length)):
                        for i in range(length):
                            prob_map[r][c+i] += 1
                if r + length <= size:
                    if all(hits_grid[r+i][c] == MAP_UNKNOWN for i in range(length)):
                        for i in range(length):
                            prob_map[r+i][c] += 1
    return prob_map

def _calculate_target_probabilities(hits_grid, size, ship_lengths, target_hits):
    prob_map = [[0 for _ in range(size)] for _ in range(size)]
    for length in ship_lengths:
        for r_hit, c_hit in target_hits:
            for offset in range(length):
                # Orizzontale
                start_r, start_c = r_hit, c_hit - offset
                if start_c + length <= size and start_c >= 0:
                    possible_coords = [(start_r, start_c + i) for i in range(length)]
                    if all(hits_grid[r][c] in [MAP_UNKNOWN, INTERNAL_HIT] for r,c in possible_coords) and \
                       all(hit in possible_coords for hit in target_hits):
                        for r,c in possible_coords:
                            if hits_grid[r][c] == MAP_UNKNOWN:
                                prob_map[r][c] += 1
                # Verticale
                start_r, start_c = r_hit - offset, c_hit
                if start_r + length <= size and start_r >= 0:
                    possible_coords = [(start_r + i, start_c) for i in range(length)]
                    if all(hits_grid[r][c] in [MAP_UNKNOWN, INTERNAL_HIT] for r,c in possible_coords) and \
                       all(hit in possible_coords for hit in target_hits):
                        for r,c in possible_coords:
                            if hits_grid[r][c] == MAP_UNKNOWN:
                                prob_map[r][c] += 1
    return prob_map

def ai_advanced_shot(hits_grid, size, opponent_fleet, ai_target_hits):
    remaining_ship_lengths = [ship.length for ship in opponent_fleet if not ship.is_sunk()]
    if not ai_target_hits:
        prob_map = _calculate_hunt_probabilities(hits_grid, size, remaining_ship_lengths)
    else:
        prob_map = _calculate_target_probabilities(hits_grid, size, remaining_ship_lengths, ai_target_hits)
    max_prob = -1
    best_shots = []
    for r in range(size):
        for c in range(size):
            if prob_map[r][c] > max_prob:
                max_prob = prob_map[r][c]
                best_shots = [(r, c)]
            elif prob_map[r][c] == max_prob and prob_map[r][c] > 0:
                best_shots.append((r, c))
    if not best_shots:
        possible_shots = [(r, c) for r in range(size) for c in range(size) if hits_grid[r][c] == MAP_UNKNOWN]
        return random.choice(possible_shots) if possible_shots else (0,0)
    return random.choice(best_shots)

# --- Funzioni di Visualizzazione ---

def print_grid_setup(grid, size):
    """Stampa una singola griglia durante la fase di posizionamento."""
    col_labels = "   " + "".join([chr(ord('A') + i) for i in range(size)])
    print(col_labels)
    for r in range(size):
        row_label = size - r
        row_str = f"{row_label:<2}|"
        for c in range(size):
            cell = grid[r][c]
            if isinstance(cell, Ship):
                row_str += FLEET_SHIP
            else:
                row_str += MAP_UNKNOWN
        print(row_str + "|")

def create_target_grid(size, user_hits_on_ai):
    grid = [[MAP_UNKNOWN for _ in range(size)] for _ in range(size)]
    for r in range(size):
        for c in range(size):
            if user_hits_on_ai[r][c] == MAP_MISS: grid[r][c] = MAP_MISS
            elif user_hits_on_ai[r][c] == INTERNAL_HIT: grid[r][c] = TARGET_HIT
            elif user_hits_on_ai[r][c] == INTERNAL_SUNK: grid[r][c] = TARGET_SUNK
    return grid

def create_fleet_grid(size, user_grid, ai_hits_on_user):
    grid = [[MAP_UNKNOWN for _ in range(size)] for _ in range(size)]
    for r in range(size):
        for c in range(size):
            if isinstance(user_grid[r][c], Ship):
                ship = user_grid[r][c]
                if ship.is_sunk(): grid[r][c] = FLEET_SUNK
                elif (r, c) in ship.hits: grid[r][c] = FLEET_HIT
                else: grid[r][c] = FLEET_SHIP
            elif ai_hits_on_user[r][c] == MAP_MISS:
                grid[r][c] = MAP_MISS
    return grid

def print_dual_grids(left_grid, right_grid, size):
    left_title, right_title = "GRIGLIA BERSAGLIO", "LA TUA FLOTTA"
    spacing = " " * (size - len(left_title) + 5)
    print(f"\n{left_title}{spacing}{right_title}")
    col_labels = "   " + "".join([chr(ord('A') + i) for i in range(size)])
    spacing_grids = "      "
    print(f"{col_labels}{spacing_grids}{col_labels}")
    for r in range(size):
        row_label = size - r
        left_row_str = f"{row_label:<2}|" + "".join(left_grid[r]) + "|"
        right_row_str = f"{row_label:<2}|" + "".join(right_grid[r]) + "|"
        print(f"{left_row_str}{spacing_grids}{right_row_str}")
    bottom_frame = "  +" + "-" * size + "+"
    print(f"{bottom_frame}{spacing_grids}{bottom_frame}")

def build_prompt_string(turn, user_fleet, ai_fleet, user_hits_on_ai, ai_hits_on_user):
    user_sunk_ships = sum(1 for ship in user_fleet if ship.is_sunk())
    ai_sunk_ships = sum(1 for ship in ai_fleet if ship.is_sunk())
    
    # Usa la nuova funzione per calcolare le statistiche
    _, user_accuracy = calculate_stats(user_hits_on_ai)
    _, ai_accuracy = calculate_stats(ai_hits_on_user)
    
    user_ships_str = f"{len(user_fleet) - user_sunk_ships}/{len(user_fleet)}"
    ai_ships_str = f"{len(ai_fleet) - ai_sunk_ships}/{len(ai_fleet)}"
    return f"T:{turn} N:{user_ships_str} A:{ai_ships_str} p%:{user_accuracy:.1f}/{ai_accuracy:.1f}> "

# --- Funzione Principale ---

def main():
    print(f"\nBenvenuto alla Battaglia Navale!\n\t\t{VERSIONE}")
    
    # Carica la classifica all'inizio
    classifica = load_classifica()

    size = 0
    while not (8 <= size <= 26):
        try:
            size_input = input("Inserisci la dimensione della griglia (da 8 a 26): ").strip()
            if not size_input: continue
            size = int(size_input)
            if not (8 <= size <= 26):
                print("Dimensione non valida. Inserisci un numero tra 8 e 26.")
        except ValueError:
            print("Input non valido. Inserisci un numero.")
    ships_config = generate_fleet_config(size)
    print(f"Giocherai su una griglia {size}x{size} con {len(ships_config)} navi.")
    user_grid, ai_grid = initialize_grid(size), initialize_grid(size)
    user_fleet = place_ships_manually(user_grid, ships_config, size)
    ai_fleet = place_ships_randomly(ai_grid, ships_config, size)
    print("\nOttimo! La tua flotta è schierata. Che la battaglia abbia inizio!")
    user_hits_on_ai, ai_hits_on_user = initialize_grid(size), initialize_grid(size)
    ai_target_hits = []
    game_over = False
    winner = None # Variabile per sapere chi ha vinto
    turn = 1
    while not game_over:
        target_grid = create_target_grid(size, user_hits_on_ai)
        fleet_grid = create_fleet_grid(size, user_grid, ai_hits_on_user)
        print_dual_grids(target_grid, fleet_grid, size)
        valid_shot = False
        while not valid_shot:
            try:
                prompt_text = build_prompt_string(turn, user_fleet, ai_fleet, user_hits_on_ai, ai_hits_on_user)
                shot_str = input(prompt_text).strip().upper()
                if shot_str == 'Q':
                    print("Uscita dal gioco in corso...")
                    sys.exit()
                if not shot_str: continue
                row, col = parse_coordinate(shot_str, size)
                result, hit_ship = take_shot(ai_grid, ai_fleet, user_hits_on_ai, row, col)
                print(f"Risultato del tuo colpo: >> {result} <<")
                valid_shot = True
                if all_ships_sunk(ai_fleet):
                    print("\n🎉 CONGRATULAZIONI! Hai vinto! 🎉")
                    winner = "Player"
                    game_over = True
            except ValueError as e:
                print(f"Errore: {e}. Riprova.")
        if game_over: break
        print("\n--- Turno dell'IA ---")
        ai_row, ai_col = ai_advanced_shot(ai_hits_on_user, size, user_fleet, ai_target_hits)
        result, hit_ship = take_shot(user_grid, user_fleet, ai_hits_on_user, ai_row, ai_col)
        shot_coord_str = f"{chr(ord('A') + ai_col)}{size - ai_row}"
        print(f"L'IA spara in {shot_coord_str}. Risultato: >> {result} <<")
        if "Colpito" in result:
            ai_target_hits.append((ai_row, ai_col))
            if "affondato" in result:
                ai_target_hits = []
        if all_ships_sunk(user_fleet):
            print("\n☠️ PECCATO! L'IA ha vinto. ☠️")
            winner = "IA"
            game_over = True
        turn += 1

    # --- Logica di Fine Partita (NUOVA) ---
    if game_over:
        if winner == "Player":
            winner_name = ""
            while not winner_name:
                winner_name = input("Inserisci il tuo nome per la classifica: ").strip()
                if not winner_name:
                    print("Il nome non può essere vuoto.")
            shots, accuracy = calculate_stats(user_hits_on_ai)
        else: # L'IA ha vinto
            winner_name = generate_ai_name()
            print(f"L'IA si registra in classifica con il nome: {winner_name}")
            shots, accuracy = calculate_stats(ai_hits_on_user)
            
        # Aggiorna, mostra e salva la classifica
        classifica_aggiornata = update_and_display_classifica(classifica, size, winner_name, shots, accuracy)
        save_classifica(classifica_aggiornata)
        print("\nClassifica salvata. Grazie per aver giocato!")


if __name__ == "__main__":
    main()