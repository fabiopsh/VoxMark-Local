Documento di Design Tecnico: "VoxMark Local"

Versione: 1.0.0
Stato: Draft
Obiettivo: Creare un'applicazione desktop locale per la sintesi vocale (TTS) ad alta fedeltà utilizzando StyleTTS 2, con supporto per input Markdown semantico.

1. Panoramica dell'Architettura

L'applicazione utilizzerà il pattern "Sidecar Architecture".

Frontend (UI): Un'applicazione web scritta in SolidJS che gestisce l'interfaccia utente, l'editor Markdown e il player audio.

Wrapper Desktop: Tauri v2 (o Electron) che ospita il frontend e gestisce il ciclo di vita del processo backend.

Backend (Core): Un server Python (FastAPI) che viene avviato come sottoprocesso (sidecar) dall'applicazione desktop. Questo server carica il modello StyleTTS 2 e riceve le richieste di inferenza.

Diagramma di Flusso

[Utente] -> [SolidJS UI (Markdown Input)]
    |
    v (Parsing Semantico)
[Pre-processor JSON/Phoneme]
    |
    v (Richiesta HTTP/WebSocket localhost)
[Python Backend (FastAPI)]
    | -> [StyleTTS 2 Model Inference]
    | -> [Post-Processing Audio (WAV)]
    v
[Audio Stream al Frontend] -> [Playback]


2. Stack Tecnologico

Frontend & Wrapper

Framework UI: SolidJS (per le prestazioni reattive granulari).

Styling: Tailwind CSS.

Wrapper: Tauri 2.0 (Preferito per leggerezza e integrazione Rust) oppure Electron.

Nota: Tauri permette di definire "sidecar" (binari esterni) nel file tauri.conf.json, ideale per lanciare l'eseguibile Python.

Backend (The Brain)

Linguaggio: Python 3.10+.

API Framework: FastAPI (Uvicorn server).

ML Engine: PyTorch + StyleTTS 2 Libs.

Dipendenze Critiche: espeak-ng (spesso richiesto per la fonetizzazione), scipy, numpy.

Packaging: PyInstaller o Nuitka per compilare il backend Python in un singolo file .exe da includere nel bundle dell'app.

3. Strategia di Parsing Markdown (Semantic-to-Speech)

Il punto di forza dell'app è trasformare la formattazione visiva in "intenzione vocale". StyleTTS 2 permette di manipolare vettori di stile (Style Vectors) o prosodia.

Dato che StyleTTS 2 non accetta nativamente "grassetto", dobbiamo creare un Middleware di Parsing.

Mappa di Conversione (Markdown -> Prosodia)

Elemento Markdown

Intenzione Vocale

Implementazione Tecnica (Backend)

**Grassetto**

Enfasi / Importanza

Aumento volume (+2dB) + Rallentamento velocità (0.9x)

*Corsivo*

Sussurro / Pensiero

Riduzione energia/pitch o switch a Style Vector "Soft"

# Titolo 1

Annuncio / Cambio Argomento

Pausa lunga pre-frase (1.5s) + Pitch più profondo

> Citazione

Voce narrante distinta

Switch leggero del timbro (se supportato multispeaker)

--- (HR)

Pausa Scenica

Inserimento di 2 secondi di silenzio

... (Ellissi)

Esitazione

Inserimento token pausa breve

Algoritmo di Pre-Processing

Il backend non riceve il raw markdown, ma una lista segmentata di oggetti.

Esempio Payload JSON dal Frontend:

{
  "segments": [
    { "text": "Benvenuti nel capitolo uno.", "style": "heading_1" },
    { "text": "Questa è una frase normale, ma...", "style": "default" },
    { "text": "questa parte è cruciale.", "style": "emphasis", "speed": 0.9 }
  ]
}


4. Implementazione Backend (Python)

Il backend esporrà due endpoint principali:

GET /status: Per verificare se il modello è caricato in VRAM/RAM.

POST /synthesize: Riceve il JSON segmentato e restituisce l'audio.

Gestione del Modello (Loading Strategy)

Per evitare che l'app pesi 4GB all'avvio, il modello verrà caricato in modalità "Lazy Loading" (solo quando l'utente preme "Play" o "Prepara Voce").

5. Build e Distribuzione (.exe)

La sfida maggiore è distribuire Python e PyTorch senza richiedere all'utente di installarli.

Ambiente Python Portatile: Usare un ambiente virtuale isolato.

Compilazione: Usare PyInstaller con il flag --onedir (più veloce all'avvio rispetto a --onefile) per creare una cartella /_internal contenente le dipendenze.

Integrazione Tauri:

Configurare tauri.conf.json per includere la cartella del backend compilato come resources.

Usare l'API Command di Tauri per lanciare l'eseguibile Python all'avvio dell'app UI.

Implementare un listener sulla porta localhost (es. 8000) per attendere che il server sia pronto.

6. Roadmap di Sviluppo

Fase 1 (Core): Script Python che accetta testo e genera WAV con StyleTTS locale.

Fase 2 (API): Avvolgere lo script in FastAPI.

Fase 3 (Frontend): Creare UI SolidJS con textarea e bottone play.

Fase 4 (Parsing): Implementare la logica Markdown -> Segmenti JSON.

Fase 5 (Packaging): Configurare PyInstaller e Tauri per la build finale.