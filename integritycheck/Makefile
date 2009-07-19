CXXFLAGS =	-O2 -g -Wall -fmessage-length=0

OBJS =		integritycheck.o

LIBS =

TARGET =	integritycheck

$(TARGET):	$(OBJS)
	$(CXX) -o $(TARGET) $(OBJS) $(LIBS)

all:	$(TARGET)

clean:
	rm -f $(OBJS) $(TARGET)
