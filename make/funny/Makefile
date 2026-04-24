# this example is from Chapter 4 of the make manual

# A normal prerequisite makes two statements: 
# 1. It imposes an order in which recipes will be invoked: the recipes
# for all prerequisites of a target will be completed before the recipe for the target is started.
# 2. It imposes a dependency relationship: if any prerequisite is newer than the target,
# then the target is considered out-of-date and must be rebuilt.

# Order only prerequisites don't enforce the 2nd one 

OBJDIR := objdir
OBJS := $(addprefix $(OBJDIR)/,foo.o bar.o baz.o)
$(OBJDIR)/%.o : %.c # what happens if you add redo as a prerequisite here? see the section on empty targets
	gcc -c $< -o $@ 
all: $(OBJS)
$(OBJS): | $(OBJDIR) # what happens without the | ?
$(OBJDIR):
	mkdir $(OBJDIR)

.PHONY : clean
clean:
	rm -r $(OBJDIR)
redo: