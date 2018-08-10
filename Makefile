MPTOP = micropython
LUATOP = lua-5.3.5

all: test

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

test: shell_upy shell_lua
	python3 tests.py

test_threads:
	git submodule update --init --recursive
	(cd $(MPTOP)/ports/unix; $(MAKE) axtls; $(MAKE))
	$(MPTOP)/ports/unix/micropython sample_threads/thread_test.py

cscope:
	cscope -R

clean:
	rm -rf shell_upy shell_lua *.o libmicropython.a build __pycache__ cscope.out $(LUATOP) $(LUATOP).tar.gz
	git submodule deinit micropython
