class fibonacci:
    def __init__(self, limit):
        self.limit = limit
    
    def __iter__(self):
        self.a = 0
        self.b = 1
        return self
    
    def __next__(self):
        if self.a > self.limit:
            raise StopIteration
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        return result
    
for i in fibonacci(10):
    print(i)