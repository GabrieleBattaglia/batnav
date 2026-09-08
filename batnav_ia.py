# batnav_ia, il motore dell'avversario di batnav.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode)
# 08/09/2026: nasce con la 3.0.0 al posto delle mappe di probabilita' della 2.x.

"""Motore dell'intelligenza artificiale: campionamento Monte Carlo delle flotte.

Il motore riceve cio' che l'avversario sa della griglia del giocatore, cioe'
per ogni casella se e' ignota, mancata, colpita o parte di una nave gia'
affondata, e le lunghezze delle navi ancora in acqua. Da questi dati
costruisce a caso molte flotte complete compatibili con tutto cio' che si sa:
le navi non escono dalla griglia, non passano sulle caselle mancate ne' su
quelle delle navi affondate, non si toccano fra loro nemmeno in diagonale, e
ogni casella colpita ma non ancora affondata e' coperta da una nave. Ogni
casella ignota viene poi votata dal numero di flotte che ci passano sopra, e
il colpo va dove i voti sono di piu'.

Rispetto alle mappe di densita' della 2.x, che valutavano ogni nave da sola,
qui le navi si condizionano a vicenda: una nave lunga non entra in un buco
stretto, due navi non possono stare a contatto, e i colpi a segno vincolano
tutta la flotta e non soltanto la nave che li ha ricevuti. Misurato l'8
settembre 2026 su centinaia di partite simulate contro la 2.4.1 sulla stessa
disposizione: in attacco i due sono alla pari sulle flotte disposte a caso,
e questo e' circa un colpo piu' efficiente contro le flotte disposte in
difesa. La strategia avida, cioe' sparare dove la probabilita' e' piu'
alta, e' vicina all'ottimo per questo gioco, e la densita' indipendente
della 2.x la approssimava gia' bene: il margine in attacco e' piccolo per
natura, ed e' la difesa qui sotto a valere di piu'.

Finche' non c'e' nessun colpo a segno da inseguire, il tiro si limita alla
classe di parita' della nave piu' corta ancora in acqua: una nave lunga L
tocca sempre una casella ogni L, quindi le altre non servono a trovarla. E'
il filtro che aveva anche la 2.x, e senza di esso il campionamento da solo
non la batteva sulle griglie piccole.

Il motore lavora a tempo: campiona per una frazione di secondo e poi decide,
cosi' anche su una griglia da ventisei la risposta arriva in fretta. Se il
campionamento non produce abbastanza flotte, cosa che con le regole attuali
non dovrebbe succedere, ripiega su una scelta semplice: una casella accanto
a un colpo a segno, oppure una casella ignota a caso.

La stessa idea serve in difesa. Fra molte disposizioni casuali della propria
flotta il motore preferisce quelle che un cacciatore a densita' troverebbe
per ultime, cioe' con le navi sui bordi e negli angoli, dove passano meno
piazzamenti possibili, ma sceglie a caso fra le migliori per non diventare
prevedibile.
"""

import random
import time


