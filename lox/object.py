from rpython.rlib.objectmodel import r_dict, compute_hash

class ObjType:
     STRING = 0
     FUNCTION = 1

class Obj(object):
     def __init__(self, value_type):
          self.type = value_type

     def __repr__(self):
          return self.repr()

     def repr(self):
          return "UNREPRESENTABLE INSTANCE"

     def is_equal(self, other):
          return False

     def hash(self):
          return 0


class ObjString(Obj):
     def __init__(self, value):
          self.type = ObjType.STRING
          self.buffer = value
          self.length = len(value)

     def __repr__(self):
          return self.repr()

     def repr(self):
          return str(self.buffer)

     def is_equal(self, other):
          if self.type != other.type:
               return False
          return self.buffer == other.buffer

     def cmp_less(self, other):
          assert self.type == other.type
          return self.buffer < other.buffer

     def concat(self, other):
          return ObjString(self.buffer + other.buffer)

     def hash(self):
          return compute_hash(self.buffer)


class ObjFunction(Obj):
     def __init__(self, obj, chunk, name):
          self.obj = obj
          self.arity = 0
          self.chunk = chunk
          self.name = name

     def __repr__(self):
          return self.repr()

     def repr(self):
          return "<fn %s>" % self.name
