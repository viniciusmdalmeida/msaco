from  MyUtils.ThreadKillable import *
import time
from threading import Thread

class Route(ThreadKillable):
    pontos = []
    tempo = 20
    stop = False
    def __init__(self,cliente,pontos):
        Thread.__init__(self)
        self.cliente = cliente
        self.pontos = pontos

    def run(self):
        print("Iniciando Rota")
        pontoAtual = 0
        time.sleep(self.tempo)
        while pontoAtual<len(self.pontos) and self.stop == False:
            ponto = self.pontos[pontoAtual]
            print("movendo {}".format(ponto))
            self.cliente.moveToPositionAsync(ponto[0],ponto[1],ponto[2], 5).join()
            pontoAtual += 1
        print("Fim")
