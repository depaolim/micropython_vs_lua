import subprocess
import unittest


class Shell:
    def __init__(self, *args):
        self.shell = subprocess.Popen(
                args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __getattr__(self, item):
        return getattr(self.shell, item)


class TestPy(unittest.TestCase):
    def test_print(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"print(\"ciao\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"ciao", stdoutdata)
        self.assertFalse(stderrdata)

    def test_print_a_variable_value(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"""
a = 10
print(a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertFalse(stderrdata)

    def test_call_a_non_existent_function(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"_not_existent_function(10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"NameError", stderrdata)
        self.assertIn(b"ERROR", stderrdata)

    def test_syntax_error(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"print((10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"SyntaxError", stderrdata)
        self.assertIn(b"ERROR", stderrdata)

    @unittest.skip
    def test_call_a_private_function(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"""
a = log_10(100.0)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 2.0", stdoutdata)

    @unittest.skip
    def test_call_with_wrong_argument_type(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"log_10(\"wrongtype\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"TypeError", stderrdata)

    def test_import_std_module(self):
        shell = Shell("./shell_py")
        shell.stdin.write(b"""
import math
a = math.log(8, 2)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 3.0", stdoutdata)


class TestUpy(unittest.TestCase):
    def test_print(self):
        shell = Shell("./shell_upy")
        shell.stdin.write(b"print(\"ciao\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"ciao", stdoutdata)
        self.assertFalse(stderrdata)

    def test_print_a_variable_value(self):
        shell = Shell("./shell_upy")
        shell.stdin.write(b"""
a = 10
print(a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertFalse(stderrdata)

    def test_call_a_non_existent_function(self):
        shell = Shell("./shell_upy")
        shell.stdin.write(b"_not_existent_function(10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 1)
        self.assertIn(b"NameError:", stderrdata)

    def test_call_a_private_function(self):
        shell = Shell("./shell_upy")
        shell.stdin.write(b"""
a = log_10(100.0)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 2.0", stdoutdata)

    def test_call_with_wrong_argument_type(self):
        shell = Shell("./shell_upy")
        shell.stdin.write(b"log_10(\"wrongtype\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"TypeError", stderrdata)

    def test_import_std_module(self):
        shell = Shell("./shell_upy")
        shell.stdin.write(b"""
import math
a = math.log(8, 2)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 3.0", stdoutdata)


class TestLua(unittest.TestCase):
    def test_print(self):
        shell = Shell("./shell_lua")
        shell.stdin.write(b"print(\"ciao\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"ciao", stdoutdata)
        self.assertFalse(stderrdata)

    def test_print_a_variable_value(self):
        shell = Shell("./shell_lua")
        shell.stdin.write(
                b"a = 10\n"
                b"print(a)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertFalse(stderrdata)

    def test_call_a_non_existent_function(self):
        shell = Shell("./shell_lua")
        shell.stdin.write(b"_sleep(10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertTrue(stderrdata)

    def test_call_a_private_function(self):
        shell = Shell("./shell_lua")
        shell.stdin.write(
                b"a = sleep(10)\n"
                b"print(\"return value: \")\n"
                b"print(a)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertFalse(stderrdata)
        self.assertIn(b"return value: \n> nil", stdoutdata)

    def test_call_a_private_function_with_return_value(self):
        shell = Shell("./shell_lua")
        shell.stdin.write(
                b"a = log_10(100.0)\n"
                b"print(\"return value: \")\n"
                b"print(a)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: \n> 2.0", stdoutdata)

    def test_call_with_wrong_argument_type(self):
        shell = Shell("./shell_lua")
        shell.stdin.write(b"sleep(\"wrongtype\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"Assertion", stderrdata)


if __name__ == '__main__':
    unittest.main()