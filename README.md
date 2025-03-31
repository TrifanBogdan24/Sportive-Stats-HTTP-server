# Sportiv Stats - HTTP web server

> Tema 1 ASC - Trifan Bogdan-Cristian, 331CD

> Link repository: <https://github.com/TrifanBogdan24/Sportive-Stats-HTTP-server.git> 

> Am implementat întreg enunțul temei, inclusiv logging și unit testing.

În cadrul acestei teme, am implementat back-end-ul unui server HTTP
capabil să proceseze simultan mai multe request-uri în același timp,
datorită faptului că am folosit design pattern-ul **Replicated Workers** (numit și **Thread Pool**)

## RESTful API

Metode pentru **procesarea datelor**:

| Metoda HTTP | URI | JSON payload |
| :--- | :--- | :--- |
| `POST` | `http://127.0.0.1:5000//api/states_mean` | `{"question": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/state_mean` | `{"question": "...", "state": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/best5` | `{"question": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/worst5` | `{"question": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/global_mean` | `{"question": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/diff_from_mean` | `{"question": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/state_diff_from_mean` | `{"question": "...", "state": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/mean_by_category` | `{"question": "..."}` |
| `POST` | `http://127.0.0.1:5000//api/state_mean_by_category` | `{"question": "...", "state": "..."}` |

Metode pentru **controlul serverului/server info**:

| Metoda HTTP | URI |
| :--- | :--- |
| `GET` | `http://127.0.0.1:5000//api/graceful_shutdown` |
| `GET` | `http://127.0.0.1:5000//api/num_jobs` |
| `GET` | `http://127.0.0.1:5000//api/jobs` |
| `GET` | `http://127.0.0.1:5000//api/get_results/<job_id>` |

> `<job_id>` este un *placeholder*: în locul său se va trece un număr întreg

## 📬 Postman/🦊 Restfox

Un lucru cu adevărat interesant pe care l-am învățat în această temă
a fost cum să-mi testez **API**-ul construit
(o situație reală la un posibil viitor loc de muncă 🤓).

Am folosit **Restfox** (alternativa lightweight a lui **Postman**)
pentru a analiza răspunsurile serverului, comportamentul bazei de date și logurile.

Dacă nu aș fi rulat request-urile mai întâi secvențial din **Restfox**,
nu aș fi descoperit **dead-lock**-uri sau gestionarea greșită a `mutex`-urilor pe fișiere,
probleme care mi-au limitat procesarea datelor la un singur request pe secundă.

## 📋 Data Ingestor: CSV processing

La pornirea server-ului se citește fișierul **CSV**
și se încarcă în memorie doar coloanele de interes,
în funcție de care se va realiza selecția ulterioară a datelor.

Instanța clasei `DataIngestor` furnizează metode care,
filtrând liniile tabelului în funcție de **question** și **state**,
afectuează diverse **operații statistice** asupra acestora
(e.g.: medie, deviație de la medie, cele mai bune/slabe intrări)
și întoarce un JSON sub forma unui dicționar.

Tratarea cererilor HTTP pentru procesări de date presupune apelarea acestor metode.

## 🧵 Thread Pool

În programarea paralelă, modelul **Replicated Workers** (sau **Thread Pool**)
este folosit pentru obținerea de concurență în execuția unui program:
în cazul de față, procesarea mai multor request-uri HTTP în același timp de către un server web.

Acest **desgin pattern** presupune implementarea a două componenta principale:
1. Un **pool** de task-uri de executat, reprezentat de o **coadă**
    - > Structura `Queue()` din Python oferă, by default, operații **thread-safe**
2. Un grup de **workeri** (**thread**-uri)

Numărul de thread-uri create va fi extras dintr-o variabilă de mediu,
în absența căreia se vor inițializa atâtea thread-uri câte core-uri are procesorul.

```py
num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count()))
```



