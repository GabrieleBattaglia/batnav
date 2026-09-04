# batnav, utilita': prepara l'archivio per la distribuzione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Opus 5, modalita' auto).
# 04/09/2026: primo chiamante, il mestiere sta in crea_archivio_release di GBUtils V104.

"""Comprime il risultato di PyInstaller in un solo archivio.

Tutto il mestiere sta in GBUtils, cosi' la regola sulle esclusioni e' una
sola per tutti i progetti. Qui resta soltanto il nome di batnav.

batnav si compila in un file unico, quindi dentro dist c'e' soltanto
l'eseguibile: la collezione dei suoni, dichiarata nei datas dello spec,
viaggia dentro di lui e non va cercata accanto. Prima di comprimere,
svuota dist da quello che ha prodotto la prova dell'eseguibile.

Si lascia fuori l'archivio delle partite, che nasce giocando la prima
volta accanto all'eseguibile e conterrebbe le tue.
"""

import sys

from GBUtils import crea_archivio_release

FUORI = ["batnav_charts.json"]


def main():
    try:
        crea_archivio_release("batnav", cartella_dist="dist", escludi=FUORI)
    except (FileNotFoundError, OSError) as e:
        print(f"Archivio non creato: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
