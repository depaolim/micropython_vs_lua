#include <assert.h>
#include <iostream>
#include <vector>
#include <thread>
#include <unistd.h>
#include <math.h>

#include "lua.hpp"

static const char* PROMPT = "> ";
static const int num_of_threads = 10;
std::vector<std::thread> threads;


void call_from_thread() {
    std::cout << "Hello, World!" << std::endl;
}


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


int main(void) {
    threads.push_back(std::thread(call_from_thread));

    for (std::thread& t : threads)
        t.join();

	std::cout << "Lua shell 0.0.1" << std::endl;
	lua_State *L = luaL_newstate();  // opens Lua
	luaL_openlibs(L);  // opens the standard libraries
    add_functions(L);  // add the private library

	std::string line;
	std::cout << PROMPT;

	while (std::getline(std::cin, line)) {
		int error = luaL_loadstring(L, line.c_str());
		if (not error) {
			error = lua_pcall(L, 0, 0, 0);
		}
		if (error) {
			std::cerr << lua_tostring(L, -1) << std::endl;
			lua_pop(L, 1);  // pop error message from stack
		}
		std::cout << PROMPT;
	}

	std::cout << std::endl;

	lua_close(L);
	return 0;
}
