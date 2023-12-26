APP ?= targetlox-c
RPYTHON ?= pypy/rpython/bin/rpython
ARGS ?= -O2

SOURCES=$(shell find lox -type f -name "*.py")

all: $(APP)

$(APP): targetlox.py $(SOURCES)
	$(RPYTHON) $(ARGS) $<

clean:
	$(RM) $(APP)
