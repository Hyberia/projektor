# Created by : Jamie Nadeau
# Version    : 0.1
# Revision   : 38

CC = gcc
CFLAGS = -g -Wall
OBJECTS = toueid.o
INCFLAGS =
LDFLAGS = -Wl,-rpath,/usr/local/lib
LIBS = -L/usr/local/lib -lReadToueiConfig

all: toueid

toueid: $(OBJECTS)
	$(CC) -o toueid $(OBJECTS) $(LDFLAGS) $(LIBS)

.SUFFIXES:
.SUFFIXES:	.c .cc .C .cpp .o

.c.o :
	$(CC) -o $@ -c $(CFLAGS) $< $(INCFLAGS)

install:
	cp toueid /usr/local/bin

uninstall:
	rm /usr/local/bin/toueid

count:
	wc *.c *.cc *.C *.cpp *.h *.hpp

clean:
	rm -f *.o
	rm -f toueid

.PHONY: all
.PHONY: count
.PHONY: clean
.PHONY: install
.PHONY: uninstall
