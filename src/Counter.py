class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def toString(self):
        return str(self.count)

    def reset(self):
        self.count = 0
