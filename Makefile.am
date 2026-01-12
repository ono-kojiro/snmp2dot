ACLOCAL_AMFLAGS = -I config

SUBDIRS = test

all :

package :
	python3 -m build

prepare :
	python3 -m pip install -r requirements.txt

show :
	unzip -t ./dist/$(PACKAGE)-$(VERSION)-py3-none-any.whl

localinstall :
	pip install ./dist/$(PACKAGE)-$(VERSION)-py3-none-any.whl

li : localinstall

localuninstall :
	pip uninstall -y snmp2dot

lu : localuninstall

test : check

test-prepare :
	$(MAKE) -C test prepare

.PHONY : \
	test prepare package
