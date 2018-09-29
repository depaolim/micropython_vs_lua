import os
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
    def test_timer(self):
        prog = Prog("./dboxpy")
        stdoutdata, stderrdata = prog.communicate()
        self.assertIn(b"nanoseconds", stdoutdata)


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


class TestUpyPyClass(unittest.TestCase):
    def test_class(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
class MyClass: pass
mc = MyClass()
print("return value:", mc)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: <MyClass object at", stdoutdata)

    def test_class(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
class MyClass: pass
mc = MyClass()
mc.my_attr = 8
print("return value:", mc.my_attr)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 8", stdoutdata)


class TestUpyCClass(unittest.TestCase):

    def test_initialize_default(self):
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

    def test_initialize_with_values(self):
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

    def test_set_value_from_python(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
pp = example.PolarPoint(1, 2)
pp.set_radius(3)
print("return value:", pp.radius)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 3", stdoutdata)

    @unittest.skip("TODO")
    def test_modify_attribute_from_python(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
pp = example.PolarPoint(1, 2)
pp.radius = 3
print("return value:", pp.radius)
""")
        stdoutdata, stderrdata = shell.communicate()
        print(stderrdata)
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 3", stdoutdata)

    @unittest.skip("TODO")
    def test_add_attribute_from_python(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import example
pp = example.PolarPoint(1, 2)
pp.new_attr = 3
print("return value:", pp.new_attr)
""")
        stdoutdata, stderrdata = shell.communicate()
        print(stderrdata)
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 3", stdoutdata)


class TestUpyGlobalStructure(unittest.TestCase):
    def test_py_defined_struct(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import uctypes
buf = b"12345678abcd"
struct = uctypes.struct(uctypes.addressof(buf), {"f32": uctypes.UINT32 | 0, "f64": uctypes.UINT64 | 4}, uctypes.LITTLE_ENDIAN)
struct.f32 = 0x7fffffff
print("return value:", buf)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: b'\\xff\\xff\\xff\\x7f5678abcd'", stdoutdata)

    def test_c_defined_bytearray(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
print("global_struct_size:", global_struct_size)
import uctypes
buf = uctypes.bytearray_at(global_struct_ptr, global_struct_size)
print("return value:", buf)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"global_struct_size: 8", stdoutdata)
        self.assertIn(b"return value: bytearray(b'\\n\\x00\\x00\\x00\\x14\\x00\\x00\\x00')", stdoutdata)

    def test_c_defined_bytearray_modified(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import uctypes
buf = uctypes.bytearray_at(global_struct_ptr, global_struct_size)
buf[0] = 0xff
print("return value:", buf)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: bytearray(b'\\xff\\x00\\x00\\x00\\x14\\x00\\x00\\x00')", stdoutdata)

    def test_c_defined_struct_modified(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import uctypes
buf = uctypes.bytearray_at(global_struct_ptr, global_struct_size)
global_struct = uctypes.struct(uctypes.addressof(buf), {"int_1": uctypes.INT32 | 0, "int_2": uctypes.INT32 | 4})
global_struct.int_1 = 0x99887766
print("return value:", buf)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: bytearray(b'fw\\x88\\x99\\x14\\x00\\x00\\x00')", stdoutdata)

    def test_c_defined_struct_slots(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
import uctypes
buf = uctypes.bytearray_at(global_struct_ptr, global_struct_size)
global_struct = uctypes.struct(uctypes.addressof(buf), {"int_1": uctypes.INT32 | 0, "int_2": uctypes.INT32 | 4})
global_struct.int_1 = 0x99
print("return value:", global_struct.int_1, global_struct.int_2)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 153 20", stdoutdata)

    def test_c_defined_struct_hidden(self):
        shell = Shell("upy")
        shell.stdin.write(b"""
global_struct.int_1 = 0x99
print("return value:", global_struct.int_1, global_struct.int_2)
""")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(stderrdata, b"")
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"return value: 153 20", stdoutdata)


class TestUpyMetaCommands(unittest.TestCase):
    def setUp(self):
        self.tmp_file_in = 'tmp_file.py'
        self.tmp_file_out = 'tmp_file.mpy'
        self.py_code = b"a = 10\nprint(a)\n"
        self.mpy_code = b"\x4d\x03\x00\x3f\x1d\x02\x00\x00\x00\x00\x00\x07\x33\x00\x01\x00\x00\x00\xff\x8a\x24\x2d\x01\x1b\xee\x00\x1b\x2d\x01\x64\x01\x32\x11\x5b\x08\x3c\x6d\x6f\x64\x75\x6c\x65\x3e\x00\x01\x61\x05\x70\x72\x69\x6e\x74\x01\x61\x00\x00"

    def tearDown(self):
        try:
            os.remove(self.tmp_file_in)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.tmp_file_out)
        except FileNotFoundError:
            pass

    def test_invalid_action(self):
        shell = Shell("upy")
        shell.stdin.write(b"\\x")
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 1)
        self.assertIn(b"unknown action", stderrdata)

    def test_store_mpy(self):
        with open(self.tmp_file_in, "wb") as f:
            f.write(self.py_code)
        shell = Shell("upy")
        shell.stdin.write(bytearray("\s {} {}".format(self.tmp_file_in, self.tmp_file_out), "utf8"))
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        with open(self.tmp_file_out, "rb") as f:
            buf = f.read()
        self.assertEqual(buf, self.mpy_code)

    def test_execute_mpy(self):
        with open(self.tmp_file_out, "wb") as f:
            f.write(self.mpy_code)
        shell = Shell("upy")
        shell.stdin.write(bytearray("\e {}".format(self.tmp_file_out), "utf8"))
        stdoutdata, stderrdata = shell.communicate()
        self.assertEqual(shell.returncode, 0)
        self.assertEqual(shell.returncode, 0)
        self.assertIn(b"10", stdoutdata)
        self.assertIn(b"\\x4d\\x03\\x00\\x3f", stderrdata)


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
