# this example is completely from Chapter 2 of the make documentation
# refer that to know/experiment more

CXX = gcc
# objects = main.o kbd.o command.o display.o \
insert.o search.o files.o utils.o 
# uncomment the above and use this variable 


# note the line splitting here using \ 
# "Outside of recipe lines, backslash/newlines are converted into a single space character.
# Once that is done, all whitespace around the backslash/newline is condensed into a single
# space: this includes all whitespace preceding the backslash, all whitespace at the beginning
# of the line after the backslash/newline, and any consecutive backslash/newline combinations."

# Inside the recipe, however, "in contrast to how they are treated in other places in a makefile , 
# backslash/newline pairs are not removed from the recipe. Both the backslash and the newline 
# characters are preserved and passed to the shell. How the backslash/newline is interpreted 
# depends on your shell. "

# you can do some fun things with line splitting. See section 3.1 and 5.1 in the official docs

edit : main.o kbd.o command.o display.o \
insert.o search.o files.o utils.o
	$(CXX) -o edit main.o kbd.o command.o display.o \
insert.o search.o files.o utils.o
# edit : $(objects)
#	$(CXX) -o edit $(objects)
# is there an automatic variable that can replace $(objects) in the above?

# implicit rule for object files: update .o from 
# corresponding .c file using cc -c
main.o : main.c defs.h
	$(CXX) -c main.c
kbd.o : kbd.c defs.h command.h
	$(CXX) -c kbd.c
command.o : command.c defs.h command.h
	$(CXX) -c command.c
display.o : display.c defs.h buffer.h
	$(CXX) -c display.c
insert.o : insert.c defs.h buffer.h
	$(CXX) -c insert.c
search.o : search.c defs.h buffer.h
	$(CXX) -c search.c
files.o : files.c defs.h buffer.h command.h
	$(CXX) -c files.c
utils.o : utils.c defs.h
	$(CXX) -c utils.c

# instead of all that, we can simply write

# main.o : defs.h
# kbd.o : defs.h command.h
# command.o : defs.h command.h
# display.o : defs.h buffer.h
# insert.o : defs.h buffer.h
# search.o : defs.h buffer.h
# files.o : defs.h buffer.h command.h
# utils.o : defs.h

# thanks to implicit rules!


# alternatively, we can have

# $(objects) : defs.h
# kbd.o command.o files.o : command.h
# display.o insert.o search.o files.o : buffer.h


# .PHONY : clean
# what happens if clean is not declared as phony target, and clean is a file in the directory?
clean :
	rm edit main.o kbd.o command.o display.o \
insert.o search.o files.o utils.o