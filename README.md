# Sportiv Stats - HTTP web server

> Tema 1 ASC - Trifan Bogdan-Cristian, 331CD

> Link repository: <https://github.com/TrifanBogdan24/Sportive-Stats-HTTP-server.git> 

> Am implementat intreg enuntul temei, inclusiv logging si unit testing.



In cadrul acestei teme, am implementat back-end-ul unui server HTTP
capabil sa proceseze simultan mai multe reqeust-uri in acelasi timp,
datorita faptului ca am folosit design pattern-ul **Replicated Workers** (numit si **Thread Pool**)


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

> `<job_id>` este un *placeholder*: in locul sau se va trece un numar intreg

## 📬Postman/🦊Restfox

Un lucru cu adevarat interesant pe care l-am invatat la aceasta tema
a fost cum sa-mi testez **API**-ul construit
(o situatie reala la un posibil viitor loc de munca 🤓).

Am folosit **Restfox** (alternativa lightweight a lui **Postman**)
pentru a analiza raspunsurile serverului, comportamentul bazei de date si logurile.


Daca nu as fi rulat request-urile mai intai secvential din **Restfox**,
nu as fi descoperit **dead-lock**-uri cauzate de gestionarea gresita a `mutex`-urilor pe fisiere,
probleme care mi-au limitat procesarea datelor la un singur request pe secunda.




## 📋 Data Ingestor: CSV processing

La pornirea server-ului se citeste fisierul **CSV**
si se incarca in memorie doar coloanele de interes,
in functie de care se va realiza selectia ulterioara a datelor.

Instanta clasei `DataIngestor` furnizeaza metode care,
filtrand liniile tabelului in functie de **question** si **state**,
afectueaza diverse **operatii statistice** asupra acestora
(e.g.: medie, deviatie de la medie, cele mai bune/slabe intrari)
si intoarce un JSON sub forma unui dictionar.

Tratarea cererilor HTTP pentru procesari de date presupune apelarea acestor metode.


## 🧵 Thread Pool

In programarea paralela, modelul **Replicated Workers** (sau **Thread Pool**)
este folosit pentru obtinerea de concurenta in executia unui program:
in cazul de fata, procesarea mai multor request-uri HTTP in acelasi timp de catre un server web.



Acest **desgin pattern** presupune implementarea a doua componenta principale:
1. Un **pool** de task-uri de executat, reprezentat de o **coada**
    - > Structura `Queue()` din Python ofera, by default, operatii **thread-safe**
2. Un grup de **workeri** (**thread**-uri)


Numarul de thread-uri create va fi extras dintr-o variabila de mediu,
in absenta careia se vor initializa atatea thread-uri cate core-uri are procesorul.

```py
num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count()))
```


**Thread Pool**-ul se ocupa cu gestiunea in **paralel** a request-urilor de procesare de date,
apeland metodele corespunzatoare din clasa `DataIngestor`
(celelalte cereri la server fiind executate **secvential**).


## ⏻  Oprirea Thread Pool-ului


Pentru tratarea request-ului `GET /api/graceful_shutdown`,
am definit un `Event()` la nivelul instantei clasei `ThreadPool`,
care este activat la primirea acestei cereri HTTP,
declansand astfel oprirea thread-urilor dupa ce toate request-urile de procesare de date au fost rezolvate.

Thread-urile ruleaza intr-o bucla infinita atata timp cat:
- coada mai contine task-uri de procesat
- sau `Event()`-ul nu este activat




## 🔒 Concurrent Hash Map si accesul la fisierele cu rezultate


Pentru a proteja accesul la fisierele bazei de date in contextul programarii paralele,
mi-am implementat propriul **Concurrent Hash Map** (sub forma unui `dictionar` si unui `Lock()` privat)
pentru a stoca, intr-un mod dinamic, mutex-uri doar pentru task-urile in curs de procesare.

> Accesul la fisier necesita obtinerea a doua lock-uri: unul pentru **Concurrent Hash Map** si unul pentru fisier.

Fiecare mutex este activ doar in timpul procesarii datelor si se dezaloca imediat dupa scrierea rezultatului pe disc.
Folosirea acestui concept de **lifetime** (inspirat din Rust),
impune ca numarul de mutex-uri pentru fisierele bazei de date
sa fie cel mult egal cu numarul de thread-uri, economisind astfel memorie.
 
 
**Thread Pool**-ul stocheaza joburile in procesare drept chei in **Concurrent Hash Map**,
iar lock-urile pentru fisierele respective sunt valorile din dictionar.




## 🪵 Logging server's activity

Pentru a pastra un istoric **persistent la restart** al serverului,
am inregistrat activitatea in fisiere `webserver.log`, stocate pe disc.

> ⚠️ **ATENTIE!** Pornirea serverului presupune resetarea activitatii de logging,
> ceea ce inseamna ca **fisierele** de monitorizare **vor fi sterse**.

Datorita faptului ca mai multe thread-uri ar vrea sa scrie simultan activitatea serverului,
am definit un **lock** privat, la **nivelul clasei** `Logger`,
pentru a proteja accesul la fisier.

Metoda `log_message()` a instantei clasei `Logger()` primeste un mesaj,
pe care il scrie alaturi de timestamp-ul curent,
in format 🕚 **GMT** (Greenwich Mean Time), un standard global, fix si independent de fusurile orare.


### 🗂️ Rotating file handler

In loc sa scriu toata activitatea de **logging** intr-un singur fisier mare,
folosesc `RotatingFileHandler` pentru a impune o limita superioara.
Cand `webserver.log` ajunge la dimensiunea de **10MB**, 
acesta se va redenumi in `webserer.log.1`, `.2` pana la `.10`.

```py
log_handler = RotatingFileHandler(
    "webserver.log",
    maxBytes=10*1024*1024, backupCount=10
)
```


## ✅ Unit Testing

Pentru verificarea metodelor clasei `DataIngestor`,
mi-am creat 2 CSV-uri cu cate 10 intrari:
1. Primul pentru querry-urile doar in functie de *"question"*
2. Al doilea fisier pentru procesarile care iau si *"state"*-ul in considerare


Am incercat sa fac clasa de testare cat de **generic** am putut,
astfel incat sa testeze metodele in functie de **toate fisierele input output** din directoarele aferente.
In plus, mi-am definit **o singura functie capabila sa testeze toate metodele de procesare**
(nu cate una pentru fiecate tip de request in parte).
Drept urmare, codul meu este mult mai concis si usor de urmarit.




### 👨‍💻 Cum se ruleaza **testele unitare**

Din directorul radacina al repo-ului:
```sh
$ source venv/bin/activate
$ PYTHONPATH=. python3 unittests/TestWebserver.py
```

