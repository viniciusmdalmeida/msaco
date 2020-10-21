    from threading import Thread
from time import sleep
from MyUtils.ThreadKillable import *
import time

semaforo = False
contagem = 0

def threaded_fabrica(arg):
    global contagem
    global semaforo
    while True:
        while not semaforo:
            contagem += 1
            print("Fabrica:", contagem)
            semaforo = True
        sleep(0.5)

def threaded_consumo(arg):
    global contagem
    global semaforo
    while True:
        while semaforo:
            if contagem > 0:
                contagem -= 1
                print("Consumo:",contagem)
            else:
                print("Consumo sleep")
            semaforo = False
        sleep(0.8)

class ThreadTeste(ThreadKillable):
    def __init__(self,nome,tempo):
        Thread.__init__(self)
        self.tempo = tempo
        self.nome = nome
        self.cont = 0

    def run(self):
        time.sleep(self.tempo)
        while self.cont < 10:
            self.cont += 1
            print("{} =  cont:{}".format(self.nome,self.cont))
            time.sleep(self.tempo)


#Teste classes
thread1 = ThreadTeste("Teste1",10)
thread2 = ThreadTeste("Teste2",5)
thread1.start()
thread2.start()
print("Vamos la")
thread1.join()
thread2.join()

# thread1 = Thread(target = threaded_fabrica, args = (10, ))
# thread2 = Thread(target = threaded_consumo, args = (10, ))
# thread1.start()
# thread2.start()
# thread1.join()
# thread2.join()
# print ("thread finished...exiting")