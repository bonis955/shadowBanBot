#vers 1.4.1

import asyncio
import threading
import time as t
from datetime import timedelta
from operator import attrgetter

import psycopg2
import schedule
import telepot
from telepot.namedtuple import *
from telethon.sync import TelegramClient

from convertitore import *
from database.gestione_database import Gestione_database
from gruppo import Gruppo
from meassaggi_bot import Messaggio
from tokenbot import *
from utente import Utente


class Shadowbanbot():
    lista_utenti=list()
    database=None
    gruppo=None
    nuovo_tempo=7

    def __init__(self,bot):
        self.bot=bot
        schedule.run_pending()
        thread = threading.Thread(target=self.run_threaded)
        thread.start()
        #schedule.every().second.do(self.controlla_ban)
        schedule.every().days.at(orario_script).do(self.controlla_ban)

    def attiva_database(self):
        connect = psycopg2.connect(DATABASE_URL, sslmode='require')
        connect.autocommit = True
        self.database = Gestione_database(connect)
        self.messaggio = Messaggio(bot, self.database)

    def controllo_problemi(self,msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        try:
            lascia_chat = msg['left_chat_member']['id']
            if lascia_chat == id_bot:
                self.database.rimuovi_gruppo(chat_id)
            else:
                self.database.rimuovi_utente(msg['from']['id'], chat_id)
            return False
        except:
            pass

        try:
            msg['chat']['username']
        except:
            self.messaggio.uscita_bot(chat_id)
            return False

        if chat_type == "channel":
            try:
                self.bot.leaveChat(chat_id)
            except:
                return False
            return False

        if msg['from']['is_bot']:
            return False

        return True



    def run_threaded(self):
        while 1:
            schedule.run_pending()
            t.sleep(1)

    def azzero_variabili(self):
        self.lista_utenti = list()
        self.database=None
        self.gruppo=None
        self.nuovo_tempo=7

    def on_chat_text(self,msg):
        self.azzero_variabili()
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.attiva_database()
        if not self.controllo_problemi(msg):
            return

        informazioni_utente = bot.getChatMember(chat_id, msg['from']['id'])

        if chat_type == 'private':
            if msg['text'] == '/help':
                self.messaggio.help(chat_id)
            else:
                inlineKeyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Aggiungimi in un gruppo',
                                          url='https://t.me/shadowbanbot?startgroup=limpiccatobot')]])
                bot.sendMessage(chat_id,
                                "Ciao a tutti e benvenuti nel shadow ban bot! Funziono solo nei gruppi, se vuoi aggiungermi usa il tasto sottostante\n\n"
                                "Per sapere i comandi del bot usa /help",
                                reply_markup=inlineKeyboard, parse_mode='HTML')

            self.database.rimuovi_gruppo(chat_id)
            return

        self.recupera_gruppo(chat_id, msg['chat']['username'])

        utente = self.database.trova_utente(msg['from']['id'], chat_id)
        if utente is None:
            try:
                if msg['new_chat_partecipant']['is_bot']:
                    return
            except:
                user=self.ritorna_utente(chat_id, msg['from']['id'], msg['from']['first_name'])
                self.database.aggiungi_membro(user)
        else:
            utente.data_ban=self.nuova_data_ban(ora_attuale(self.gruppo.fuso_orario))
            self.database.aggiorna_membro(utente)


        try:
            msg['text']
        except:
            return

        self.lista_utenti = self.database.ritorna_lista_utenti(chat_id)

        if msg['text'].startswith('/start') or msg['text']==('/start@shadowbanbot'):
            self.messaggio.impostazioni(chat_id, "Ciao benvenuto nel shadow ban bot dove potrai gestire in maniera automatica gli utenti inattivi del tuo gruppo\n\n❗❗❗❗❗❗❗❗\n<b>N.B IL BOT DEVE ESSERE AMMINISTRATORE O NON FUNZIONERÀ</b>\n❗❗❗❗❗❗❗❗\n\nvers 1.4.1", self.gruppo, inlinekeyboard=self.messaggio.creaInlinekeyboard())

        elif str(msg['text'].lower()).startswith('/setinattivita'):
            if informazioni_utente['status'] == 'creator' or informazioni_utente['status'] == 'administrator':
                dato=self.messaggio.isVuoto(msg['text'])
                if dato is None:
                    self.messaggio.impostazioni(chat_id, "Non hai segnato nessun tempo\n\n<b>Tieni premuto sulla scritta blu</b> e poi scrivi il tempo\n(es <b>/setinattivita 7</b>)", self.gruppo)
                else:
                    try:
                        self.nuovo_tempo=int(dato)
                    except:
                        self.messaggio.impostazioni(chat_id, "Errore! Devi inserire un numero <b>" + msg['from']['first_name'] + "</b>", self.gruppo)
                        return
                    if self.nuovo_tempo<=0:
                        self.messaggio.impostazioni(chat_id, "Errore! Devi inserire un numero maggiore di zero <b>" + msg['from']['first_name'] + "</b>", self.gruppo)
                        return
                    self.set_time(msg['chat']['username'],False,chat_id)
            else:
                self.messaggio.impostazioni(chat_id,"<b>Solo gli admin del gruppo possono utilizzare questo comando!</b>",self.gruppo,inlinekeyboard=self.messaggio.creaInlinekeyboard())

        elif str(msg['text'].lower()).startswith('/settimezone') or str(msg['text'].lower()).startswith('/settimezone'):
            if informazioni_utente['status'] == 'creator' or informazioni_utente['status'] == 'administrator':
                dato = self.messaggio.isVuoto(msg['text'])
                if dato is None:
                    self.messaggio.impostazioni(chat_id, "Non hai segnato nessun fuso orario<b>\n\nTieni premuto sulla scritta blu</b> e poi inserisci il fuso orario\n(es <b>/settimezone Europe/Rome</b>)", self.gruppo)
                else:
                    try:
                        try:
                            fuso_array=dato.split("/")
                            fuso_orario=fuso_array[0].capitalize()+"/"+fuso_array[1].capitalize()
                        except:
                            fuso_orario=dato.capitalize()
                        ora_attuale(fuso_orario.strip())
                        self.database.aggiorna_fuso_orario(fuso_orario,chat_id)
                        self.messaggio.impostazioni(chat_id,"Il nuovo fuso orario è\n<b>"+fuso_orario+"</b>",self.gruppo,inlinekeyboard=self.messaggio.creaInlinekeyboard())
                    except:
                        self.messaggio.impostazioni(chat_id,"Il fuso orario inserito non è valido, riprova.\n\nLa lista dei Fuso orari la trovi sul seguente sito <a href='https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568'>FUSO ORARI</a>",self.gruppo)

            else:
                self.messaggio.impostazioni(chat_id,
                                                "<b>Solo gli admin del gruppo possono utilizzare questo comando!</b>",
                                                self.gruppo, inlinekeyboard=self.messaggio.creaInlinekeyboard())

        elif str(msg['text'].lower()).startswith('/lista_inattivi'):
            self.messaggio.impostazioni(chat_id, self.lista_inattivi(chat_id),self.gruppo,
                                        inlinekeyboard=self.messaggio.creaInlinekeyboard())

        elif str(msg['text'].lower()).startswith('/status_inattivo'):
            try:
                id_utente_selezionato=msg['reply_to_message']['from']['id']
            except:
                id_utente_selezionato=msg['from']['id']
            utente = self.database.trova_utente(id_utente_selezionato, chat_id)
            if utente is None:
                bot.sendMessage(chat_id, "L'utente selezionato è un <b>admin</b> o un <b>bot</b> e non si può vedere l'inattività",parse_mode='HTML')
            else:
                data_ban = utente.data_ban-timedelta(days=int(self.gruppo.giorni_ban))
                giorni_rimasti = utente.data_ban-data_ban
                messaggio = "\nGiorno previsto del ban se non scrive\n\n<b>" + utente.nome + "</b> (" + utente.data_ban.strftime("%d/%m/%Y") + ")"
                messaggio = messaggio + "\n\n<b>Ultimo messaggio</b>:\n" + data_ban.strftime("%d/%m/%Y")+"\n\n<b>Tempo rimasto</b>: "+str(giorni_rimasti.days)+" "+parola_giorno(giorni_rimasti.days)
                bot.sendMessage(chat_id, messaggio,parse_mode='HTML')

        elif msg['text'].startswith('/help'):
            self.messaggio.help(chat_id)

    def on_call_back_query(self, msg):
        self.azzero_variabili()
        query_id, user_id, query_data = telepot.glance(msg, flavor='callback_query')
        chat_id=msg['message']['chat']['id']
        self.attiva_database()
        try:
            self.recupera_gruppo(chat_id, msg['message']['chat']['username'])
        except:
            self.messaggio.uscita_bot(chat_id)
            return

        messaggio_modificato = telepot.message_identifier(msg['message'])
        informazioni = bot.getChatMember(chat_id, user_id)

        if query_data.lower()=='/settime':
            if informazioni['status']=='creator' or informazioni['status']=='administrator':
                inlineKeyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='1',callback_data=1),
                     InlineKeyboardButton(text='3', callback_data=3),
                     InlineKeyboardButton(text='5', callback_data=5)],[
                     InlineKeyboardButton(text='7', callback_data=7),
                     InlineKeyboardButton(text='10', callback_data=10),
                     InlineKeyboardButton(text='15', callback_data=15),
                     InlineKeyboardButton(text='30', callback_data=30)
                    ]])
                self.messaggio.impostazioni(chat_id, "Scegli il tempo massimo per inattività:",self.gruppo, True, messaggio_modificato,inlineKeyboard)
            else:
                self.messaggio.impostazioni(chat_id, "<b>Solo gli admin del gruppo possono utilizzare questo comando!</b>",self.gruppo, True,
                                            messaggio_modificato,self.messaggio.creaInlinekeyboard())
            return

        elif query_data.lower() == '/setpunizione':
            if informazioni['status'] == 'creator' or informazioni['status'] == 'administrator':
                inlineKeyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='kick', callback_data='kick'),
                     InlineKeyboardButton(text='ban', callback_data='ban')]])
                self.messaggio.impostazioni(chat_id, "Scegli la punizione per inattività",self.gruppo,True,messaggio_modificato,inlineKeyboard)
            else:
                self.messaggio.impostazioni(chat_id,
                                            "<b>Solo gli admin del gruppo possono utilizzare questo comando!</b>",self.gruppo,True,
                                            messaggio_modificato, self.messaggio.creaInlinekeyboard())
            return

        elif query_data.lower() == '/listainattivi':
            self.messaggio.impostazioni(chat_id,self.lista_inattivi(chat_id),self.gruppo,True,messaggio_modificato,self.messaggio.creaInlinekeyboard())

        elif query_data.lower() == 'kick' or query_data.lower() == 'ban':
            self.gruppo.punizione=str(query_data)
            self.database.aggiorna_gruppo(self.gruppo)
            self.messaggio.impostazioni(chat_id,"La punizione per inattività è stata cambiata correttamente ✅",self.gruppo,True,messaggio_modificato,self.messaggio.creaInlinekeyboard())


        elif query_data.lower() == '/chiudi':
            bot.deleteMessage(messaggio_modificato)


        else:
            self.nuovo_tempo=int(query_data)
            self.set_time(msg['message']['chat']['username'],True,chat_id,messaggio_modificato)

    def set_time(self, username, isquery=True, chat_id=0,messaggio_modificato=None):
        lista_utenti = self.ritorna_lista_membri_gruppo(chat_id, username)
        for utente in lista_utenti:
            utente.data_ban=self.nuova_data_ban(utente.data_ban, True)
            self.database.aggiorna_membro(utente)
        self.gruppo.giorni_ban=self.nuovo_tempo
        self.database.aggiorna_gruppo(self.gruppo)
        self.messaggio.impostazioni(chat_id,"Ok la durata è stata modificata correttamente ✅",self.gruppo,isquery,messaggio_modificato, self.messaggio.creaInlinekeyboard())

    def nuova_data_ban(self, ora_ban, aggiorna=False):
        if aggiorna:
            days=self.gruppo.giorni_ban-(self.nuovo_tempo)
            if days==0:
                return ora_ban
            elif days<0:
                days=days*(-1)
                number_days = timedelta(days=days)
                ora_ban = ora_ban + number_days
            else:
                number_days = timedelta(days=days)
                ora_ban = ora_ban - number_days
        else:
            number_days = timedelta(days=int(self.gruppo.giorni_ban))
            ora_ban = ora_ban + number_days
        return ora_ban

    def lista_inattivi(self,chat_id):
        lista_utenti = self.database.ritorna_lista_utenti(chat_id)
        messaggio = "<b>LISTA UTENTI INATTIVI:</b>\n(Giorno ban)\n"
        lista_utenti = sorted(lista_utenti, key=attrgetter("data_ban"))
        for utente in lista_utenti:
            messaggio = messaggio + "\n<b>" + utente.nome + "</b> ("+utente.data_ban.strftime("%d/%m/%Y")+")"

        try:
            fuso_array=self.gruppo.fuso_orario.split("/")
            citta_fuso=fuso_array[1]
        except:
            citta_fuso=self.gruppo.fuso_orario
        messaggio=messaggio+"\n\n<b>Data attuale</b>:\n"+ora_attuale(self.gruppo.fuso_orario).strftime("%d/%m/%Y, %H:%M")+\
                  "\n\n<b>Fuso orario</b>: "+citta_fuso

        return messaggio

    def ritorna_lista_membri_gruppo(self, chat_id, username_gruppo):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = TelegramClient('session', API_ID, API_HASH)
        client.start(bot_token=TOKEN)
        try:
            dati = list(client.get_participants(username_gruppo, aggressive=True))
        except:
            self.bot.sendMessage(chat_id,"C'è stato un problema con il bot si prega di riprovare")
            client.disconnect()
            loop.stop()
            loop.close()
            return []

        lista_gruppo=[]
        for utente in dati:
            if not utente.bot:
                user=self.ritorna_utente(chat_id, utente.id, utente.first_name)
                lista_gruppo.append(user)

        client.disconnect()
        loop.stop()
        loop.close()
        return lista_gruppo

    def ritorna_utente(self, id_gruppo, id_utente, nome):
        ora_ban=self.nuova_data_ban(ora_attuale(self.gruppo.fuso_orario))
        user = Utente(id_gruppo, id_utente, nome, ora_ban)
        return user

    def recupera_gruppo(self,chat_id,username):
        gruppo = self.database.trova_gruppo(chat_id)
        if gruppo is None:
            self.database.aggiungi_gruppo(chat_id)
            self.gruppo = Gruppo(chat_id)
            lista_utenti = self.ritorna_lista_membri_gruppo(chat_id, username)
            for utente in lista_utenti:
                self.database.aggiungi_membro(utente)

        else:
            self.gruppo = Gruppo(chat_id, int(gruppo[1]), gruppo[2],gruppo[3],gruppo[4])

    #script che si lancia ogni giorno alle 23:55
    def controlla_ban(self):
        self.azzero_variabili()
        self.attiva_database()
        lista_gruppi=self.database.ritorna_lista_gruppi()
        for gruppo in lista_gruppi:
            id_gruppo=gruppo[0].id_gruppo
            punizione=gruppo[0].punizione
            messaggio_utenti_avviso = ""
            messaggio_utenti_bannati = ""
            for utente in gruppo[1]:
                data=datetime.now()
                tempo_rimasto=utente.data_ban-datetime(data.year,data.month,data.day)
                codice=utente.istimeban(self.bot,int(tempo_rimasto.days),punizione)
                if codice==0:
                    messaggio_utenti_bannati = messaggio_utenti_bannati + "\n• " + nome_link(utente.id_utente, utente.nome)
                    self.database.rimuovi_utente(utente.id_utente,utente.id_gruppo)
                elif codice==2:
                    bot.sendMessage(utente.id_gruppo,"Mi dispiace ma il bot non è amministratore!\n\nz<b>Metti il bot amministratore del gruppo o non funzionerà</b>",parse_mode='HTML')
                    break
                elif codice==3:
                    bot.sendMessage(utente.id_gruppo,"Mi dispiace ma non è possibile rimuovere <b>"+nome_link(utente.id_utente,utente.nome)+ "</b> un amministratore, dovrai rimuoverlo manualmente",parse_mode='HTML')
                    self.database.rimuovi_utente(utente.id_utente, utente.id_gruppo)
                elif codice==4:
                    messaggio_utenti_avviso=messaggio_utenti_avviso+"\n• "+nome_link(utente.id_utente,utente.nome)

            if messaggio_utenti_avviso!="":
                bot.sendMessage(id_gruppo,"I seguenti utenti hanno ancora \n<b>1 giorno</b> per scrivere ⚠\n"+messaggio_utenti_avviso,parse_mode='HTML')

            if messaggio_utenti_bannati!="":
                if punizione == "kick":
                    messaggio_punizione = "rimossi"
                else:
                    messaggio_punizione = "bannati"
                bot.sendMessage(id_gruppo,"I seguenti utenti sono stati "+messaggio_punizione+" per inattività 👋\n" + messaggio_utenti_bannati,parse_mode='HTML')


            informazioni_chat=bot.getChat(gruppo[0].id_gruppo)
            self.gruppo=Gruppo(gruppo[0].id_gruppo, gruppo[0].giorni_ban, gruppo[0].punizione)
            gruppo_attuale=self.ritorna_lista_membri_gruppo(gruppo[0].id_gruppo,informazioni_chat['username'])

            if len(gruppo_attuale)==0:
                for utente_database in gruppo[1]:
                    self.database.rimuovi_utente(utente_database.id_utente, utente_database.id_gruppo)

            #controllo se gli utenti del gruppo coincidono con quelli all'interno del database
            elif len(gruppo[1])>len(gruppo_attuale):
                for utente_database in gruppo[2]:
                    utentePresente=False
                    for utente_presente in gruppo_attuale:
                        if utente_presente.id_utente==utente_database.id_utente:
                            utentePresente=True
                            break
                    if not utentePresente:
                        self.database.rimuovi_utente(utente_database.id_utente, utente_database.id_gruppo)
            t.sleep(10)

        return



bot = telepot.Bot(TOKEN)
shadowbanbot = Shadowbanbot(bot)
bot.message_loop({'chat':shadowbanbot.on_chat_text,'callback_query':shadowbanbot.on_call_back_query}, run_forever=True)
