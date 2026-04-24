# this is a recursive use of make - Again, Chapter 4 of make manual
# $(MAKE) is your make program, -C is an option that tells make to change its directory and 
# then run make.

SUBDIRS = foo bar baz
# subdirs:
#	for dir in $(SUBDIRS); do \
#		$(MAKE) -C $$dir; \
#	done

# another way to write the above is
.PHONY: subdirs $(SUBDIRS)
subdirs: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@