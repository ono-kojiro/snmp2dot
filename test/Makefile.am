PREPARE_SH     = $(sort $(wildcard prepare-*.sh))
TESTSCRIPTS_SH = $(sort $(wildcard test-*.sh))

all :

prepare :
	prove $(PREPARE_SH)

test : check
	
check : pytest prove

pytest :
	pytest

prove :
	PYTHONPATH="$(top_srcdir)/lib" prove -v $(TESTSCRIPTS_SH)

.PHONY : \
	all test pytest probe

