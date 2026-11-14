TOP_DIR = ..
-include $(TOP_DIR)/local.mk
include $(TOP_DIR)/variables.mk

all : snmp json db

debug :
	echo $(SNMPLOG_SNMP)

snmp :
	sh run_snmpwalk.sh REMOTE_AGENTS="$(REMOTE_AGENTS)"

json : $(SNMPLOG_JSON)

%.json : %.snmp
	snmp2json -o $@ $<

db : $(SNMPWALK_DB)

$(SNMPWALK_DB) : $(SNMPLOG_JSON)
	snmp2db -o $@ $(SNMPLOG_JSON)
	sqlite3 $@ ".dump" > $(SNMPWALK_SQL)

clean :
	rm -f $(SNMPLOG_JSON)
	rm -f $(SNMPWALK_DB)
	rm -f $(SNMPWALK_SQL)

mclean :
	$(MAKE) clean
	rm -f $(SNMPLOG_SNMP)
	rm -f *.snmp
	rm -f *.json

.PHONY : \
	all clean test snmp mclean

