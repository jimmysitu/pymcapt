.PHONY: all default clean
.SUFFIXES: .cc .o

MAKEFLAGS += -j$(shell nproc)

ifndef NTHREADS
  NTHREADS = 4
endif

TARGET = _mcpat.so
TAG = dbg

LIBS = -lm
INCS = -Imcpat/cacti -Imcpat $(shell python2-config --cflags | cut -d ' ' -f1)

ifeq ($(TAG),dbg)
  DBG = -Wall
  OPT = -ggdb -g -O0 -DNTHREADS=1 
else
  DBG =
  OPT = -O2 -msse2 -mfpmath=sse -DNTHREADS=$(NTHREADS)
endif

CXXFLAGS = -fPIC $(DBG) $(OPT) $(INCS)
LDFLAGS = -shared -pthread
CXX = g++
CC  = gcc

VPATH = mcpat:mcpat/cacti

SRCS  = \
  array.cc \
  basic_components.cc \
  core.cc \
  interconnect.cc \
  iocontrollers.cc \
  logic.cc \
  memoryctrl.cc \
  noc.cc \
  processor.cc \
  sharedcache.cc \
  XML_Parse.cc \
  xmlParser.cc \
  arbiter.cc \
  area.cc \
  bank.cc \
  basic_circuit.cc \
  cacti_interface.cc \
  component.cc \
  crossbar.cc \
  decoder.cc \
  htree2.cc \
  io.cc \
  mat.cc \
  nuca.cc \
  parameter.cc \
  powergating.cc \
  router.cc \
  subarray.cc \
  technology.cc \
  uca.cc \
  Ucache.cc \
  wire.cc \

OBJS = $(patsubst %.cc, objs/%.o,$(SRCS))

default: objs $(OBJS)
	swig -c++ -python -Imcpat -Imcpat/cacti -o mcpat_wrap.cc -threads mcpat.i
	$(CXX) $(CXXFLAGS) -c mcpat_wrap.cc -o mcpat_wrap.o
	$(CXX) $(LDFLAGS) $(LIBS)  mcpat_wrap.o $(OBJS) -o $(TARGET)

test:
	python2 -c "import mcpat; help(mcpat)"

exe: objs $(OBJS)
	$(CXX) $(LDFLAGS) $(LIBS) $(OBJS) -o libmcpat.so
	$(CXX) $(CXXFLAGS) mcpat/main.cc -L. -lmcpat -o mcpat.exe

objs:
	-mkdir objs

objs/%.o: %.cc
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	-rm -rf objs *.o libmcpat.so mcpat.exe $(TARGET)
