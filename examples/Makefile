TOP_DIR = .

-include local.mk
include  variables.mk

#all : snmp arp db yml dot pdf
all : snmp arp db yml dot pdf

debug :
	echo $(GRAPH_YAML)

snmp :
	$(MAKE) -C snmp

json : $(SNMPLOG_JSON) $(ARPLOG_JSON)

%.json : %.snmp
	snmp2json -o $@ $<

%.json : %.arp
	arp2json -o $@ $<

db : $(DATABASE_DB)

$(DATABASE_DB) : $(SNMPWALK_SQL) $(ARPSCAN_SQL)
	rm -f $@
	sqlite3 $@ < $(SNMPWALK_SQL)
	sqlite3 $@ < $(ARPSCAN_SQL)
	createview -o $@
	sqlite3 $@ ".dump" > $(DATABASE_SQL)

yml : $(GRAPH_YAML)

$(GRAPH_YAML) : $(DATABASE_DB)
	db2yml --config config.yml -o $@ $(DATABASE_DB)

dot : $(GRAPH_DOT)

%.dot : %.yml
	#yml2dot -o $@ $<
	yml2dot --config config.yml -o $@ $<

arp :
	$(MAKE) -C arp

pdf : $(GRAPH_PDF)

$(GRAPH_PDF) : $(GRAPH_DOT)
	dot -Tpdf -o $@ $<

clean :
	$(MAKE) -C snmp clean
	$(MAKE) -C arp  clean

mclean :
	$(MAKE) clean
	$(MAKE) -C snmp mclean
	$(MAKE) -C arp  mclean
	rm -f $(DATABASE_DB)
	rm -f $(DATABASE_SQL)
	rm -f $(GRAPH_YAML)
	rm -f $(GRAPH_DOT)
.PHONY : \
	all clean test snmp arp \
	$(AGENTS)

