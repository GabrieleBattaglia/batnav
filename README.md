# batnav

Battaglia navale accessibile contro l'intelligenza artificiale. Si gioca in console, ed e' pensata per lo screen reader e per il display braille: le griglie sono in caratteri, con le lettere delle colonne allineate alle caselle, e tutto il resto si legge in modo lineare.

Versione 3.0.0 del 8 settembre 2026.
Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).

## Il menu

All'avvio il gioco controlla se esiste una versione nuova, poi presenta il menu principale: nuova partita, classifica, manuale, ascolta i suoni del gioco, esci. Si sceglie digitando le prime lettere della voce e confermando con invio; escape torna indietro o esce.

## La partita

Si comincia con il proprio nome e con il lato della griglia, da 8 a 26 caselle; invio da solo accetta 10. La flotta dipende dal lato:

- fino a 9: quattro navi, da 4, 3, 2 e 2 caselle;
- fino a 12: cinque navi, da 5, 4, 3, 3 e 2;
- fino a 16: sei navi, da 6, 5, 4, 3, 3 e 2;
- fino a 20: sette navi, da 7, 6, 5, 4, 4, 3 e 2;
- oltre: otto navi, da 8, 7, 6, 5, 4, 4, 3 e 3.

Le navi non si toccano mai, nemmeno in diagonale: fra una nave e l'altra resta sempre almeno una casella d'acqua. Ne discende una regola comoda: quando una nave affonda, tutte le caselle attorno vengono segnate come acqua, perche' li' non puo' esserci nient'altro. Quelle caselle non contano come colpi sparati.

### Disporre le navi

Il gioco chiede se vuoi disporre le navi tu. Con invio le disponi a mano, con escape le dispone il programma, che sceglie una disposizione difficile da trovare.

A mano, per ogni nave si scrive la casella di partenza, come A1, e poi l'orientamento: v per verticale, o per orizzontale. In verticale la nave si estende dalla casella scelta verso i numeri piu' bassi, in orizzontale verso le lettere successive. Se la nave uscirebbe dalla griglia o toccherebbe un'altra nave, il gioco lo dice e ripete la domanda. Scrivendo ia al posto della casella, le navi rimaste le dispone il programma; scrivendo q si torna al menu.

### Le griglie

Dopo ogni turno compaiono due griglie affiancate: a sinistra la griglia bersaglio, cioe' cio' che sai della flotta avversaria, a destra la tua flotta. I numeri delle righe stanno a sinistra, con la riga 1 in basso, e le lettere delle colonne sotto la griglia, allineate alle caselle.

Nella griglia bersaglio: il punto e' una casella su cui non hai ancora sparato, o che indica acqua, la o e' un colpo andato in acqua, la X e' una nave colpita e la A e' una nave affondata.

Nella tua flotta: la S e' una tua nave intatta, la c e' una casella di nave colpita, la F e' una nave affondata, la o e' un colpo avversario finito in acqua e il punto e' acqua su cui l'avversario non ha ancora sparato.

### Il prompt del turno

La riga che chiede il colpo e' compatta, per stare dentro le quaranta celle del display braille. Per esempio:

    T:3 N:4/4 A:3/4 p%:33.3/25.0>

T e' il numero del turno. N sono le tue navi ancora in acqua sul totale, A quelle dell'avversario. p% sono le due precisioni, prima la tua e poi quella dell'avversario: i colpi andati a segno sui colpi sparati, in percentuale.

Al prompt si scrive la casella, come B7. Le lettere si possono scrivere anche minuscole. Una casella su cui hai gia' sparato non costa il turno: il gioco lo dice e ripete la domanda. Con Q si abbandona la partita, dopo una conferma.

Ogni colpo viene annunciato con l'alfabeto fonetico, per esempio Bravo 7, seguito dall'esito: mancato, colpito, oppure colpito e affondato.

### Fine della partita

Vince chi affonda per primo tutta la flotta avversaria. Il gioco dice poi quanti turni e' durata la partita e, per ciascuno dei due, quanti colpi ha sparato, quanti sono andati a segno e con quale precisione.

