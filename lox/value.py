class ValueType:
    BOOL = 0
    NIL = 1
    NUMBER = 2
    OBJ = 3

class Value(object):
    def __init__(self, value, value_type):
        self.value = value
        self.value_type = value_type

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

class W_Bool(Value):
    def __init__(self, value, value_type=ValueType.BOOL):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        return "W_Bool(%s)" % self.repr()

class W_Number(Value):
    def __init__(self, value, value_type=ValueType.NUMBER):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        return "W_Number(%s)" % self.repr()

    def add(self, w_other):
        assert isinstance(w_other, W_Number)
        return W_Number(self.value + w_other.value)

    def sub(self, w_other):
        assert isinstance(w_other, W_Number)
        return W_Number(self.value - w_other.value)

    def mul(self, w_other):
        assert isinstance(w_other, W_Number)
        return W_Number(self.value * w_other.value)

    def div(self, w_other):
        assert isinstance(w_other, W_Number)
        return W_Number(self.value / w_other.value)

class W_Obj(Value):
    def __init__(self, value, value_type=ValueType.OBJ):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        return "W_Obj(%s)" % self.repr()
