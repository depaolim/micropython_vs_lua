#ifdef __cplusplus
extern "C" {
#endif
int setup(int argc, char *argv[]);
int teardown();
int execute(const char* const command);
#ifdef __cplusplus
}
#endif
