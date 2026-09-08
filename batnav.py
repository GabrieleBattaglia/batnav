# batnav, battaglia navale accessibile contro l'intelligenza artificiale.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
# Data concepimento: 24 settembre 2025.
# 03/09/2026: i suoni passano ad Acusticator, di GBUtils.
# 08/09/2026: revisione 1 del refactoring generale, versione 3.0.0.

import contextlib
import json
import os
import random
import sys
import time
from datetime import date, datetime

from GBUtils import Acusticator, dgt, enter_escape, gestisci_aggiornamento, key, manuale, menu

from batnav_ia import MotoreIA

APP_NAME = "batnav"
VERSIONE = "3.0.0"
RELEASE_DATE = "2026-09-08"
AUTORI = "Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)"
API_RELEASE = "https://api.github.com/repos/GabrieleBattaglia/batnav/releases/latest"
CLASSIFICA_MAX_VOCI = 15
LATO_MIN = 8
LATO_MAX = 26
LATO_PREDEFINITO = 10
# Larghezza dei blocchi in cui si spezzano le righe informative, per la
# lettura sul display braille.
LARGHEZZA_BLOCCO = 40
# Quante disposizioni casuali si confrontano per scegliere quella della
# flotta, e quanti tentativi si concedono a una nave prima di ricominciare.
DISPOSIZIONI_CANDIDATE = 24
TENTATIVI_PER_NAVE = 500
RIPARTENZE_MASSIME = 20
# Respiro fra l'esito del tuo colpo e la risposta dell'avversario, in
# secondi: senza, i due suoni si accavallano e non si capisce chi ha sparato.
PAUSA_PRIMA_DELLA_IA = 1.0

# I suoni del gioco, evento per evento. I nomi sono quelli della collezione
# condivisa Acu_Collection.json: per cambiare un suono basta cambiare qui.
SUONI = {
    "avvio": "partenza",
    "nave_posizionata": "doppio_tic_conferma",
    "sparo": "passaggio_veloce",
    "in_arrivo": "volo_radente",
    "mancato": "respiro_di_vapore",
    "colpito": "scudisciata",
    "affondato": "jingle_livello_superato",
    "affondata": "gabryscola_sconfitta",
    "errore": "errore_secco",
    "gia_colpita": "rifiutato",
    "vittoria": "fanfara_retro",
    "sconfitta": "jingle_missione_fallita",
    "classifica": "apertura",
    "salvato": "written_ok",
}
DESCRIZIONI_SUONI = {
    "avvio": "il gioco parte",
    "nave_posizionata": "una tua nave e' stata posata",
    "sparo": "il tuo colpo parte",
    "in_arrivo": "il colpo dell'avversario arriva",
    "mancato": "colpo in acqua",
    "colpito": "nave colpita",
    "affondato": "hai affondato una nave avversaria",
    "affondata": "l'avversario ha affondato una tua nave",
    "errore": "coordinata non valida",
    "gia_colpita": "casella gia' colpita",
    "vittoria": "hai vinto",
    "sconfitta": "hai perso",
    "classifica": "compare la classifica",
    "salvato": "classifica salvata",
}

NATO_PHONETIC_ALPHABET = {
    "A": "Alfa",
    "B": "Bravo",
    "C": "Charlie",
    "D": "Delta",
    "E": "Echo",
    "F": "Foxtrot",
    "G": "Golf",
    "H": "Hotel",
    "I": "India",
    "J": "Juliett",
    "K": "Kilo",
    "L": "Lima",
    "M": "Mike",
    "N": "November",
    "O": "Oscar",
    "P": "Papa",
    "Q": "Quebec",
    "R": "Romeo",
    "S": "Sierra",
    "T": "Tango",
    "U": "Uniform",
    "V": "Victor",
    "W": "Whiskey",
    "X": "X-ray",
    "Y": "Yankee",
    "Z": "Zulu",
}

# Simboli con cui ciascuno annota cio' che sa della griglia dell'altro.
MAP_UNKNOWN = "."
MAP_MISS = "o"
INTERNAL_HIT = "x"
INTERNAL_SUNK = "#"
# Simboli delle due griglie mostrate al giocatore.
TARGET_HIT = "X"
TARGET_SUNK = "A"
FLEET_SHIP = "S"
FLEET_HIT = "c"
FLEET_SUNK = "F"

