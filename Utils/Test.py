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

my_print()