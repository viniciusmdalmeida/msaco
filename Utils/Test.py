def decor(func):
    def action():
        print("Iniciando")
        x = func()
        print("finalizando",x)
    return action

@decor
def my_print():
    print("Ola!")
    return "Test"

from threading import Thread
import time

class thread_teste(Thread):
    def __init__(self, reps, name):
        Thread.__init__(self)
        print("init thread")
        self.reps = reps
        self.name = name

    def run(self):
        for i in range(self.reps):
            time.sleep(1)
            print(f'thread {i} interation')

    def print_alive(self):
        print(f"thread {self.name}, status: {self.is_alive()}")


class Tenho_thread(Thread):

    def __init__(self, reps=10, name = "test_thread"):
        Thread.__init__(self)
        self.thread = thread_teste(reps, name)

    def run(self):
        self.thread.start()
        self.thread.join()
        del self.thread
        print("Fim tenho thread")

    def print_alive(self):
        print("ainda esta rodando", self.is_alive())

test = Tenho_thread()
test.start()
time.sleep(5)
test.print_alive()
time.sleep(8)
test.join()
test_thread = test.thread
del test
test_thread.print_alive()