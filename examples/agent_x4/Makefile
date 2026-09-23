TOP_DIR = .

-include local.mk
include  variables.mk

all : build

build :
	cd ../../ && pip install -e .

test : snmp arp graph

snmp :
	$(MAKE) -C snmp

arp :
	$(MAKE) -C arp

graph :
	$(MAKE) -C graph

clean :
	$(MAKE) -C snmp  clean
	$(MAKE) -C arp   clean
	$(MAKE) -C graph clean

mclean :
	$(MAKE) -C snmp  mclean
	$(MAKE) -C arp   mclean
	$(MAKE) -C graph mclean
	
.PHONY : \
	all clean test snmp arp graph mclean

