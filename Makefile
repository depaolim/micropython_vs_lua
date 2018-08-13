MPTOP = micropython
LUATOP = lua-5.3.5
PYTOP = $(VIRTUAL_ENV)

all: test

shell_py: shell_py.o emb_py.o
	# python3-config --ldflags
	g++ -o shell_py shell_py.o emb_py.o -L$(PYTOP)/lib/python3.6/config-3.6m-x86_64-linux-gnu -lpython3.6m -lpthread -ldl -lutil -lm -Xlinker -export-dynamic

shell_py.o: shell_py.cpp emb.h
	# python3-config --cflags
	g++ -std=c++11 -c shell_py.cpp -I$(PYTOP)/include/python3.6m -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall

emb_py.o: emb_py.c emb.h
	# python3-config --cflags
	gcc -std=c99 -c emb_py.c -I/home/depaolim/Envs/micropython_vs_lua/include/python3.6m -I/home/depaolim/Envs/micropython_vs_lua/include/python3.6m -Wno-unused-result -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall

shell_upy: shell_upy.o -lmicropython
	g++ -o shell_upy shell_upy.o -lmicropython -L.

shell_upy.o: shell_upy.cpp
	git submodule update --init --recursive
	g++ -std=c++11 -c shell_upy.cpp -I$(MPTOP) -I. -DNO_QSTR -g

-lmicropython:
	$(MAKE) -f $(MPTOP)/examples/embedding/Makefile.upylib MPTOP=$(MPTOP)

lua: $(LUATOP).tar.gz $(LUATOP)/src/lua
	$(LUATOP)/src/lua fac.lua

$(LUATOP).tar.gz:
	curl -R -O http://www.lua.org/ftp/$(LUATOP).tar.gz

$(LUATOP)/src/lua:
	tar zxf $(LUATOP).tar.gz
	(cd $(LUATOP); make linux test)

shell_lua: lua shell_lua.o
	g++ -o shell_lua shell_lua.o -llua -lm -ldl -pthread -L$(LUATOP)/src

shell_lua.o: shell_lua.cpp
	g++ -std=c++11 -c shell_lua.cpp -I$(LUATOP)/src

test: shell_py shell_upy shell_lua
	python3 tests.py

test_threads:
	git submodule update --init --recursive
	(cd $(MPTOP)/ports/unix; $(MAKE) axtls; $(MAKE))
	$(MPTOP)/ports/unix/micropython sample_threads/thread_test.py

cscope:
	cscope -R

clean:
	rm -rf shell_upy shell_lua shell_py
	rm -rf *.o libmicropython.a build
	rm -rf __pycache__
	rm -rf cscope.out
	rm -rf $(LUATOP)

clean_all: clean
	rm -rf $(LUATOP).tar.gz
	git submodule deinit micropython
	git submodule deinit cpython
