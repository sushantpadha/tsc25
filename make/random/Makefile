# these examples are randomly sourced, from AI or the manual or our slides

#.PHONY: print - what if we uncomment this line? (thanks @Shreyas Lohiya)
print: $(wildcard *.c)
	ls -la $?
	touch print

# below - explicit rules do not affect implicit rule search
foo : foo.o
	gcc -o $@ $<
foo.o : foo.p # which rule is used to make foo.o? why?

# below - difference between = and := demonstrated
# Chapter 6.2 in the make manual has more on this 
VALUE = initial
COND ?= $(VALUE)
RECURSIVE = $(VALUE)
SIMPLE := $(VALUE)
VALUE = updated
COND ?= $(VALUE)
COND ?= jellybean
# what will be the final values of RECURSIVE, SIMPLE and COND?
testassign:
	@echo "Recursive: $(RECURSIVE)" 
	@echo "Simple:    $(SIMPLE)"
	@echo "Cond:    $(COND)"
