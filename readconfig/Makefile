#Created by Jamie Nadeau

CC = g++
MODULES= readconfig.o ReadConfigLib.o
OBJECTS=
RCLOBJECTS= ReadConfigLib.cpp readconfig.cpp configDefinitions.h readconfig.h ReadConfigLib.h readconfig.h configDefinitions.h
LDFLAGS = -Wl,-rpath,/usr/lib
LIBS = -L/usr/local/lib -lReadToueiConfig

all: libReadToueiConfig.so

libReadToueiConfig.so: $(MODULES)
	$(CC) -shared $(MODULES) -o libReadToueiConfig.so

readconfig.o: $(RCLOBJECTS)
	$(CC) -O2 -s -fpic -c readconfig.cpp -o readconfig.o

ReadConfigLib.o: $(RCLOBJECTS)
	$(CC) -O2 -s -fpic -c ReadConfigLib.cpp -o ReadConfigLib.o
	

install:
	cp libReadToueiConfig.so /usr/local/lib
	
uninstall:
	rm /usr/local/lib/libReadToueiConfig.so
	
count:
	wc *.c *.cc *.C *.cpp *.h *.hpp

clean:
	rm -f *.o
	rm -f libReadToueiConfig.so

.PHONY: all
.PHONY: count
.PHONY: clean
.PHONY: install
.PHONY: uninstall
