class Value(object):
    def __init__(self, value, value_type):
        self.value = value

    def repr(self):
        return str(self.value)

class ValueArray(object):
    def __init__(self):
        self.values = []

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, key, item):
        self.values[key] = item

    def __len__(self):
        return len(self.values)

    def append(self, value):
        self.values.append(value)
        return len(self.values) - 1
