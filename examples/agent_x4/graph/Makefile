TOP_DIR = ..
-include $(TOP_DIR)/local.mk
include $(TOP_DIR)/variables.mk

all : db yml dot pdf

db : $(DATABASE_DB)

$(DATABASE_DB) : $(SNMPWALK_SQL) $(ARPSCAN_SQL)
	rm -f $@
	sqlite3 $@ < $(SNMPWALK_SQL)
	sqlite3 $@ < $(ARPSCAN_SQL)
	sqlite3 $@ ".dump" > $(DATABASE_SQL)

yml : $(GRAPH_YML)

$(GRAPH_YML) : $(DATABASE_DB)
	db2yml -o $@ $<

dot : $(GRAPH_DOT)

$(GRAPH_DOT) : $(GRAPH_YML)
	yml2dot -o $@ $<
	#cat $@

pdf : $(GRAPH_PDF)

$(GRAPH_PDF) : $(GRAPH_DOT)
	dot -Tpdf -o $@ $<

clean :
	rm -f $(DATABASE_DB) $(DATABASE_SQL)
	rm -f $(GRAPH_YML) $(GRAPH_DOT) $(GRAPH_PDF)

mclean :
	$(MAKE) clean
	rm -f *.db
	rm -f *.dot *.pdf

.PHONY : \
	all clean test mclean db

