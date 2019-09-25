from datetime import datetime
from pytz import timezone

def parola_giorno(tempo):
    if tempo == 1:
        return "giorno"
    else:
        return "giorni"

def ora_attuale(fuso_orario):
    return datetime.now().astimezone(timezone(fuso_orario))

def nome_link(id,nome):
    return  "<a href=\'tg://user?id="+str(id)+"\'>"+nome+"</a>"

#print(datetime.now().astimezone(timezone("Europe/Rome")))