# Esiti di un colpo, con la frase che li annuncia e il suono che li accompagna.
ESITO_GIA_COLPITA = "gia_colpita"
ESITO_MANCATO = "mancato"
ESITO_COLPITO = "colpito"
ESITO_AFFONDATO = "affondato"
FRASI_ESITO = {
    ESITO_MANCATO: "Mancato!",
    ESITO_COLPITO: "Colpito!",
    ESITO_AFFONDATO: "Colpito e affondato!",
}
MENU_PRINCIPALE = {
    "gioca": "Nuova partita",
    "classifica": "Classifica",
    "manuale": "Manuale",
    "suoni": "Ascolta i suoni del gioco",
    "esci": "Esci",
}


# Percorsi.


def cartella_dati():
    """Dove stanno i file scrivibili: accanto all'eseguibile, o al sorgente.

    Mai la directory di lavoro: fino alla 2.4.1 la classifica si cercava li',
    e avviando il gioco da un'altra cartella ne nasceva una seconda.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def percorso_risorsa(nome):
    """Dove sta una risorsa in sola lettura, come il manuale: da compilato dentro il pacchetto."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", None)
        if base and os.path.isfile(os.path.join(base, nome)):
            return os.path.join(base, nome)
    return os.path.join(cartella_dati(), nome)


CLASSIFICA_FILE = os.path.join(cartella_dati(), "batnav_charts.json")
MANUALE_FILE = percorso_risorsa("README.md")


# Testi e suoni.


def blocchi(testo, larghezza=LARGHEZZA_BLOCCO):
    """Spezza un testo in righe di circa larghezza caratteri, senza tagliare le parole."""
    righe = []
    corrente = ""
    for parola in testo.split():
        if not corrente:
            corrente = parola
        elif len(corrente) + 1 + len(parola) <= larghezza:
            corrente += " " + parola
        else:
            righe.append(corrente)
            corrente = parola
    if corrente:
        righe.append(corrente)
    return righe


def dillo(testo):
    """Stampa un testo informativo in blocchi di circa quaranta caratteri."""
    for riga in blocchi(testo):
        print(riga)


def virgola(numero, decimali=1):
    """Un numero con la virgola decimale, come si legge in italiano."""
    return f"{numero:.{decimali}f}".replace(".", ",")


def suona(evento, sync=False):
    """Riproduce il suono associato a un evento del gioco."""
    nome = SUONI.get(evento)
    if nome:
        Acusticator.play(nome, sync=sync)


def prova_suoni():
    """Fa ascoltare i suoni del gioco uno alla volta, dicendo a cosa servono."""
    print("I suoni del gioco, uno per volta.")
    print("Invio per il prossimo, escape per smettere.")
    for evento, nome in SUONI.items():
        print(f"{DESCRIZIONI_SUONI[evento]}: {nome}")
        suona(evento, sync=True)
        if key("\rProssimo> \r") in ("\x1b", "esc"):
            print()
            break
    print("Fine dei suoni.")


def mostra_manuale():
    """Mostra il manuale una pagina alla volta."""
    try:
        manuale(nf=MANUALE_FILE, nome="Manuale di batnav")
    except (OSError, ValueError) as e:
        dillo(f"Manuale non disponibile: {e}")


# Classifica.


def _data_iso(testo):
    """Porta la data in AAAA-MM-GG.

    Le voci salvate fino alla 2.4.1 la scrivevano GG/MM/AAAA, e alcune non
    ce l'hanno affatto: in quel caso resta vuota.
    """
    if not isinstance(testo, str):
        return ""
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(testo.strip(), formato).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _data_italiana(iso):
    """La data come GG/MM/AAAA, oppure vuota se non si sa."""
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return ""


