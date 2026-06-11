# Standalone build (no CMake required)
CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -O2 -Iinclude
LDFLAGS ?=

LIB_SRCS = src/util.c src/cp2k_out.c src/cp2k_run.c src/sdc.c
LIB_OBJS = $(LIB_SRCS:.c=.o)

.PHONY: all clean install

all: simukit-sdc simukit-run

simukit-sdc: src/main_sdc.o libsimukit.a
	$(CC) $(CFLAGS) -o $@ src/main_sdc.o libsimukit.a $(LDFLAGS) -lm

simukit-run: src/main_run.o libsimukit.a
	$(CC) $(CFLAGS) -o $@ src/main_run.o libsimukit.a $(LDFLAGS)

libsimukit.a: $(LIB_OBJS)
	ar rcs $@ $(LIB_OBJS)

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(LIB_OBJS) src/main_sdc.o src/main_run.o libsimukit.a simukit-sdc simukit-run

install: all
	install -d ../bin
	install simukit-sdc simukit-run ../bin/
