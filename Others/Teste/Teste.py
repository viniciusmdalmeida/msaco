class Teste:
    def check(self):
        if self.teste is None:
            self.teste = "OK"
        print(self.teste)

teste = Teste()
teste.check()
teste.teste = "Testando"
teste.check()