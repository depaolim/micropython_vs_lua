import subprocess
import unittest


class Prog:
    def __init__(self, *cmd):
        self.shell = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def __getattr__(self, item):
        return getattr(self.shell, item)


class Shell(Prog):
    def __init__(self, lang):
        super().__init__("./shell_" + lang)


class TestDboxPy(unittest.TestCase):
    def test(self):
        prog = Prog("./dboxpy")
        prog.stdin.write(b"""
<xml>
    <script output='a:int;b:float'>
a = 10
b = a * 2
    </script>
</xml>
""")
        stdoutdata, stderrdata = prog.communicate()


class TestElements(unittest.TestCase):
    def test_ok(self):
        prog = Prog("./test_elements")
        prog.stdin.write(b"<xml><tag></tag></xml>")
        stdoutdata, stderrdata = prog.communicate()
        self.assertEqual(prog.returncode, 0)
        self.assertIn(b"tag", stdoutdata)
        self.assertFalse(stderrdata)

    def test_nok(self):
        prog = Prog("./test_elements")
        prog.stdin.write(b"<xml></xml-wrong>")
        stdoutdata, stderrdata = prog.communicate()
        self.assertNotEqual(prog.returncode, 0)
        self.assertIn(b"xml", stdoutdata)
        self.assertIn(b"mismatched tag at line 1", stderrdata)


    def test_characters(self):
        prog = Prog("./test_elements")
        prog.stdin.write(b"<xml><ctag>SOME</ctag><ctag2> CHARACTERS</ctag2></xml>")
        stdoutdata, stderrdata = prog.communicate()
        self.assertEqual(prog.returncode, 0)
        self.assertIn(b"SOME", stdoutdata)
        self.assertIn(b" CHARACTERS", stdoutdata)
        self.assertFalse(stderrdata)


class TestPy(unittest.TestCase):
    def test_print(self):
        shell = Shell("py")
        shell.stdin.write(b"print(\"ciao\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"ciao", stdoutdata)
        self.assertFalse(stderrdata)

    def test_print_a_variable_value(self):
        shell = Shell("py")
        shell.stdin.write(b"""
a = 10
print(a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertFalse(stderrdata)

    def test_call_a_non_existent_function(self):
        shell = Shell("py")
        shell.stdin.write(b"_not_existent_function(10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"NameError", stderrdata)
        self.assertIn(b"ERROR", stderrdata)

    def test_syntax_error(self):
        shell = Shell("py")
        shell.stdin.write(b"print((10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"SyntaxError", stderrdata)
        self.assertIn(b"ERROR", stderrdata)

    @unittest.skip
    def test_call_a_private_function(self):
        shell = Shell("py")
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
        shell = Shell("py")
        shell.stdin.write(b"log_10(\"wrongtype\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"TypeError", stderrdata)

    def test_import_std_module(self):
        shell = Shell("py")
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
        shell = Shell("upy")
        shell.stdin.write(b"print(\"ciao\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"ciao", stdoutdata)
        self.assertFalse(stderrdata)

    def test_print_a_variable_value(self):
        shell = Prog("./shell_upy", "a", "undef")
        shell.stdin.write(b"""
a = 10
print(a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertIn(b"globals:\na = 10.00\nundef = <UNDEF>\n", stdoutdata)
        self.assertFalse(stderrdata)

    def test_call_a_non_existent_function(self):
        shell = Shell("upy")
        shell.stdin.write(b"_not_existent_function(10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 1)
        self.assertIn(b"NameError:", stderrdata)

    def test_call_a_private_function(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
a = log_10(100.0)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 2.0", stdoutdata)

    def test_call_with_wrong_argument_type(self):
        shell = Shell("upy")
        shell.stdin.write(b"log_10(\"wrongtype\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"TypeError", stderrdata)

    def test_import_std_module(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import math
a = math.log(8, 2)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 3.0", stdoutdata)

    def test_import_c_implemented_module(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
a = example.double(1000)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 2000", stdoutdata)

    def test_import_external_module(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import pyexamplemod as exm
a = exm.double(3000)
print("return value:", a)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 6000", stdoutdata)

    def test_import_c_implemented_module_with_constant(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
print("return value:", example.BeforeSend)
        """)
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 1", stdoutdata)


class TestUpyCClass(unittest.TestCase):

    def test_c_initialize_default(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
pp = example.PolarPoint()
print("return value:", pp.radius)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 0", stdoutdata)

    def test_c_initialize_with_values(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
pp = example.PolarPoint(1, 2)
print("return value:", pp.radius)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 1", stdoutdata)


class TestLua(unittest.TestCase):
    def test_print(self):
        shell = Shell("lua")
        shell.stdin.write(b"print(\"ciao\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"ciao", stdoutdata)
        self.assertFalse(stderrdata)

    def test_print_a_variable_value(self):
        shell = Shell("lua")
        shell.stdin.write(
                b"a = 10\n"
                b"print(a)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertFalse(stderrdata)

    def test_call_a_non_existent_function(self):
        shell = Shell("lua")
        shell.stdin.write(b"_sleep(10)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertTrue(stderrdata)

    def test_call_a_private_function(self):
        shell = Shell("lua")
        shell.stdin.write(
                b"a = sleep(10)\n"
                b"print(\"return value: \")\n"
                b"print(a)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertFalse(stderrdata)
        self.assertIn(b"return value: \n> nil", stdoutdata)

    def test_call_a_private_function_with_return_value(self):
        shell = Shell("lua")
        shell.stdin.write(
                b"a = log_10(100.0)\n"
                b"print(\"return value: \")\n"
                b"print(a)\n")
        stdoutdata, stderrdata = shell.communicate()
        self.assertFalse(stderrdata)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: \n> 2.0", stdoutdata)

    def test_call_with_wrong_argument_type(self):
        shell = Shell("lua")
        shell.stdin.write(b"sleep(\"wrongtype\")")
        stdoutdata, stderrdata = shell.communicate()
        self.assertNotEqual(shell.returncode, 0)
        self.assertIn(b"Assertion", stderrdata)


if __name__ == '__main__':
    unittest.main()
