TOP_DIR = ..
-include $(TOP_DIR)/local.mk
include $(TOP_DIR)/variables.mk

all : snmp json

debug :
	echo $(SNMPLOG_SNMP)

snmp :
	sh run_snmpwalk.sh REMOTE_AGENTS="$(REMOTE_AGENTS)"

json : $(SNMPLOG_JSON)

%.json : %.snmp
	snmp2json -o $@ $<

clean :
	rm -f *.json

mclean :
	$(MAKE) clean
	rm -f *.snmp

.PHONY : \
	all clean test snmp mclean