def _voce_valida(voce):
    """True se la voce ha tutto cio' che serve; nel frattempo la normalizza."""
    if not isinstance(voce, dict):
        return False
    nome = voce.get("nome")
    colpi = voce.get("colpi")
    perc = voce.get("perc_colpi")
    if not isinstance(nome, str) or not nome.strip():
        return False
    if isinstance(colpi, bool) or not isinstance(colpi, int) or colpi < 1:
        return False
    if isinstance(perc, bool) or not isinstance(perc, int | float) or not 0 <= perc <= 100:
        return False
    voce["nome"] = nome.strip()
    voce["perc_colpi"] = float(perc)
    voce["data"] = _data_iso(voce.get("data"))
    return True


def ordina_classifica(voci):
    """Meno colpi prima; a parita', precisione piu' alta; poi il record piu' vecchio."""
    return sorted(voci, key=lambda v: (v["colpi"], -v["perc_colpi"], v["data"] or "9999-99-99"))


def _leggi_json(percorso):
    """Il contenuto del file, che deve essere un dizionario; altrimenti ValueError."""
    with open(percorso, encoding="utf-8") as f:
        dati = json.load(f)
    if not isinstance(dati, dict):
        raise ValueError("il contenuto non e' un dizionario")
    return dati


def load_classifica():
    """Legge la classifica. Restituisce la classifica e un avviso, vuoto se e' andato tutto bene.

    Se il file principale non si legge prova la copia di sicurezza; se nemmeno
    quella, mette da parte il file rotto con un altro nome, cosi' il prossimo
    salvataggio non lo cancella, e riparte da vuota dicendolo.
    """
    if not os.path.exists(CLASSIFICA_FILE):
        return {}, ""
    avvisi = []
    try:
        dati = _leggi_json(CLASSIFICA_FILE)
    except (OSError, ValueError) as e:
        avvisi.append(f"Classifica non leggibile: {e}.")
        copia = CLASSIFICA_FILE + ".bak"
        try:
            dati = _leggi_json(copia)
            avvisi.append("Uso la copia di sicurezza.")
        except (OSError, ValueError):
            rotto = CLASSIFICA_FILE + ".rotto"
            with contextlib.suppress(OSError):
                os.replace(CLASSIFICA_FILE, rotto)
            avvisi.append(f"Riparto da vuota, il file rotto e' {os.path.basename(rotto)}.")
            return {}, " ".join(avvisi)
    classifica = {}
    scartate = 0
    for chiave, voci in dati.items():
        if not (isinstance(chiave, str) and chiave.isdigit() and isinstance(voci, list)):
            scartate += len(voci) if isinstance(voci, list) else 1
            continue
        buone = [v for v in voci if _voce_valida(v)]
        scartate += len(voci) - len(buone)
        if buone:
            classifica[chiave] = ordina_classifica(buone)[:CLASSIFICA_MAX_VOCI]
    if scartate:
        avvisi.append(f"Scartate {scartate} voci incomplete della classifica.")
    return classifica, " ".join(avvisi)


def save_classifica(classifica):
    """Scrive su un file temporaneo e sostituisce solo a scrittura riuscita.

    La versione precedente resta come copia di sicurezza. Restituisce un
    messaggio di errore, vuoto se il salvataggio e' andato bene.
    """
    temporaneo = CLASSIFICA_FILE + ".tmp"
    copia = CLASSIFICA_FILE + ".bak"
    try:
        with open(temporaneo, "w", encoding="utf-8") as f:
            json.dump(classifica, f, indent=4, ensure_ascii=False)
        if os.path.exists(CLASSIFICA_FILE):
            os.replace(CLASSIFICA_FILE, copia)
        os.replace(temporaneo, CLASSIFICA_FILE)
    except OSError as e:
        with contextlib.suppress(OSError):
            os.remove(temporaneo)
        return f"Classifica non salvata: {e}"
    return ""


def aggiorna_classifica(classifica, size, nome, colpi, precisione):
    """Inserisce il risultato e restituisce la posizione raggiunta, o None se resta fuori."""
    chiave = str(size)
    voce = {"nome": nome, "colpi": colpi, "perc_colpi": precisione, "data": date.today().strftime("%Y-%m-%d")}
    voci = ordina_classifica([*classifica.get(chiave, []), voce])[:CLASSIFICA_MAX_VOCI]
    classifica[chiave] = voci
    for posizione, v in enumerate(voci, 1):
        if v is voce:
            return posizione
    return None


