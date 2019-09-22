# shadowBanBot
Bot di telegram che gestisce in automatico gli utenti inattivi dei gruppi	Bot di telegram che gestisce in automatico gli utenti inattivi dei gruppi

# Setup:

Questa sezione descrive i passaggi necessari per far funzionare il bot sul vostro server.

## Requisiti:

1. PostgreSQL Server
2. Python 3.6+
3. Un Bot di telegram (Usa [@BotFather](https://t.me/botfather))
4. Un account telegram
5. Una applicazione telegram (https://my.telegram.org/apps)
6. Un server per hostare il bot, consiglio (https://www.heroku.com/)

## BotFather:

Vai su telegram e apri [@BotFather](https://t.me/botfather)

1. /new e segui tutti i passaggi per creare il bot
2. Una volta creato ti verrà fornito un token che dovrai inserire in tokenbot.py

## Installazione:

1. Crea un database PostgresSQL
2. Inserisci i dati necessari in "tokenbot.py"
3. In questo database fai partire lo script "creazione_tabelle.py"
4. Hosta il bot 
