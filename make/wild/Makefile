# This example is from Chapter 4 of the make manual - you can read about
# wildcards and static pattern rules from here 
# Initially your directory will contain the .o files. Running make should work
# What happens when you run make clean, and then try to run make again?
# Why? Can you fix it? 

# 1. $(patsubst %.c,%.o,$(wildcard *.c)) to get all object files
# 2. $(objects): %.o: %.c - static pattern rules
# 	 	$(CXX)-c $(CFLAGS) $<-o $@
# try using the above ways (or any other way ;) ) to fix this makefile!

CXX = gcc
CFLAGS = -g
objects = *.o
foo : $(objects)
	$(CXX) -o foo $(CFLAGS) $(objects)
.PHONY : clean
clean :
	rm foo *.o