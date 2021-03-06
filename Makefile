# Makefile template for shared library
 
CC = gcc # C++ compiler
CFLAGS = -fPIC -Wall -Wextra -O3 -Werror -g # C flags
LDFLAGS = -shared # linking flags
RM = rm -f # rm command
TARGET_LIB = clib/clib.so # target lib
 
SRCS = $(shell echo clib/*.c) # source files
OBJS = $(SRCS:.c=.o)
 
.PHONY: all
all: ${TARGET_LIB}
 
$(TARGET_LIB): $(OBJS)
	$(CC) ${LDFLAGS} -o $@ $^
 
$(SRCS:.c=.d):%.d:%.c
	$(CC) $(CFLAGS) -MM $< >$@
 
include $(SRCS:.c=.d)
 
.PHONY: clean
clean:
	${RM} ${TARGET_LIB} ${OBJS} $(SRCS:.c=.d)
	${RM} *.pyc pylib/*.pyc
