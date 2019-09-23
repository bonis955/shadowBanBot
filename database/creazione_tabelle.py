import psycopg2
from tokenbot import DATABASE_URL

connect=psycopg2.connect(DATABASE_URL,sslmode='require')
connect.autocommit=True
c=connect.cursor()

c.execute("""CREATE TABLE utenti(     
      id_gruppo BIGINT,
      id_utente BIGINT,      
      nome Text  ,
      data_ban Text)""")

c.execute("""CREATE TABLE gruppi(     
      id_gruppo BIGINT PRIMARY KEY ,
      data_massima_settata Text,
      punizione Text,
      lingua Text,
      fuso_orario Text
      )""")


