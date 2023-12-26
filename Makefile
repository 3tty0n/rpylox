APP ?= targetlox-c
RPYTHON ?= pypy/rpython/bin/rpython
ARGS ?=

SOURCES=$(shell find lox -type f -name "*.py")

all: targetlox-jit targetlox-interp

targetlox-jit: targetlox.py $(SOURCES)
	$(RPYTHON) -Ojit $(ARGS) $<

targetlox-interp: targetlox.py $(SOURCES)
	$(RPYTHON) -O2 $(ARGS) $<

$(APP): targetlox.py $(SOURCES)
	$(RPYTHON) $(ARGS) $<

clean:
	$(RM) $(APP)
