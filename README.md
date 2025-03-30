# Sportiv Stats - HTTP web server

> Tema 1 ASC - Trifan Bogdan-Cristian, 331CD

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


## 📋 Data Ingestor: CSV processing

La pornirea server-ului se citeste fisierul **CSV**
si se incarca in memorie doar coloanele de interes,
in functie de care se va realiza selectia ulterioara a datelor.

<!-- TODO: continua descrierea -->


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
celelalte cereri la server fiind executate **secvential**.


## ⏻  Oprirea Thread Pool-ului


Pentru tratarea request-ului `GET /api/graceful_shutdown`,
am definit un `Event()` la nivelul instantei clasei `ThreadPool`,
care este activat la primirea acestei cereri HTTP,
declansand astfel oprirea thread-urilor dupa ce toate request-urile de procesare de date au fost rezolvate.

Thread-urile ruleaza intr-o bucla infinita atata timp cat:
- coada mai contine task-uri de procesat
- sau `Event()`-ul nu este activat




## 🔒 Concurrent Hash Map si accesul la fisierele cu rezultate

Folosirea unei baze de date pe disc in contextul programarii paralele
presupune folosirea unor primitive de sincronizare care sa protejeze accesul la fisiere.

Totusi, s-ar ocupa inutil RAM-ul daca as creea cate un mutex pentru fiecare job.
Intrucat ultima scriere in fisier este aceea a rezultatului,
pot sa fac urmatoarea **optimizare a memoriei**:
mutex-ul pe fisierul unui job va *exista* doar pe durata procesarii datelor,
iar apoi va fi dezalocat.

Pentru implementarea unei astfel de structuri de date dinamice,
am ales sa folosesc un **Concurrent Hash Map** (dictionar),
care are un lock intern declarat sub forma unui atribut privat
pentru a asigura faptul ca operatiile realizate asupra dictionarului sunt thread-safe.

Thread Pool-ul va stoca ID-urile joburile in procesare drept chei in **Concurrent Hash Map**,
iar `Lock()`-urile pe fieserele aferente job-urilor vor reprezenta valorile dictionarului.

> Deschiderea accesului la fisier presupune obtinerea a doua mutex-uri:
> lock-ul intern al **Concurrent Hash Map**-ului, iar apoi lock-ul aferent fisierului

> Obtinerea accesului la fisier se face pe baza **JOB ID**-ului, astfel.

Pasi:
1. La creerea unui job nou se creeaza un nou mutex si se insereaza `id_job -> Lock()` in **Concurrent Hash Map**
2. Tot la crearea job-ului, se scrie in fisierul rezultat: `{"status": "running"}`
3. Se proceseaza datele, se scrie rezultatul in fisier, iar apoi se sterge intrarea `id_job -> Lock()` din dictionar


Astfel, folosind acest concept de **lifetime** (inspirat din Rust),
impun ca numarul de mutex-uri pentru fisierele bazei de date
sa fie cel mult egal cu numarul de thread-uri.


## 🪵 Logging server's activity

Pentru a pastra un istoric **persistent la restart** al serverului,
am inregistrat activitatea in fisiere `*.log`, stocate pe disc.

> ⚠️ **ATENTIE!** Pornirea serverului presupune resetarea activitatii de logging,
> ceea ce inseamna ca **fisierele** de monitorizare **vor fi sterse**.

Datorita faptului ca mai multe thread-uri ar vrea sa scrie simultan activitatea serverului,
am definit un **lock** privat, la **nivelul clasei** `Logger`,
pentru a proteja accesul la fisier.

Metoda `log_message()` a instantei clasei `Logger()` primeste un mesaj,
pe care il scrie alaturi de timestamp-ul curent,
in format 🕚 **GMT** (Greenwich Mean Time), un standard global, fix si independent de fusurile orare.

Aceasta metoda `log_message()` este apelata:
- La initializarea server-ului: mesajul va contine numarul de thread-uri
- Ori de cate ori un request HTTP este primit de catre server:
    mesajul va contine:
    - Tipul metodei HTTP (`POST`/`GET`)
    - Endpoint-ul accesat
    - Payload-ul JSON (daca request-ul este de tip `POST`)
    - In cazul request-urile de tip `POST`, se va afisa `job_id`-ul
- Cand se primesc request-uri de procesare dupa ce s-a primit `GET /api/graceful_shutdown`:
    mesajul scris va fi unul de eroare
- Cand thread-urile au fost oprite in urma request-ului de `shutdown`
- Cand un rezultat a fost calculat pentru un request de procesare a datelor

<!-- TODO: continua descrierea -->