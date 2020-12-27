class TestClass:
    def __init__(self, a=10, b=None, c=20):
        self.a = a
        self.b = b
        self.c = c

    def test(self, a=None, b=None, c=None):
        args_func = locals().copy()
        print(args_func)
        for key in args_func:
            if str(key) == 'self':
                continue
            var = eval(key)
            if var is not None:
                print(key,":",var)
                self.__dict__[key] = var


testObj = TestClass(10,20)
testObj.test(23,34)
print(testObj.a,testObj.b,testObj.c)