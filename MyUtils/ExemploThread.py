from threading import Thread
from time import sleep


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

thread1 = Thread(target = threaded_fabrica, args = (10, ))
thread2 = Thread(target = threaded_consumo, args = (10, ))
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print ("thread finished...exiting")