**Thread Pool**-ul se ocupă cu gestiunea în **paralel** a request-urilor de procesare de date,
apelând metodele corespunzătoare din clasa `DataIngestor`
(celelalte cereri la server fiind executate **secvențial**).

## ⏻  Oprirea Thread Pool-ului

Pentru tratarea request-ului `GET /api/graceful_shutdown`,
am definit un `Event()` la nivelul instantei clasei `ThreadPool`,
care este activat la primirea acestei cereri HTTP,
declanșând astfel oprirea thread-urilor după ce toate request-urile de procesare de date au fost rezolvate.

Thread-urile rulează într-o buclă infinită atâta timp cât:
- coada mai conține task-uri de procesat
- sau `Event()`-ul nu este activat

## 🔒 Concurrent Hash Map și accesul la fișierele cu rezultate

Pentru a proteja accesul la fișierele bazei de date în contextul programării paralele,
mi-am implementat propriul **Concurrent Hash Map** (sub forma unui `dictionar` și unui `Lock()` privat)
pentru a stoca, într-un mod dinamic, mutex-uri doar pentru task-urile în curs de procesare.

> Accesul la fișier necesită obținerea a două lock-uri: unul pentru **Concurrent Hash Map** și unul pentru fișier.

Fiecare mutex este activ doar în timpul procesării datelor și se dezalocă imediat după scrierea rezultatului pe disc.
Folosirea acestui concept de **lifetime** (inspirat din Rust),
impune ca numărul de mutex-uri pentru fișierele bazei de date
să fie cel mult egal cu numărul de thread-uri, economisind astfel memorie.
 
**Thread Pool**-ul stochează joburile în procesare drept chei în **Concurrent Hash Map**,
iar lock-urile pentru fișierele respective sunt valorile din dicționar.

## 🪵 Logging server's activity

Pentru a păstra un istoric **persistent la restart** al serverului,
am înregistrat activitatea în fișiere `webserver.log`, stocate pe disc.

> ⚠️ **ATENȚIE!** Pornirea serverului presupune resetarea activității de logging,
> ceea ce înseamnă că **fișierele** de monitorizare **vor fi șterse**.

Datorită faptului că mai multe thread-uri ar vrea să scrie simultan activitatea serverului,
am definit un **lock** privat, la **nivelul clasei** `Logger`,
pentru a proteja accesul la fișier.

Metoda `log_message()` a instantei clasei `Logger()` primește un mesaj,
pe care îl scrie alături de timestamp-ul curent,
în format 🕚 **GMT** (Greenwich Mean Time), un standard global, fix și independent de fusurile orare.

### 🗂️ Rotating file handler

În loc să scriu toată activitatea de **logging** într-un singur fișier mare,
folosesc `RotatingFileHandler` pentru a impune o limită superioară.
Când `webserver.log` ajunge la dimensiunea de **10MB**, 
acesta se va redenumi în `webserer.log.1`, `.2` până la `.10`.

```py
log_handler = RotatingFileHandler(
    "webserver.log",
    maxBytes=1010241024, backupCount=10
)
```


## ✅ Unit Testing

Pentru verificarea metodelor clasei `DataIngestor`,
mi-am creat 2 CSV-uri cu câte 10 intrări:
1. Primul pentru querry-urile doar în funcție de *"question"*
2. Al doilea fișier pentru procesările care iau și *"state"*-ul în considerare

Am încercat să fac clasa de testare cât de **generic** am putut,
astfel încât să testeze metodele în funcție de **toate fișierele input output** din directoarele aferente.
În plus, mi-am definit **o singură funcție (de ordin superior) capabilă să testeze toate metodele de procesare**
(nu câte una pentru fiecate tip de request în parte).
Drept urmare, codul meu este mult mai concis și ușor de urmărit.

### 👨‍💻 Cum se rulează **testele unitare**

Din directorul rădăcină al repo-ului:
```py
$ source venv/bin/activate
$ PYTHONPATH=. python3 unittests/TestWebserver.py
```