def mostra_classifica(classifica, size):
    """La classifica di una dimensione, una frase per voce."""
    voci = classifica.get(str(size), [])
    if not voci:
        print(f"Nessun risultato per la griglia {size} per {size}.")
        return
    print(f"Classifica della griglia {size} per {size}.")
    for posizione, v in enumerate(voci, 1):
        data = _data_italiana(v["data"])
        quando = f"il {data}" if data else "data sconosciuta"
        dillo(f"{posizione}. {v['nome']}, {v['colpi']} colpi, precisione {virgola(v['perc_colpi'])} per cento, {quando}.")


def mostra_tutte_le_classifiche(classifica):
    dimensioni = sorted(int(k) for k in classifica)
    if not dimensioni:
        print("La classifica e' ancora vuota.")
        return
    suona("classifica")
    for size in dimensioni:
        mostra_classifica(classifica, size)


def generate_ai_name():
    """Un nome casuale per l'avversario, come IA-Fofofo."""
    consonanti = "BCDFGHJKLMNPQRSTVWXYZ"
    vocali = "AEIOU"
    c1, c2 = random.choice(consonanti), random.choice(consonanti)
    v1, v2 = random.choice(vocali), random.choice(vocali)
    return f"IA-{(c1 + v1 + c2 + v2 + c2 + v2).lower().title()}"


# Griglie e flotte.


class Ship:
    def __init__(self, length):
        self.length = length
        self.coordinates = []
        self.hits = []

    def is_sunk(self):
        return len(self.hits) == self.length


class Tiri:
    """Quanti colpi sono partiti davvero e quanti sono andati a segno.

    Fino alla 2.4.1 i colpi si contavano sulla griglia, e la regola che marca
    d'ufficio i dintorni di una nave affondata li gonfiava tutti.
    """

    def __init__(self):
        self.colpi = 0
        self.centri = 0

    def registra(self, esito):
        self.colpi += 1
        if esito != ESITO_MANCATO:
            self.centri += 1

    @property
    def precisione(self):
        return self.centri / self.colpi * 100 if self.colpi else 0.0


def initialize_grid(size):
    return [[MAP_UNKNOWN for _ in range(size)] for _ in range(size)]


def generate_fleet_config(size):
    if size <= 9:
        return [4, 3, 2, 2]
    if size <= 12:
        return [5, 4, 3, 3, 2]
    if size <= 16:
        return [6, 5, 4, 3, 3, 2]
    if size <= 20:
        return [7, 6, 5, 4, 4, 3, 2]
    return [8, 7, 6, 5, 4, 4, 3, 3]


def parse_coordinate(coord_str, size):
    if len(coord_str) < 2 or not coord_str[0].isalpha() or not coord_str[1:].isdigit():
        raise ValueError("Formato non valido. Usa una lettera e un numero, come A1.")
    col = ord(coord_str[0]) - ord("A")
    row_input = int(coord_str[1:])
    row = size - row_input
    if not (0 <= row < size and 0 <= col < size and 1 <= row_input <= size):
        raise ValueError("Coordinate fuori dalla griglia.")
    return row, col


def nome_casella(row, col, size):
    """La casella detta con l'alfabeto fonetico, come Alfa 3."""
    return f"{NATO_PHONETIC_ALPHABET[chr(ord('A') + col)]} {size - row}"


def can_place_ship(grid, size, length, is_vertical, start_row, start_col):
    if is_vertical:
        if start_row + length > size:
            return False
        end_row, end_col = start_row + length - 1, start_col
    else:
        if start_col + length > size:
            return False
        end_row, end_col = start_row, start_col + length - 1
    for r in range(max(0, start_row - 1), min(size, end_row + 2)):
        for c in range(max(0, start_col - 1), min(size, end_col + 2)):
            if grid[r][c] != MAP_UNKNOWN:
                return False
    return True


def posa_nave(grid, length, is_vertical, start_row, start_col):
    """Mette una nave sulla griglia e la restituisce."""
    ship = Ship(length)
    for i in range(length):
        row, col = (start_row + i, start_col) if is_vertical else (start_row, start_col + i)
        grid[row][col] = ship
        ship.coordinates.append((row, col))
    return ship


