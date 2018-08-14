#include <assert.h>
#include <iostream>
#include <unistd.h>
#include <math.h>

#include "emb.h"
#include "lua.hpp"

static lua_State *L;


static int lua_sleep(lua_State* L) {
    int isnum;
    int m = lua_tointegerx(L, 1, &isnum);
    assert(isnum);
    usleep(m * 1000);
    return 0;
}


static int lua_log_10(lua_State* L) {
    int isnum;
    float m = lua_tonumberx(L, 1, &isnum);
    assert(isnum);
    lua_pushnumber(L, log10(m));
    return 1; // number of results
}


static void add_functions(lua_State* L) {
    lua_pushcfunction(L, lua_sleep);
    lua_setglobal(L, "sleep");
    lua_pushcfunction(L, lua_log_10);
    lua_setglobal(L, "log_10");
}


int setup(int argc, char *argv[]) {
	L = luaL_newstate();  // opens Lua
	luaL_openlibs(L);  // opens the standard libraries
    add_functions(L);  // add the private library
    return 0;
}


int teardown() {
	lua_close(L);
	return 0;
}


int execute(const char* const command) {
	int error = luaL_loadstring(L, command);
	if (not error) {
	    error = lua_pcall(L, 0, 0, 0);
	}
	if (error) {
	    std::cerr << lua_tostring(L, -1) << std::endl;
		lua_pop(L, 1);  // pop error message from stack
        return -1;
	}
    return 0;
}
