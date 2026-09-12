# Changelog, batnav

Tutti i cambiamenti e le novità introdotte nelle versioni di batnav.
Il changelog nasce con la versione 3.0.0. Per le versioni precedenti il resoconto sta nella cronologia dei commit e nelle release pubblicate su GitHub.

## [3.0.1] - 2026-09-12

I percorsi dei file passano da GBUtils, che dalla V138 li offre a tutti con cartella_applicazione e percorso_risorsa: la logica che dice dove stanno i dati e le risorse era riscritta in dieci progetti, e adesso e' scritta in un posto solo. Il comportamento non cambia, tranne che una risorsa che nel pacchetto non c'e' viene ora cercata anche accanto all'eseguibile.

## [3.0.0] - 2026-09-08

Pubblicata su GitHub il 2026-09-08 come release `v3.0.0`, con il solo archivio `batnav.zip` in allegato. Verificato che l'auto updater la riconosca e ne riceva le note. Issue 1 chiusa.

Revisione 1 del refactoring generale, più il motore nuovo dell'avversario e i suoni rifatti.

### Aggiunto

- **Motore nuovo dell'avversario**, nel modulo `batnav_ia.py`. Prima di ogni colpo costruisce a caso migliaia di flotte complete compatibili con tutto ciò che sa, e spara dove le flotte passano più spesso, restando in caccia sulla classe di parità della nave più corta. Le navi si condizionano a vicenda: una nave lunga non viene cercata in un buco dove non entrerebbe, e un colpo a segno vincola tutta la flotta. La 2.x valutava ogni nave da sola. Il motore lavora a tempo: al massimo un terzo di secondo per colpo, di norma molto meno. Misurato su centinaia di partite simulate contro la 2.4.1 sulla stessa disposizione: in attacco i due sono alla pari sulle flotte disposte a caso, e il nuovo è circa un colpo più efficiente contro le flotte disposte in difesa.
- **Difesa**: l'avversario dispone la propria flotta scegliendo, fra ventiquattro disposizioni casuali, una di quelle più difficili da trovare, con le navi verso i bordi e gli angoli. Contro un cacciatore a densità come la 2.4.1 una flotta così disposta costa in media tre colpi in più su una griglia da 8 e due su una da 10: è il guadagno più grande della versione. Lo stesso vale per la tua flotta quando la fai disporre al programma.
- **Menu principale** con `menu` di GBUtils: nuova partita, classifica, manuale, ascolta i suoni, esci. Prima il gioco partiva direttamente con la domanda del nome.
- **Manuale** in `README.md`, leggibile dal menu una pagina alla volta con `manuale` di GBUtils. Spiega comandi, simboli delle griglie e sigle del prompt, che finora non erano scritte da nessuna parte.
- **Controllo automatico degli aggiornamenti** all'avvio, affidato a `gestisci_aggiornamento` di GBUtils, come negli altri progetti del parco.
- **Ascolta i suoni del gioco**: la voce del menu li riproduce uno per volta, dicendo a cosa serve ciascuno.
- **Statistiche di fine partita**: turni giocati e, per ciascuno dei due, colpi sparati, colpi a segno e precisione.
- Il risultato dice **in che posizione della classifica** è entrato.
- Le domande passano da `dgt` e `enter_escape` di GBUtils invece che da `input` con i controlli riscritti a mano.
- File di contorno finora assenti: `CHANGELOG.md`, `README.md`, `requirements.txt` e `ruff.toml`.

### Cambiato

- **Suoni rifatti**, tutti dalla collezione condivisa: il tuo colpo parte con un passaggio veloce, quello avversario arriva con un volo radente, il colpo in acqua è uno sbuffo, la nave colpita un colpo secco di rumore marrone, l'affondamento un jingle, che sale quando affondi tu e scende quando affondano te; vittoria e sconfitta hanno una fanfara e una missione fallita; coordinata sbagliata e casella già colpita hanno due suoni distinti. Prima ogni colpo era preceduto da un missile di quasi tre secondi, in attesa.
- Fra l'esito del tuo colpo e la risposta dell'avversario c'è un secondo di respiro, altrimenti i due suoni si accavallavano e non si capiva chi avesse sparato.
- La tabella dei suoni sta in un unico dizionario in testa al programma, con l'esito del colpo espresso da una costante e non più dal confronto di tre frasi ripetute in tre punti.
- **La classifica si legge in frasi**, una per voce, invece che in una tabella a colonne fra due righe di trattini.
- L'ordine della classifica tiene conto anche della precisione, a parità di colpi, e poi della data. Le date si salvano in formato anno-mese-giorno; quelle vecchie vengono convertite alla lettura.
- Una **casella già colpita non costa più il turno**: il gioco lo dice e ripete la domanda.
- Quando l'avversario comincia, le griglie compaiono **dopo** il suo primo colpo, non prima.
- Via le emoji dai messaggi di fine partita, che lo screen reader leggeva per nome.
- Versione, data di rilascio e autori stanno in tre costanti separate. La riga di avvio dice versione e data, poi gli autori.
- Le griglie in caratteri restano come sono: sono leggibili sul display braille, con le lettere delle colonne allineate alle caselle.

### Corretto

- **I colpi si contano davvero.** Fino alla 2.4.1 colpi e precisione si ricavavano contando le caselle marcate sulla griglia, comprese quelle segnate d'ufficio attorno alle navi affondate: una partita perfetta su 8 per 8 risultava di cinquanta colpi al ventidue per cento invece che undici al cento. Ora ogni colpo sparato viene contato nel momento in cui parte. La classifica è ripartita da vuota, perché i risultati vecchi non erano confrontabili con quelli nuovi; gli avversari che vincono continuano a entrarci con il loro nome, per scelta di Gabriele.
- **La classifica sta accanto al programma**, non nella directory di lavoro: avviando il gioco da un'altra cartella non ne nasce più una seconda.
- **Salvataggio sicuro**: si scrive su un file temporaneo e si sostituisce solo a scrittura riuscita, la versione precedente resta in `batnav_charts.json.bak`, e un salvataggio fallito viene detto invece di chiudere il gioco con una traccia di errore.
- Alla lettura le voci incomplete vengono scartate dicendo quante sono; un file rotto fa usare la copia di sicurezza, e se manca anche quella si riparte da vuota mettendo da parte il file con estensione `.rotto`.
- Il file della classifica si apre sempre in utf-8.
- La disposizione casuale delle navi ha un numero massimo di tentativi e ricomincia da capo dicendolo, invece di poter girare per sempre.
- Refuso nell'intestazione della classifica.
- Il file `batnav.spec` è escluso dall'esclusione dei `.spec` in `.gitignore`: contiene la ricetta che porta i suoni dentro l'eseguibile.
- Il codice passa `ruff` senza rilievi.
