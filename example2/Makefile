-include local.mk
include  variables.mk

all : snmp arp

snmp :
	$(MAKE) -C snmp

arp :
	$(MAKE) -C arp

clean :
	$(MAKE) -C snmp clean
	$(MAKE) -C arp  clean

mclean :
	$(MAKE) -C snmp mclean
	$(MAKE) -C arp  mclean
	
.PHONY : \
	all clean test snmp arp mclean

