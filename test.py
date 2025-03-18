from io import StringIO
from CMPT_Milestone1_EP_HM import *
import unittest
import sys


# https://stackoverflow.com/a/16571630
class Capturing(list):
    """
    Captures all print() outputs within the context manager
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class TestPrintMenu(unittest.TestCase):
    def test_stdout(self):
        TEST = [
            "",
            "Edmonton Transit System",
            "---------------------------------",
            "(1) Load route data",
            "(2) Load shapes data",
            "(3) Reserved for future use",
            "",
            "(4) Print shape IDs for a route",
            "(5) Print coordinates for a shape ID",
            "(6) Reserved for future use",
            "",
            "(7) Save routes and shapes in a pickle",
            "(8) Load routes and shapes from a pickle",
            "",
            "(9) Reserved for future use",
            "(0) Quitd",
            "",
        ]
        with Capturing() as output:
            print_menu()
        self.assertEqual(
            output,
            TEST,
            "print_menu() prints out the wrong menu!"
        )


if __name__ == "__main__":
    unittest.main()
