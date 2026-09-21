AGENTS = 192.168.1.252 192.168.122.10 192.168.122.20 192.168.1.72
#AGENTS = 192.168.122.10 192.168.122.20

SNMPLOG_SNMP = $(AGENTS:=.snmp)
SNMPLOG_JSON = $(SNMPLOG_SNMP:.snmp=.json)
SNMPLOG_DOT  = $(SNMPLOG_JSON:.json=.dot)

ARPLOG_ARP   = arpscan.arp
ARPLOG_JSON  = $(ARPLOG_ARP:.arp=.json)

DATABASE_DB   = database.db
DATABASE_SQL  = database.sql

GRAPH_YAML    = graph.yml
GRAPH_DOT     = $(GRAPH_YAML:.yml=.dot)
GRAPH_PDF     = $(GRAPH_DOT:.dot=.pdf)

all : json db yml dot pdf

debug :
	echo $(GRAPH_YAML)

snmp : $(SNMPLOG_SNMP)

%.snmp :
	snmpwalk ${@:.snmp=} > $@


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
	db2yml --config config.yml -o $@ $(DATABASE_DB)

dot : $(GRAPH_DOT)

%.dot : %.yml
	#yml2dot -o $@ $<
	yml2dot --config config.yml -o $@ $<

arp :
	sh run_arpscan.sh

pdf : $(GRAPH_PDF)

$(GRAPH_PDF) : $(GRAPH_DOT)
	dot -Tpdf -o $@ $<

clean :
	rm -f $(SNMPLOG_JSON)
	rm -f $(ARPLOG_JSON)
	rm -f $(DATABASE_DB)
	rm -f $(DATABASE_SQL)
	rm -f $(GRAPH_YAML)
	rm -f $(GRAPH_DOT)
	rm -f $(GRAPH_PDF)
	
mclean :
	$(MAKE) clean
	rm -f $(SNMPLOG_SNMP)
	rm -f $(ARPLOG_ARP)

.PHONY : \
	all clean test \
	$(AGENTS)