def place_ships_randomly(player_grid, ships_lengths, size):
    """Dispone a caso le navi, ricominciando da capo se una non trova posto.

    Con le flotte attuali una nave trova posto sempre in pochi tentativi, ma
    un ciclo senza uscita resta un ciclo senza uscita: oltre il limite si
    tolgono le navi posate in questa chiamata e si riprova.
    """
    for _ in range(RIPARTENZE_MASSIME):
        fleet = []
        riuscito = True
        for length in ships_lengths:
            posata = False
            for _ in range(TENTATIVI_PER_NAVE):
                is_vertical = random.choice([True, False])
                start_row = random.randint(0, size - (length if is_vertical else 1))
                start_col = random.randint(0, size - (1 if is_vertical else length))
                if can_place_ship(player_grid, size, length, is_vertical, start_row, start_col):
                    fleet.append(posa_nave(player_grid, length, is_vertical, start_row, start_col))
                    posata = True
                    break
            if not posata:
                riuscito = False
                break
        if riuscito:
            return fleet
        for ship in fleet:
            for row, col in ship.coordinates:
                player_grid[row][col] = MAP_UNKNOWN
        print("Le navi non trovano posto, riprovo la disposizione.")
    raise RuntimeError(f"Impossibile disporre la flotta {ships_lengths} su una griglia {size} per {size}.")


def disponi_flotta(player_grid, ships_lengths, size, motore):
    """Dispone le navi scegliendo, fra piu' disposizioni casuali, una difficile da trovare."""
    candidate = []
    for _ in range(DISPOSIZIONI_CANDIDATE):
        scratch = [row[:] for row in player_grid]
        fleet = place_ships_randomly(scratch, ships_lengths, size)
        candidate.append([tuple(ship.coordinates) for ship in fleet])
    scelta = motore.scegli_disposizione(candidate, size, ships_lengths)
    fleet = []
    for coordinate in scelta:
        ship = Ship(len(coordinate))
        for row, col in coordinate:
            player_grid[row][col] = ship
            ship.coordinates.append((row, col))
        fleet.append(ship)
    return fleet


def place_ships_manually(player_grid, ships_lengths, size, motore):
    """Chiede al giocatore dove mettere ogni nave. Restituisce la flotta, o None se abbandona."""
    fleet = []
    for i, length in enumerate(ships_lengths):
        while True:
            print("La tua flotta:")
            print_grid_setup(player_grid, size)
            print(f"Nave da {length} caselle, la numero {i + 1} di {len(ships_lengths)}.")
            coord_str = dgt("Coordinata come A1, ia per l'automatico, q per uscire> ", kind="s", smin=1, smax=3).strip().upper()
            if coord_str == "Q":
                return None
            if coord_str == "IA":
                print("Le navi rimaste le dispongo io.")
                fleet.extend(disponi_flotta(player_grid, ships_lengths[i:], size, motore))
                return fleet
            try:
                start_row, start_col = parse_coordinate(coord_str, size)
            except ValueError as e:
                suona("errore")
                print(f"Errore: {e}")
                continue
            verso = dgt("Orientamento, v verticale oppure o orizzontale> ", kind="s", smin=1, smax=1).strip().upper()
            if verso not in ("V", "O"):
                suona("errore")
                print("L'orientamento deve essere v oppure o.")
                continue
            is_vertical = verso == "V"
            if can_place_ship(player_grid, size, length, is_vertical, start_row, start_col):
                fleet.append(posa_nave(player_grid, length, is_vertical, start_row, start_col))
                suona("nave_posizionata")
                print(f"Nave da {length} posizionata.")
                break
            suona("errore")
            dillo("Posizione non valida: la nave uscirebbe dalla griglia o toccherebbe un'altra nave.")
    return fleet


# Logica del gioco.


