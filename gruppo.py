class Gruppo():
    def __init__(self,id_gruppo,giorni_ban=7,punizione='ban',lingua='italiano',fuso_orario="Europe/Rome"):
        self.id_gruppo=id_gruppo
        self.giorni_ban=giorni_ban
        self.punizione=punizione
        self.lingua=lingua
        self.fuso_orario=fuso_orario