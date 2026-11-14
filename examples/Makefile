TOP_DIR = .

-include $(TOP_DIR)/local.mk
include $(TOP_DIR)/variables.mk

all : snmp arp

prepare :
	sudo apt -y install snmp sqlite3

debug :
	echo $(GRAPH_YAML)

snmp :
	$(MAKE) -C snmp

arp :
	$(MAKE) -C arp

json : $(SNMPLOG_JSON) $(ARPLOG_JSON)

%.json : %.snmp
	snmp2json -o $@ $<

%.json : %.arp
	arp2json -o $@ $<

db : $(DATABASE_DB)

$(DATABASE_DB) : $(SNMPLOG_JSON) $(ARPLOG_JSON)
	rm -f $@
	snmp2db -c config.yml -o $@ $(SNMPLOG_JSON)
	arp2db  -o $@ $(ARPLOG_JSON)
	createview -o $@
	sqlite3 $@ ".dump" > $(DATABASE_SQL)

yml : $(GRAPH_YAML)

$(GRAPH_YAML) : $(DATABASE_DB)
	db2yml -o $@ $(DATABASE_DB)

dot : $(GRAPH_DOT)

%.dot : %.yml
	#yml2dot -o $@ $<
	yml2dot --config config.yml -o $@ $<

pdf : $(GRAPH_PDF)

$(GRAPH_PDF) : $(GRAPH_DOT)
	dot -Tpdf -o $@ $<

clean :
	$(MAKE) -C snmp clean
	$(MAKE) -C arp  clean

mclean :
	$(MAKE) -C snmp mclean
	$(MAKE) -C arp  mclean

.PHONY : \
	all clean test snmp arp

