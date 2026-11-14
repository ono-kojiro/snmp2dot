TOP_DIR = ..
-include $(TOP_DIR)/local.mk
include $(TOP_DIR)/variables.mk

all : arp json db

arp :
	sh run_arpscan.sh REMOTE_IFACES="$(REMOTE_IFACES)"

json : $(ARPLOG_JSON)

%.json : %.arp
	arp2json -o $@ $<

db : $(ARPSCAN_DB)

$(ARPSCAN_DB) : $(ARPLOG_JSON)
	arp2db -o $@ $(ARPLOG_JSON)
	sqlite3 $@ ".dump" > $(ARPSCAN_SQL)

clean :
	rm -f $(ARPLOG_JSON)
	rm -f $(ARPSCAN_DB) $(ARPSCAN_SQL)

mclean :
	$(MAKE) clean
	rm -f *.arp
	rm -f *.json

.PHONY : \
	all clean test snmp mclean db

