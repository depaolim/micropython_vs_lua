#include <iostream>
#include "emb.h"

static const char* PROMPT = "> ";

int main(int argc, char *argv[]) {
	std::cout << "PyShell 0.0.1" << std::endl;

    if (setup(argc, argv))
        return 1;

	std::string line;
	std::cout << PROMPT;

	while (std::getline(std::cin, line)) {
        int error = execute(line.c_str());
		if (error) {
			std::cerr << "ERROR" << std::endl;
            return error;
		}
		std::cout << PROMPT;
	}

	std::cout << std::endl;

    if (teardown())
        return 1;

    return 0;
}
