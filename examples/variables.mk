SNMPLOG_SNMP = $(REMOTE_AGENTS:=.snmp)
SNMPLOG_JSON = $(SNMPLOG_SNMP:.snmp=.json)
SNMPLOG_DOT  = $(SNMPLOG_JSON:.json=.dot)

ARPLOG_ARP   = arpscan.arp
ARPLOG_JSON  = $(ARPLOG_ARP:.arp=.json)

DATABASE_DB   = database.db
DATABASE_SQL  = database.sql

GRAPH_YAML    = graph.yml
GRAPH_DOT     = $(GRAPH_YAML:.yml=.dot)
GRAPH_PDF     = $(GRAPH_DOT:.dot=.pdf)


