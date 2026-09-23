SNMPLOG_SNMP = $(REMOTE_AGENTS:=.snmp)
SNMPLOG_JSON = $(SNMPLOG_SNMP:.snmp=.json)
SNMPLOG_DOT  = $(SNMPLOG_JSON:.json=.dot)

ARPLOG_ARP   = $(REMOTE_IFACES:=.arp)
ARPLOG_JSON  = $(ARPLOG_ARP:.arp=.json)

ARPSCAN_DB    = $(TOP_DIR)/arp/arpscan.db
ARPSCAN_SQL   = $(TOP_DIR)/arp/arpscan.sql

SNMPWALK_DB   = $(TOP_DIR)/snmp/snmpwalk.db
SNMPWALK_SQL  = $(TOP_DIR)/snmp/snmpwalk.sql

DATABASE_DB   = database.db
DATABASE_SQL  = database.sql

GRAPH_YML    = graph.yml
GRAPH_DOT     = $(GRAPH_YML:.yml=.dot)
GRAPH_PDF     = $(GRAPH_DOT:.dot=.pdf)


