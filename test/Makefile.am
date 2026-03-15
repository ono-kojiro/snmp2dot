AGENTS = switch3

PREPARE_SH     = $(sort $(wildcard prepare-*.sh))
TESTSCRIPTS_SH = $(sort $(wildcard test-*.sh))

all : debug

prepare :
	prove $(PREPARE_SH)

test : check
	
check : pytest prove

pytest :
	pytest

prove :
	PYTHONPATH="$(top_srcdir)/lib" prove -v $(TESTSCRIPTS_SH)

debug :
	@for agent in $(AGENTS); do \
		python3 run_snmpwalk.py \
		  -c agents.yml -p password.yml \
		  -o $${agent}.log $${agent}; \
	done

.PHONY : \
	all test pytest probe

