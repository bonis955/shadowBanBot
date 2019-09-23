from telepot.namedtuple import InlineKeyboardMarkup,InlineKeyboardButton
from database.convertitore import parola_giorno

class Messaggio:
    def __init__(self,bot,database):
        self.bot=bot
        self.database=database

    def uscita_bot(self, chat_id):
        self.bot.sendMessage(chat_id, "Il gruppo deve essere pubblico affinchè il bot funzioni")
        self.bot.leaveChat(chat_id)
        self.database.rimuovi_gruppo(chat_id)
        return

    def help(self, chat_id):
        self.bot.sendMessage(chat_id,
                        "<b> Comandi del bot</b>\n\n"
                        "/lista_inattivi - riporta la lista degli utenti del gruppo con a fianco il loro periodo di inattività\n\n"
                        "/status_inattivo - Per sapere il tuo tempo di inattività\n\n"
                        "<b> Comandi admin</b>\n\n"
                        "/settimezone timezone - Setta il fuso orario per visualizzare l'ora corretta" 
                        "/setTempo tempo - Setta il periodo massimo per il ban dell'utente\n\n", parse_mode='HTML')

    def isVuoto(self, msg):
        vettore = str(" ".join(msg.split())).split(" ")
        try:
            dato = vettore[1]
        except:
            return None
        return dato

    def creaInlinekeyboard(self):
        inlineKeyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Setta il tempo di inattività', callback_data='/settime')],
            [InlineKeyboardButton(text='Setta la punizione', callback_data='/setpunizione')],
            [InlineKeyboardButton(text='⚠ Lista inattivi ⚠', callback_data='/listainattivi')],
            [InlineKeyboardButton(text='Chiudi tastiera', callback_data='/chiudi')]])
        return inlineKeyboard

    def impostazioni(self, chat_id, messaggio, gruppo, isquery=False, messaggio_modificato=0, inlinekeyboard=None):
        messaggio_default = messaggio + "\n\n<b>-Tempo massimo:</b> " + str(
            gruppo.giorni_ban) + " " + parola_giorno(
            gruppo.giorni_ban) + "\n<b>-La punizione:</b> " + gruppo.punizione
        if isquery:
            try:
                self.bot.editMessageText(messaggio_modificato, messaggio_default, reply_markup=inlinekeyboard,
                                    parse_mode='HTML')
            except:
                inlineKeyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Setta il tempo di inattività', callback_data='/settime')],
                    [InlineKeyboardButton(text='Setta la punizione', callback_data='/setpunizione')],
                    [InlineKeyboardButton(text='Chiudi tastiera', callback_data='/chiudi')]])
                self.bot.editMessageText(messaggio_modificato, messaggio_default, reply_markup=inlineKeyboard,
                                    parse_mode='HTML')
        else:
            self.bot.sendMessage(chat_id, messaggio_default, reply_markup=inlinekeyboard, parse_mode='HTML')