class MotoreIA:
    """L'avversario. I quattro simboli sono quelli con cui il gioco marca la griglia."""

    def __init__(self, ignoto, mancato, colpito, affondato, tempo=0.35, campioni_max=4000, campioni_min=300):
        self.ignoto = ignoto
        self.mancato = mancato
        self.colpito = colpito
        self.affondato = affondato
        # Tempo di campionamento per ogni colpo, in secondi; oltre il
        # quadruplo si decide comunque con quello che c'e'.
        self.tempo = tempo
        self.campioni_max = campioni_max
        self.campioni_min = campioni_min
        # Quante flotte ha costruito l'ultima decisione e quanto ci ha messo,
        # per le statistiche e per le prove.
        self.ultimi_campioni = 0
        self.ultimo_tempo = 0.0
        self._cache_densita = {}
        self.parita = 0
        self.nuova_partita()

    def nuova_partita(self):
        """Sorteggia la classe di parita' con cui cacciare in questa partita."""
        # Sei valori coprono tutte le combinazioni di resto per le navi piu'
        # corte possibili, da due e da tre caselle.
        self.parita = random.randrange(6)

    # Attacco.

    def scegli_colpo(self, griglia, lunghezze):
        """La casella su cui sparare, come (riga, colonna), oppure None se non ne restano."""
        size = len(griglia)
        ignote = set()
        colpite = set()
        for r in range(size):
            for c in range(size):
                simbolo = griglia[r][c]
                if simbolo == self.ignoto:
                    ignote.add((r, c))
                elif simbolo == self.colpito:
                    colpite.add((r, c))
        if not ignote:
            return None
        if not lunghezze:
            return random.choice(sorted(ignote))
        consentite = ignote | colpite
        piazzamenti = self._piazzamenti(size, lunghezze, consentite)
        inizio = time.perf_counter()
        if any(not lista for lista in piazzamenti.values()):
            # Una nave non ha nessun posto possibile: cio' che si sa e'
            # contraddittorio e nessuna flotta lo rispetta, inutile provare.
            self.ultimi_campioni = 0
            self.ultimo_tempo = 0.0
            return self._ripiego(ignote, colpite)
        copre = self._coperture(piazzamenti, colpite)
        aloni = {cella: self._alone(cella, size) for cella in consentite}
        voti = dict.fromkeys(ignote, 0)
        accettati = 0
        scadenza = inizio + self.tempo
        scadenza_dura = inizio + self.tempo * 2
        while accettati < self.campioni_max:
            adesso = time.perf_counter()
            # Allo scadere del tempo si decide se i campioni bastano; se non
            # ne e' arrivato nemmeno uno non ne arriveranno abbastanza, e
            # si smette subito.
            if adesso >= scadenza_dura or (adesso >= scadenza and (accettati >= self.campioni_min or accettati == 0)):
                break
            flotta = self._campione(lunghezze, piazzamenti, copre, colpite, aloni)
            if flotta is None:
                continue
            accettati += 1
            for nave in flotta:
                for cella in nave:
                    if cella in voti:
                        voti[cella] += 1
        self.ultimi_campioni = accettati
        self.ultimo_tempo = time.perf_counter() - inizio
        if accettati < 30 or max(voti.values()) == 0:
            return self._ripiego(ignote, colpite)
        candidate = voti
        if not colpite:
            # In caccia si spara solo sulle caselle della classe di parita'
            # della nave piu' corta: una nave lunga L ne tocca sempre una
            # ogni L, quindi le altre non servono a trovarla e si visitano
            # dopo. La classe e' sorteggiata a inizio partita e vale per
            # tutta la partita, perche' cambiarla a meta' sprecherebbe la
            # copertura gia' fatta.
            periodo = min(lunghezze)
            classe = {cella: v for cella, v in voti.items() if (cella[0] + cella[1]) % periodo == self.parita % periodo}
            if classe and max(classe.values()) > 0:
                candidate = classe
        massimo = max(candidate.values())
        migliori = [cella for cella, v in candidate.items() if v == massimo]
        return random.choice(migliori)

    def _piazzamenti(self, size, lunghezze, consentite):
        """Per ogni lunghezza, tutti i modi di posare una nave sulle caselle consentite."""
        risultato = {}
        for lunghezza in set(lunghezze):
            lista = []
            for r in range(size):
                for c in range(size):
                    if c + lunghezza <= size:
                        nave = tuple((r, c + i) for i in range(lunghezza))
                        if all(cella in consentite for cella in nave):
                            lista.append(nave)
                    if lunghezza > 1 and r + lunghezza <= size:
                        nave = tuple((r + i, c) for i in range(lunghezza))
                        if all(cella in consentite for cella in nave):
                            lista.append(nave)
            risultato[lunghezza] = lista
        return risultato

    @staticmethod
    def _coperture(piazzamenti, colpite):
        """Per ogni lunghezza e ogni casella colpita, i piazzamenti che la coprono."""
        copre = {}
        for lunghezza, lista in piazzamenti.items():
            per_cella = {}
            for nave in lista:
                for cella in nave:
                    if cella in colpite:
                        per_cella.setdefault(cella, []).append(nave)
            copre[lunghezza] = per_cella
        return copre

    @staticmethod
    def _alone(cella, size):
        """La casella e le sue vicine, anche in diagonale: dove un'altra nave non puo' stare."""
        r, c = cella
        return frozenset((r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if 0 <= r + dr < size and 0 <= c + dc < size)

    def _campione(self, lunghezze, piazzamenti, copre, colpite, aloni):
        """Una flotta completa compatibile con cio' che si sa, oppure None se il tentativo fallisce.

        Prima si coprono le caselle colpite, scegliendo a caso fra tutte le
        coppie nave e piazzamento che ne coprono una, poi si posano a caso le
        navi rimaste. Un tentativo fallisce quando una casella colpita non e'
        piu' raggiungibile o una nave non trova posto: succede, ed e' normale,
        e il chiamante semplicemente riprova.
        """
        rimaste = list(lunghezze)
        random.shuffle(rimaste)
        bloccate = set()
        scoperte = set(colpite)
        flotta = []
        while scoperte:
            if not rimaste:
                return None
            cella = random.choice(tuple(scoperte))
            candidati = []
            viste = set()
            for lunghezza in rimaste:
                if lunghezza in viste:
                    continue
                viste.add(lunghezza)
                for nave in copre[lunghezza].get(cella, ()):
                    if bloccate.isdisjoint(nave):
                        candidati.append((lunghezza, nave))
            if not candidati:
                return None
            lunghezza, nave = random.choice(candidati)
            rimaste.remove(lunghezza)
            flotta.append(nave)
            for c in nave:
                bloccate |= aloni[c]
            scoperte.difference_update(nave)
        for lunghezza in rimaste:
            nave = self._piazzamento_libero(piazzamenti[lunghezza], bloccate)
            if nave is None:
                return None
            flotta.append(nave)
            for c in nave:
                bloccate |= aloni[c]
        return flotta

    @staticmethod
    def _piazzamento_libero(lista, bloccate):
        """Un piazzamento a caso che non tocchi le navi gia' posate.

        Finche' la griglia e' aperta bastano pochi tentativi ciechi; quando
        si e' riempita si filtra la lista intera, che costa di piu' ma non
        sbaglia.
        """
        quanti = len(lista)
        if not quanti:
            return None
        for _ in range(40):
            nave = lista[random.randrange(quanti)]
            if bloccate.isdisjoint(nave):
                return nave
        liberi = [nave for nave in lista if bloccate.isdisjoint(nave)]
        return random.choice(liberi) if liberi else None

    @staticmethod
    def _ripiego(ignote, colpite):
        """Quando il campionamento non basta: accanto a un colpo a segno, o a caso."""
        vicine = [(r + dr, c + dc) for r, c in colpite for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)) if (r + dr, c + dc) in ignote]
        if vicine:
            return random.choice(vicine)
        return random.choice(sorted(ignote))

    # Difesa.

    def scegli_disposizione(self, candidate, size, lunghezze):
        """Fra piu' disposizioni della flotta, una delle piu' difficili da trovare.

        Ogni candidata e' una lista di navi, ciascuna una sequenza di caselle.
        Il punteggio di una disposizione e' la somma, sulle caselle occupate,
        di quanti piazzamenti possibili passano da li' su una griglia vuota:
        bordi e angoli valgono poco, il centro molto. Si estrae a caso fra il
        terzo migliore, cosi' l'avversario non finisce sempre negli stessi
        angoli.
        """
        if not candidate:
            return None
        densita = self._densita_vuota(size, tuple(sorted(lunghezze)))

        def punteggio(flotta):
            return sum(densita[cella] for nave in flotta for cella in nave)

        ordinate = sorted(candidate, key=punteggio)
        rosa = ordinate[: max(1, len(ordinate) // 3)]
        return random.choice(rosa)

    def _densita_vuota(self, size, lunghezze):
        """Quanti piazzamenti passano da ogni casella su una griglia vuota, per questa flotta."""
        chiave = (size, lunghezze)
        if chiave not in self._cache_densita:
            tutte = {(r, c) for r in range(size) for c in range(size)}
            densita = dict.fromkeys(tutte, 0)
            for lista in self._piazzamenti(size, lunghezze, tutte).values():
                for nave in lista:
                    for cella in nave:
                        densita[cella] += 1
            self._cache_densita[chiave] = densita
        return self._cache_densita[chiave]
