BEGIN TRANSACTION;
CREATE TABLE ant(id INTEGER PRIMARY KEY AUTOINCREMENT, runId INTEGER, step INTEGER, pos INTEGER);
CREATE TABLE runs(runId INTEGER PRIMARY KEY AUTOINCREMENT, run_date DATETIME);
CREATE TABLE sqlite_sequence(name,seq);
COMMIT;
