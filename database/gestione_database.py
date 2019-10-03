from datetime import datetime
from utente import Utente
from gruppo import Gruppo
import copy

class Gestione_database():

    def __init__(self,connect):
        self.connect=connect
        self.gestore_database=connect.cursor()

    #gestione gruppi
    def ritorna_lista_gruppi(self):
        lista_gruppi=[]
        with self.connect:
            self.gestore_database.execute("SELECT * FROM gruppi")
            gruppi = self.gestore_database.fetchall()
            for gruppo in gruppi:
                self.gestore_database.execute("SELECT * FROM utenti WHERE id_gruppo=%s", [int(gruppo[0])])
                dati2 = self.gestore_database.fetchall()
                lista_gruppi.append([Gruppo(gruppo[0],gruppo[1],gruppo[2]),self.costruisci_lista(dati2)])
        return lista_gruppi

    def costruisci_lista(self,utenti):
        lista_utenti = []
        if utenti is None:
            utenti=list()
        for utente in utenti:
            data = convertitoreStringtoData(copy.copy(utente[3]))
            lista_utenti.append(Utente(utente[0], utente[1], utente[2], data))
        return lista_utenti

    def ritorna_lista_utenti(self,id_gruppo):
        with self.connect:
            self.gestore_database.execute("SELECT * FROM utenti WHERE id_gruppo=%s",[id_gruppo])
            dati=self.gestore_database.fetchall()
            return self.costruisci_lista(dati)

    def trova_gruppo(self,id_gruppo):
        with self.connect:
            self.gestore_database.execute("SELECT * FROM gruppi WHERE id_gruppo=%s",[id_gruppo])
            gruppo=self.gestore_database.fetchone()
            return gruppo

    def aggiungi_gruppo(self, id_gruppo):
        with self.connect:
            self.gestore_database.execute("INSERT INTO gruppi VALUES(%s,%s,%s,%s,%s)", [id_gruppo, 7, "ban","italiano","Europe/Rome"])
            self.connect.commit()

    def aggiorna_lingua(self,lingua,id_gruppo):
        with self.connect:
            self.gestore_database.execute("UPDATE gruppi SET lingua=%s  WHERE id_gruppo=%s",
                                          [lingua,id_gruppo])
            self.connect.commit()

    def aggiorna_fuso_orario(self,fuso_orario,id_gruppo):
        with self.connect:
            self.gestore_database.execute("UPDATE gruppi SET fuso_orario=%s  WHERE id_gruppo=%s",
                                          [fuso_orario,id_gruppo])
            self.connect.commit()

    def aggiorna_gruppo(self, gruppo):
        with self.connect:
            self.gestore_database.execute("UPDATE gruppi SET data_massima_settata=%s, punizione=%s  WHERE id_gruppo=%s",
                                          [gruppo.giorni_ban, gruppo.punizione, gruppo.id_gruppo])
            self.connect.commit()

    def rimuovi_gruppo(self, id_gruppo):
        with self.connect:
            self.gestore_database.execute("DELETE FROM gruppi WHERE id_gruppo=%s",
                                          [id_gruppo])
            self.gestore_database.execute("DELETE FROM utenti WHERE id_gruppo=%s",
                                          [id_gruppo])
            self.connect.commit()
            return True

    #gestione utenti
    def trova_utente(self,id_utente, id_gruppo):
        with self.connect:
            self.gestore_database.execute("SELECT * FROM utenti WHERE id_utente=%s AND id_gruppo=%s",[id_utente, id_gruppo])
            dati=self.gestore_database.fetchone()
            if dati is None:
                return None
            data=convertitoreStringtoData(copy.copy(dati[3]))
            utente=Utente(dati[0],dati[1],dati[2],data)
            return utente

    def aggiungi_membro(self, user):
        with self.connect:
            self.gestore_database.execute("INSERT INTO utenti VALUES(%s,%s,%s,%s)", [user.id_gruppo, user.id_utente, user.nome, user.data_ban.strftime("%x")])
            self.connect.commit()

    def aggiorna_membro(self,utente):
        with self.connect:
            self.gestore_database.execute("UPDATE utenti SET data_ban=%s  WHERE id_gruppo=%s AND id_utente=%s",
                                          [utente.data_ban.strftime("%x"), utente.id_gruppo, utente.id_utente])
            self.connect.commit()

    def rimuovi_utente(self, id_utente, id_gruppo):
        with self.connect:
            self.gestore_database.execute("DELETE FROM utenti WHERE id_utente=%s AND id_gruppo=%s",
                                          [id_utente, id_gruppo])
            self.connect.commit()
            return True

def convertitoreStringtoData(stringa):
    data=stringa.split("/")
    anno=int(data[2])+2000
    return datetime(month=int(data[0]),day=int(data[1]),year=int(anno))