from abc import ABC, abstractmethod


class AbstractClass(ABC):

    def __init__(self, value):
        self.value = value
        super().__init__()

    @abstractmethod
    def do_something(self):
        pass

    @abstractmethod
    def do_something2(self):
        pass

# Examplo Error
# class Example(AbstractClass):
#     def do_something(self):
#         print("Teste")

class Example(AbstractClass):
    def do_something(self):
        print("Teste")

    def do_something2(self):
        print("Teste2")

exemplo = Example(10)
exemplo.do_something()