def take_shot(opponent_grid, hits_grid, row, col):
    """Registra un colpo e ne restituisce l'esito e la nave interessata, se c'e'."""
    if hits_grid[row][col] != MAP_UNKNOWN:
        return ESITO_GIA_COLPITA, None
    target = opponent_grid[row][col]
    if not isinstance(target, Ship):
        hits_grid[row][col] = MAP_MISS
        return ESITO_MANCATO, None
    hits_grid[row][col] = INTERNAL_HIT
    target.hits.append((row, col))
    if not target.is_sunk():
        return ESITO_COLPITO, target
    size = len(hits_grid)
    for r_ship, c_ship in target.coordinates:
        hits_grid[r_ship][c_ship] = INTERNAL_SUNK
    # Le navi non si toccano nemmeno in diagonale, quindi attorno a una nave
    # affondata non c'e' niente: si segna d'ufficio, senza contarli come colpi.
    for r_ship, c_ship in target.coordinates:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r_ship + dr, c_ship + dc
                if 0 <= nr < size and 0 <= nc < size and hits_grid[nr][nc] == MAP_UNKNOWN:
                    hits_grid[nr][nc] = MAP_MISS
    return ESITO_AFFONDATO, target


def all_ships_sunk(fleet):
    return all(ship.is_sunk() for ship in fleet)


# Visualizzazione. Le griglie in caratteri sono leggibili sul display
# braille, con le lettere delle colonne allineate alle caselle: restano
# come sono per scelta di Gabriele.


def print_grid_setup(grid, size):
    """Una sola griglia, durante il posizionamento."""
    print("   " + "".join(chr(ord("A") + i) for i in range(size)))
    for r in range(size):
        row_str = f"{size - r:<2}|"
        for c in range(size):
            row_str += FLEET_SHIP if isinstance(grid[r][c], Ship) else MAP_UNKNOWN
        print(row_str + "|")


def create_target_grid(size, user_hits_on_ai):
    grid = initialize_grid(size)
    simboli = {MAP_MISS: MAP_MISS, INTERNAL_HIT: TARGET_HIT, INTERNAL_SUNK: TARGET_SUNK}
    for r in range(size):
        for c in range(size):
            grid[r][c] = simboli.get(user_hits_on_ai[r][c], MAP_UNKNOWN)
    return grid


def create_fleet_grid(size, user_grid, ai_hits_on_user):
    grid = initialize_grid(size)
    for r in range(size):
        for c in range(size):
            cella = user_grid[r][c]
            if isinstance(cella, Ship):
                if cella.is_sunk():
                    grid[r][c] = FLEET_SUNK
                elif (r, c) in cella.hits:
                    grid[r][c] = FLEET_HIT
                else:
                    grid[r][c] = FLEET_SHIP
            elif ai_hits_on_user[r][c] == MAP_MISS:
                grid[r][c] = MAP_MISS
    return grid


def print_dual_grids(left_grid, right_grid, size):
    """Le due griglie affiancate, cornice compresa, con le lettere sotto."""
    spacing_grids = " " * 7
    print(f"GRIGLIA BERSAGLIO{spacing_grids}LA TUA FLOTTA")
    top_bottom_frame = "  +" + "-" * size + "+"
    col_labels = "   " + "".join(chr(ord("A") + i) for i in range(size))
    print(f"{top_bottom_frame}{spacing_grids}{top_bottom_frame}")
    for r in range(size):
        row_label = size - r
        left_row_str = f"{row_label:<2}|" + "".join(left_grid[r]) + "|"
        right_row_str = f"{row_label:<2}|" + "".join(right_grid[r]) + "|"
        print(f"{left_row_str}{spacing_grids}{right_row_str}")
    print(f"{top_bottom_frame}{spacing_grids}{top_bottom_frame}")
    print(f"{col_labels}{spacing_grids}{col_labels}")


# La partita.


