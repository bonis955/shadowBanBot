def parola_giorno(tempo):
    if tempo == 1:
        return "giorno"
    else:
        return "giorni"

def dataItaliana(data):
        dataMostrare = str(data.strftime("%x")).split("/")
        dataMess = dataMostrare[1] + "/" + dataMostrare[0] + "/" + dataMostrare[2]
        return dataMess