## L'avversario

L'avversario ha un nome inventato ogni volta, come IA-Fofofo, e dalla versione 3.0.0 ha un motore nuovo.

Prima di ogni colpo costruisce a caso migliaia di flotte complete compatibili con tutto cio' che sa: le navi non escono dalla griglia, non passano sulle caselle gia' colpite in acqua ne' su quelle delle navi affondate, non si toccano fra loro, e ogni casella colpita ma non ancora affondata e' coperta da una nave. Poi spara sulla casella che, fra tutte quelle flotte, e' occupata piu' spesso. Le navi si condizionano a vicenda, quindi una nave lunga non viene cercata in un buco dove non entrerebbe, e un colpo a segno vincola tutta la flotta e non solo la nave che lo ha ricevuto. Finche' non ha colpi da inseguire, caccia soltanto sulle caselle di una classe di parita' scelta a inizio partita: una nave lunga L ne tocca sempre una ogni L, quindi le altre non servono a trovarla.

Il motore lavora a tempo: al massimo un terzo di secondo per colpo, anche sulle griglie grandi, e di norma molto meno.

Anche in difesa l'avversario ragiona: fra molte disposizioni casuali della propria flotta preferisce quelle piu' difficili da trovare, con le navi verso i bordi e gli angoli, scegliendo a caso fra le migliori per non essere prevedibile. La stessa scelta viene fatta per la tua flotta quando lasci disporre le navi al programma.

## La classifica

Per ogni lato di griglia il gioco conserva le quindici partite migliori. Entra chi vince, con il numero di colpi sparati e la precisione: meno colpi valgono di piu'; a parita', vale la precisione piu' alta, poi il risultato piu' vecchio. Quando vince l'avversario, entra lui con il suo nome.

La classifica si legge dal menu, una frase per voce, e si salva in batnav_charts.json accanto al programma, con una copia di sicurezza in batnav_charts.json.bak. Se il file principale non si legge, il gioco usa la copia; se nemmeno quella, riparte da vuota e lo dice, lasciando il file rotto con l'estensione .rotto.

La classifica e' ripartita da vuota con la versione 3.0.0: i risultati precedenti contavano fra i colpi anche le caselle segnate d'ufficio attorno alle navi affondate, e non erano confrontabili con quelli nuovi.

## I suoni

Ogni evento della partita ha un suono: la partenza del gioco, una nave posata, il tuo colpo che parte, il colpo avversario che arriva, il colpo in acqua, la nave colpita, la nave affondata con un jingle che sale se l'hai affondata tu e scende se l'hanno affondata a te, la coordinata sbagliata, la casella gia' colpita, la vittoria, la sconfitta, la classifica e il salvataggio. Fra l'esito del tuo colpo e la risposta dell'avversario passa un secondo di pausa. La voce del menu che li fa ascoltare li riproduce uno alla volta, dicendo a cosa servono.

I suoni vengono dalla collezione condivisa di GBUtils, Acu_Collection.json, e nell'eseguibile compilato viaggiano dentro il programma.

## Installazione da sorgente

Serve Python 3.12 o successivo. Le dipendenze si installano con:

    pip install -r requirements.txt

Manca pero' una dipendenza che pip non puo' scaricare, perche' non sta su PyPI: e' GBUtils, la libreria condivisa del parco software di IZ4APU. Va clonata a parte:

    git clone https://github.com/GabrieleBattaglia/GBUtils.git

poi si mette la sua cartella in PYTHONPATH, oppure si copiano GBUtils.py e Acu_Collection.json accanto a batnav.py. Senza Acu_Collection.json il gioco funziona ma resta muto.

## File accanto al programma

batnav_charts.json e' la classifica, batnav_charts.json.bak la sua copia di sicurezza. auto_updater_error.log compare solo se il controllo degli aggiornamenti incontra un errore.

L'eseguibile non e' firmato: al primo avvio Windows puo' mostrare l'avviso di SmartScreen, ed e' normale.
