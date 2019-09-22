import telepot

class Utente:

    def __init__(self,id_gruppo,id_utente,nome,data_ban):
        self.id_gruppo=id_gruppo
        self.id_utente=id_utente
        self.nome=nome
        self.data_ban=data_ban

    def istimeban(self,bot,tempo_rimasto,punizione):
        try:
            if tempo_rimasto<=0:
                bot.kickChatMember(self.id_gruppo, self.id_utente)
                if punizione=="kick":
                    messaggio="rimosso"
                    bot.unbanChatMember(self.id_gruppo, self.id_utente)
                else:
                    messaggio="bannato"
                bot.sendMessage(self.id_gruppo,
                                    "L'utente <b>"+self.nome+"</b> è stato "+messaggio+" dal gruppo per inattività ⚠", parse_mode='HTML')
                return 0
            else:
                return 1
        except telepot.exception.NotEnoughRightsError:
            return 2
        except telepot.exception.TelegramError:
            return 3





