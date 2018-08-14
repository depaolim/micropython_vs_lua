MPTOP = micropython
LUATOP = lua-5.3.5
PYTOP = cpython
EXPATTOP = libexpat

all: test

shell.o: shell.cpp emb.h
	g++ -std=c++11 -c shell.cpp

shell_py: shell.o emb_py.o $(PYTOP)/libpython3.8m.a
	# $(PYTOP)/python python-config.py --ldflags
	g++ -o shell_py shell.o emb_py.o -L$(PYTOP) -L$(PYTOP)/build/lib/python3.8/config-3.8m-x86_64-linux-gnu -lpython3.8m -lpthread -ldl -lutil -lm -Xlinker -export-dynamic

emb_py.o: emb_py.c emb.h
	# $(PYTOP)/python python-config.py --cflags
	gcc -std=c99 -c emb_py.c -I$(PYTOP)/Include -I$(PYTOP) -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall

$(PYTOP)/libpython3.8m.a: $(PYTOP)/Makefile
	(cd $(PYTOP); $(MAKE)) 

$(PYTOP)/Makefile:
	git submodule update --init --recursive
	(cd $(PYTOP); ./configure) 

shell_upy: shell.o emb_upy.o -lmicropython
	g++ -o shell_upy shell.o emb_upy.o -lmicropython -L.

emb_upy.o: emb_upy.c
	git submodule update --init --recursive
	gcc -std=c99 -c emb_upy.c -I$(MPTOP) -I. -DNO_QSTR -g

-lmicropython:
	$(MAKE) -f $(MPTOP)/examples/embedding/Makefile.upylib MPTOP=$(MPTOP)

lua: $(LUATOP).tar.gz $(LUATOP)/src/lua
	$(LUATOP)/src/lua fac.lua

$(LUATOP).tar.gz:
	curl -R -O http://www.lua.org/ftp/$(LUATOP).tar.gz

$(LUATOP)/src/lua:
	tar zxf $(LUATOP).tar.gz
	(cd $(LUATOP); make linux test)

shell_lua: lua shell.o emb_lua.o
	g++ -o shell_lua shell.o emb_lua.o -llua -lm -ldl -pthread -L$(LUATOP)/src

emb_lua.o: lua emb_lua.cpp
	g++ -std=c++11 -c emb_lua.cpp -I$(LUATOP)/src

elements: expat
	gcc -std=c99 -c elements.c -I$(EXPATTOP)/expat/lib
	g++ -o elements elements.o -lexpat -L$(EXPATTOP)/expat/lib
	# ./elements < $(EXPATTOP)/testdata/largefiles/nes96.xml

expat: $(EXPATTOP)/expat $(EXPATTOP)/expat/lib/libexpat.la

$(EXPATTOP)/expat:
	git submodule update --init --recursive

$(EXPATTOP)/expat/lib/libexpat.la:
	(cd $(EXPATTOP)/expat; mkdir -p m4; ./buildconf.sh; ./configure --without-docbook; make)

test: shell_py shell_upy shell_lua elements
	(export PYTHONHOME=$(PYTOP) ; export PYTHONPATH=$(PYTOP)/Lib:$(PYTOP)/build/lib.linux-x86_64-3.8 ; $(PYTOP)/python tests.py)

test_threads:
	git submodule update --init --recursive
	(cd $(MPTOP)/ports/unix; $(MAKE) axtls; $(MAKE))
	$(MPTOP)/ports/unix/micropython sample_threads/thread_test.py

cscope:
	cscope -R

clean:
	rm -rf shell_upy shell_lua shell_py elements
	rm -rf *.o libmicropython.a build
	rm -rf __pycache__
	rm -rf cscope.out
	rm -rf $(LUATOP)
	rm -rf $(EXPATTOP)/expat/lib/libexpat.la

clean_all: clean
	rm -rf $(LUATOP).tar.gz
	git submodule deinit $(MPTOP)
	git submodule deinit $(PYTOP)
	git submodule deinit $(EXPATTOP)
