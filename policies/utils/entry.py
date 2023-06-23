
class Entry:

    counter_total = 0

    def __init__(self):
        self.value = 0
        self.counter = 0
        self.sumValue = 0
        self.sumSquaredValue = 0
        self.values = []

    def set_value(self, value):
        self.value = value
        self.counter = self.counter + 1
        Entry.counter_total = Entry.counter_total + 1

    def set_value_sums(self, value):
        self.sumValue = self.sumValue + value
        self.sumSquaredValue = self.sumSquaredValue + value**2

    def update(self, value):
        old_value = self.value
        counter = self.counter
        new_value = ((counter / (counter + 1)) * old_value) + ((1 / (counter + 1)) * value)
        self.set_value(new_value)
        self.set_value_sums(value)