class Partita:
    """Lo stato di una partita e i suoi turni."""

    def __init__(self, nome_giocatore, size, motore):
        self.nome = nome_giocatore
        self.nome_ia = generate_ai_name()
        self.size = size
        self.motore = motore
        self.motore.nuova_partita()
        self.lunghezze = generate_fleet_config(size)
        self.griglia_giocatore = initialize_grid(size)
        self.griglia_ia = initialize_grid(size)
        self.flotta_giocatore = []
        self.flotta_ia = []
        # Cio' che ognuno sa della griglia dell'altro.
        self.colpi_su_ia = initialize_grid(size)
        self.colpi_su_giocatore = initialize_grid(size)
        self.tiri_giocatore = Tiri()
        self.tiri_ia = Tiri()
        self.turno = 1
        self.vincitore = None

    def prompt(self):
        """La riga del turno, compatta: T turno, N tue navi, A navi avversarie, p% precisioni."""
        navi_tue = sum(1 for s in self.flotta_giocatore if not s.is_sunk())
        navi_ia = sum(1 for s in self.flotta_ia if not s.is_sunk())
        quante = len(self.flotta_giocatore)
        return (
            f"T:{self.turno} N:{navi_tue}/{quante} A:{navi_ia}/{quante} "
            f"p%:{self.tiri_giocatore.precisione:.1f}/{self.tiri_ia.precisione:.1f}> "
        )

    def mostra_griglie(self):
        target_grid = create_target_grid(self.size, self.colpi_su_ia)
        fleet_grid = create_fleet_grid(self.size, self.griglia_giocatore, self.colpi_su_giocatore)
        print_dual_grids(target_grid, fleet_grid, self.size)

    def schiera(self):
        """Dispone le due flotte. Restituisce False se il giocatore abbandona."""
        print(f"Griglia {self.size} per {self.size}, {len(self.lunghezze)} navi per parte.")
        dillo("Lunghezze delle navi: " + ", ".join(str(n) for n in self.lunghezze) + ".")
        if enter_escape("Le navi le disponi tu? invio sì, escape lascia fare al programma> "):
            self.flotta_giocatore = place_ships_manually(self.griglia_giocatore, self.lunghezze, self.size, self.motore)
            if self.flotta_giocatore is None:
                return False
        else:
            self.flotta_giocatore = disponi_flotta(self.griglia_giocatore, self.lunghezze, self.size, self.motore)
            print("Flotta disposta.")
        self.flotta_ia = disponi_flotta(self.griglia_ia, self.lunghezze, self.size, self.motore)
        return True

    def annuncia_esito(self, frase, casella, esito, tuo_colpo):
        """Dice l'esito e lo suona; l'affondamento ha due suoni, uno per parte."""
        print(f"{frase} {casella}: {FRASI_ESITO[esito]}")
        if esito == ESITO_AFFONDATO and not tuo_colpo:
            suona("affondata")
        else:
            suona(esito)

    def turno_giocatore(self):
        """Chiede un colpo finche' non ne parte uno valido. Restituisce False se il giocatore abbandona."""
        while True:
            shot_str = dgt(self.prompt(), kind="s", smin=1, smax=3).strip().upper()
            if shot_str == "Q":
                if enter_escape("Abbandoni la partita? invio sì, escape no> "):
                    return False
                continue
            try:
                row, col = parse_coordinate(shot_str, self.size)
            except ValueError as e:
                suona("errore")
                print(f"Errore: {e}")
                continue
            esito, _ = take_shot(self.griglia_ia, self.colpi_su_ia, row, col)
            if esito == ESITO_GIA_COLPITA:
                suona("gia_colpita")
                print(f"{nome_casella(row, col, self.size)} l'hai gia' colpita, scegline un'altra.")
                continue
            suona("sparo", sync=True)
            self.tiri_giocatore.registra(esito)
            self.annuncia_esito("Spari in", nome_casella(row, col, self.size), esito, tuo_colpo=True)
            return True

    def turno_ia(self):
        lunghezze = [s.length for s in self.flotta_giocatore if not s.is_sunk()]
        scelta = self.motore.scegli_colpo(self.colpi_su_giocatore, lunghezze)
        if scelta is None:
            return
        row, col = scelta
        time.sleep(PAUSA_PRIMA_DELLA_IA)
        suona("in_arrivo", sync=True)
        esito, _ = take_shot(self.griglia_giocatore, self.colpi_su_giocatore, row, col)
        self.tiri_ia.registra(esito)
        self.annuncia_esito(f"{self.nome_ia} spara in", nome_casella(row, col, self.size), esito, tuo_colpo=False)

    def gioca(self):
        """La battaglia. Restituisce il vincitore, giocatore o IA, oppure None se il giocatore abbandona."""
        primo = random.choice(("giocatore", "IA"))
        print(f"Il sorteggio fa cominciare {self.nome if primo == 'giocatore' else self.nome_ia}.")
        if primo == "IA":
            self.turno_ia()
        self.mostra_griglie()
        while True:
            if not self.turno_giocatore():
                return None
            if all_ships_sunk(self.flotta_ia):
                self.vincitore = "giocatore"
                return self.vincitore
            self.turno_ia()
            if all_ships_sunk(self.flotta_giocatore):
                self.vincitore = "IA"
                return self.vincitore
            self.mostra_griglie()
            self.turno += 1

    def riepilogo(self):
        """Le statistiche della partita, a parole."""
        dillo(f"Partita finita al turno {self.turno}.")
        dillo(
            f"Tu: {self.tiri_giocatore.colpi} colpi, {self.tiri_giocatore.centri} a segno, "
            f"precisione {virgola(self.tiri_giocatore.precisione)} per cento."
        )
        dillo(
            f"{self.nome_ia}: {self.tiri_ia.colpi} colpi, {self.tiri_ia.centri} a segno, "
            f"precisione {virgola(self.tiri_ia.precisione)} per cento."
        )


