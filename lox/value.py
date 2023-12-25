from lox.object import ObjString

class ValueType:
    BOOL = 0
    NIL = 1
    NUMBER = 2
    OBJ = 3

class Value(object):
    def __init__(self, value, value_type):
        if value_type == ValueType.BOOL:
            W_Bool.__init__(self, value)
        elif value_type == ValueType.NIL:
            W_Nil.__init__(self)
        elif value_type == ValueType.NUMBER:
            W_Number.__init__(self, value)
        elif value_type == ValueType.OBJ:
            W_Obj.__init__(self, value)

    def repr(self):
        return str(self.value)

    def get_value(self):
        return self.value

    def is_bool(self):
        return self.value_type == ValueType.BOOL

    def is_number(self):
        return self.value_type == ValueType.NUMBER

    def is_nil(self):
        return self.value_type == ValueType.NIL

    def is_obj(self):
        return self.value_type == ValueType.NIL

    def is_string(self):
        return isinstance(self.value, ObjString)

    def as_bool(self):
        raise NotImplemented

    def as_number(self):
        raise NotImplemented

    def is_falsy(self):
        return isinstance(self, W_Nil) or isinstance(self, W_Bool) and (not self.as_bool())


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

class W_Nil(Value):
    def __init__(self, value=None, value_type=ValueType.NIL):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        return "W_Nil"

    def as_bool(self):
        return W_Bool(False)

class W_Bool(Value):
    def __init__(self, value, value_type=ValueType.BOOL):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        return "%s" % self.repr()

    def as_number(self):
        if self.value:
            return W_Number(1)
        else:
            return W_Number(0)

    def as_bool(self):
        return self.value

class W_Number(Value):
    def __init__(self, value, value_type=ValueType.NUMBER):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        return "%s" % self.repr()

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

    def as_number(self):
        return self.value

    def as_bool(self):
        if self.value:
            return True
        return False

class W_Obj(Value):
    def __init__(self, value, value_type=ValueType.OBJ):
        self.value = value
        self.value_type = value_type

    def __repr__(self):
        if isinstance(self.value, ObjString):
            return '"%s"' % self.repr()
        return self.repr()

    def repr(self):
        return repr(self.value)
