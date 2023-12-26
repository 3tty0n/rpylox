from lox.object import ObjString

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
        raise NotImplementedError()

    def __repr__(self):
        return "<Value: '%s'>" % self.repr()

    def is_bool(self):
        return self.value_type == ValueType.BOOL

    def is_number(self):
        return self.value_type == ValueType.NUMBER

    def is_nil(self):
        return self.value_type == ValueType.NIL

    def is_obj(self):
        return self.value_type == ValueType.NIL

    def is_string(self):
        raise NotImplementedError()

    def as_bool(self):
        raise NotImplementedError()

    def as_number(self):
        raise NotImplementedError()

    def is_falsy(self):
        return isinstance(self, ValueNil) or isinstance(self, ValueBool) and (not self.as_bool())


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

class ValueNil(Value):
    def __init__(self, value=None, value_type=ValueType.NIL):
        self.value_type = value_type

    def repr(self):
        return "nil"

    def get_value(self):
        return self.value

    def as_bool(self):
        return ValueBool(False)

    def is_string(self):
        return False

    def negate(self):
        return self

class ValueBool(Value):
    def __init__(self, value, value_type=ValueType.BOOL):
        self.value = value
        self.value_type = value_type

    def repr(self):
        if self.value: return "true"
        else: return "false"

    def get_value(self):
        return self.value

    def is_string(self):
        return False

    def as_number(self):
        if self.value:
            return 1
        else:
            return 0

    def as_bool(self):
        return self.value

    def negate(self):
        return ValueBool(not self.value)

class ValueNumber(Value):
    def __init__(self, value, value_type=ValueType.NUMBER):
        self.value = value
        self.value_type = value_type

    def repr(self):
        return str(self.value)

    def get_value(self):
        return self.value

    def is_string(self):
        return False

    def add(self, w_other):
        assert isinstance(w_other, ValueNumber)
        return ValueNumber(self.value + w_other.value)

    def sub(self, w_other):
        assert isinstance(w_other, ValueNumber)
        return ValueNumber(self.value - w_other.value)

    def mul(self, w_other):
        assert isinstance(w_other, ValueNumber)
        return ValueNumber(self.value * w_other.value)

    def div(self, w_other):
        assert isinstance(w_other, ValueNumber)
        return ValueNumber(self.value / w_other.value)

    def negate(self):
        return ValueNumber(-self.value)

    def as_number(self):
        return self.value

    def as_bool(self):
        if self.value:
            return True
        return False

class ValueObj(Value):
    def __init__(self, obj, value_type=ValueType.OBJ):
        self.obj = obj
        self.value_type = value_type

    def __repr__(self):
        return self.repr()

    def repr(self):
        return self.obj.repr()

    def get_value(self):
        return self.obj

    def is_string(self):
        return isinstance(self.obj, ObjString)

    def negate(self):
        return self