def nuova_partita(classifica, motore):
    """Una partita intera, dalla scelta del nome alla classifica."""
    nome = ""
    while not nome:
        nome = dgt("Il tuo nome> ", kind="s", smin=1, smax=20).strip().title()
    size = dgt(
        f"Lato della griglia, da {LATO_MIN} a {LATO_MAX}, invio={LATO_PREDEFINITO}> ",
        kind="i",
        imin=LATO_MIN,
        imax=LATO_MAX,
        default=LATO_PREDEFINITO,
    )
    partita = Partita(nome, size, motore)
    print(f"Ciao {nome}, oggi sfidi {partita.nome_ia}.")
    if not partita.schiera():
        print("Partita annullata.")
        return
    print("Flotte schierate, che la battaglia abbia inizio.")
    dillo("Al prompt scrivi la casella, come B7. Q per abbandonare.")
    vincitore = partita.gioca()
    if vincitore is None:
        print("Partita abbandonata, niente classifica.")
        return
    if vincitore == "giocatore":
        print(f"Congratulazioni {nome}, hai vinto!")
        suona("vittoria", sync=True)
        nome_vincitore, tiri = nome, partita.tiri_giocatore
    else:
        print(f"Peccato, ha vinto {partita.nome_ia}.")
        suona("sconfitta", sync=True)
        nome_vincitore, tiri = partita.nome_ia, partita.tiri_ia
        print(f"{partita.nome_ia} si registra in classifica.")
    partita.riepilogo()
    posizione = aggiorna_classifica(classifica, size, nome_vincitore, tiri.colpi, tiri.precisione)
    if posizione:
        print(f"Risultato in classifica al posto {posizione}.")
    else:
        print("Risultato fuori dalle prime quindici posizioni.")
    errore = save_classifica(classifica)
    if errore:
        suona("errore")
        dillo(errore)
    else:
        suona("salvato")
    suona("classifica")
    mostra_classifica(classifica, size)


def main():
    print(f"Battaglia navale accessibile, batnav {VERSIONE} del {_data_italiana(RELEASE_DATE)}.")
    dillo(AUTORI)
    suona("avvio")
    if gestisci_aggiornamento(APP_NAME, VERSIONE, API_RELEASE):
        return
    classifica, avviso = load_classifica()
    if avviso:
        suona("errore")
        dillo(avviso)
    motore = MotoreIA(MAP_UNKNOWN, MAP_MISS, INTERNAL_HIT, INTERNAL_SUNK)
    while True:
        scelta = menu(d=MENU_PRINCIPALE, p="Cosa vuoi fare? ", show=True, keyslist=True, ordered=False)
        if scelta in (None, "esci"):
            break
        if scelta == "gioca":
            nuova_partita(classifica, motore)
        elif scelta == "classifica":
            mostra_tutte_le_classifiche(classifica)
        elif scelta == "manuale":
            mostra_manuale()
        elif scelta == "suoni":
            prova_suoni()
    print("Grazie per aver giocato, a presto.")
    Acusticator.close()


if __name__ == "__main__":
    main()
