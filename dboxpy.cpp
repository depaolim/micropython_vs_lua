#include <stdio.h>
#include <time.h>


struct Timer
{
    Timer() {
        clock_gettime(CLOCK_MONOTONIC, &t1);
    }

    long elapsed() {
        clock_gettime(CLOCK_MONOTONIC, &t2);
        return (t2.tv_nsec - t1.tv_nsec);
    }

    struct timespec t1, t2;
};


int main(int argc, char *argv[]) {
    Timer t;

    // sample operation
    for (int idx = 0; idx < 3; ++idx) {
        fprintf(stdout, "%d elapsed nanoseconds: %ld\n", idx, t.elapsed());
    }

    fprintf(stdout, "nanoseconds: %ld\n", t.elapsed());
    return 0;
}
