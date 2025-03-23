import builtins
from io import StringIO
import unittest.mock
from CMPT_Milestone1_EP_HM import *
import unittest
import sys


class Colors:
    """ANSI color codes"""

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


class Mute:
    """
    Mutes any stdout output during function/methods calls within the context manager
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        sys.stdout = self._stdout


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


class CapturingInputOutput(list):
    """Captures both stdout and input prompts during testing"""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        self._original_input = builtins.input

        def mock_input_capture(prompt=""):
            # Write the prompt to stdout so it's captured
            if prompt:
                print(prompt, end="")
            # Let the test's mocked input handle the actual input
            return self._original_input()

        builtins.input = mock_input_capture
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
        builtins.input = self._original_input


class TestIO(object):
    """
    A class to store input and output test data.

    This class helps manage test cases by storing a collection of inputs and expected outputs,
    allowing for iteration over these pairs.

    Args:
        inputs (list[list[str]]): A list of input test cases, where each test case is a list of strings.
        outputs (list[list[str]]): A list of expected output test cases, where each test case is a list of strings.

    Raises:
        TypeError: If inputs or outputs are not lists.
        Exception: If inputs and outputs have different lengths.

    Examples:
        >>> test_data = TestIO([['input1'], ['input2']], [['output1'], ['output2']])
        >>> for test_input, expected_output in test_data:
        ...     # Run your test
        ...     pass
    """

    def __init__(self, inputs: list[list[str]], outputs: list[list[str]]) -> None:
        if not isinstance(inputs, list):
            raise TypeError("inputs argument must be a list of strings")
        if not isinstance(outputs, list):
            raise TypeError("outputs argument must be a list of strings")
        if len(inputs) != len(outputs):
            raise Exception("Inputs must have the same elements as outputs")

        self.inputs = inputs
        self.outputs = outputs
        self.index = 0

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.inputs)

    def __next__(self):
        if self.index >= len(self.inputs):
            raise StopIteration
        value = (self.inputs[self.index], self.outputs[self.index])
        self.index += 1
        return value


class TestPrintMenu(unittest.TestCase):
    TEST_MENU_OUTPUT = [
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
        "(0) Quit",
        "",
    ]

    def test_stdout(self):
        with Capturing() as output:
            print_menu()
        self.assertEqual(
            output, self.TEST_MENU_OUTPUT, "print_menu() prints out the wrong menu!"
        )

    @unittest.mock.patch("builtins.input")
    def test_invalid_option(self, mocked_input: unittest.mock.Mock):
        EXPECTED_INPUT = [
            ["99", "0"],
            ["3", "0"],
            ["6", "0"],
            ["9", "0"],
        ]
        EXPECTED_OUTPUT = [
            [
                *self.TEST_MENU_OUTPUT,
                "Enter Command: Invalid Option",
                *self.TEST_MENU_OUTPUT,
                "Enter Command: ",
            ],
            [
                *self.TEST_MENU_OUTPUT,
                "Enter Command: Option 3 reserved for Milestone#2",
                *self.TEST_MENU_OUTPUT,
                "Enter Command: ",
            ],
            [
                *self.TEST_MENU_OUTPUT,
                "Enter Command: Option 6 reserved for Milestone#2",
                *self.TEST_MENU_OUTPUT,
                "Enter Command: ",
            ],
            [
                *self.TEST_MENU_OUTPUT,
                "Enter Command: Option 9 reserved for Milestone#2",
                *self.TEST_MENU_OUTPUT,
                "Enter Command: ",
            ],
        ]

        for exp_input, exp_output in TestIO(EXPECTED_INPUT, EXPECTED_OUTPUT):
            mocked_input.side_effect = exp_input

            with CapturingInputOutput() as output:
                main()

            self.assertEqual(
                output,
                exp_output,
                f"\nFunction {Colors.UNDERLINE}load_route_data{Colors.END}:\nwith inputs:\n{exp_input}\ngot:\n{Colors.RED}{output}{Colors.END}\nexpected:\n{Colors.GREEN}{exp_output}{Colors.END}",
            )


class TestLoadRouteData(unittest.TestCase):
    @unittest.mock.patch("builtins.input")
    def test_load_route_data(self, mocked_input: unittest.mock.Mock):
        EXPECTED_INPUT = [
            ["non_existent_file"],
            ["data/trips.txt"],
            [""],
        ]
        EXPECTED_OUTPUT = [
            ["Enter a filename: IOError: Couldn't open non_existent_file"],
            ["Enter a filename: Data from data/trips.txt loaded"],
            ["Enter a filename: Data from data/trips.txt loaded"],
        ]

        for exp_input, exp_output in TestIO(EXPECTED_INPUT, EXPECTED_OUTPUT):
            mocked_input.side_effect = exp_input
            data = RouteData()

            with CapturingInputOutput() as output:
                load_route_data(data)

            self.assertEqual(
                output,
                exp_output,
                f"\nFunction {Colors.UNDERLINE}load_route_data{Colors.END}:\nwith inputs:\n{exp_input}\ngot:\n{Colors.RED}{output}{Colors.END}\nexpected:\n{Colors.GREEN}{exp_output}{Colors.END}",
            )


class TestLoadShapeData(unittest.TestCase):
    @unittest.mock.patch("builtins.input")
    def test_load_shape_data(self, mocked_input: unittest.mock.Mock):
        EXPECTED_INPUT = [
            ["non_existent_file"],
            ["data/shapes.txt"],
            [""],
        ]
        EXPECTED_OUTPUT = [
            ["Enter a filename: IOError: Couldn't open non_existent_file"],
            ["Enter a filename: Data from data/shapes.txt loaded"],
            ["Enter a filename: Data from data/shapes.txt loaded"],
        ]

        for exp_input, exp_output in TestIO(EXPECTED_INPUT, EXPECTED_OUTPUT):
            mocked_input.side_effect = exp_input
            data = RouteData()

            with CapturingInputOutput() as output:
                load_shape_data(data)

            self.assertEqual(
                output,
                exp_output,
                f"\nFunction {Colors.UNDERLINE}load_shape_data{Colors.END}:\nwith inputs:\n{exp_input}\ngot:\n{Colors.RED}{output}{Colors.END}\nexpected:\n{Colors.GREEN}{exp_output}{Colors.END}",
            )


class TestLoadPrintShapeIds(unittest.TestCase):
    TRIPS_PATH = "data/trips.txt"

    @unittest.mock.patch("builtins.input")
    def test_print_shape_ids_not_loaded(self, mocked_input: unittest.mock.Mock):
        EXPECTED = ["Route data hasn't been loaded yet"]
        mocked_input.side_effect = [""]
        data = RouteData()
        with CapturingInputOutput() as output:
            print_shape_ids(data)

        self.assertEqual(output, EXPECTED)
        
    @unittest.mock.patch("builtins.input")
    def test_print_shape_ids(self, mocked_input: unittest.mock.Mock):
        EXPECTED = [
            "Enter route: Shape ids for route [Eaux Claires - West Clareview]",
            "\t117-34-East",
            "\t117-35-West",
        ]

        mocked_input.side_effect = ["117"]
        data = RouteData()
        with Mute():
            data.load_trips_data(self.TRIPS_PATH)
        with CapturingInputOutput() as output:
            print_shape_ids(data)

        self.assertEqual(output, EXPECTED)
        
    @unittest.mock.patch("builtins.input")
    def test_print_shape_ids_not_found(self, mocked_input: unittest.mock.Mock):
        EXPECTED = ["Enter route: \t** NOT FOUND **",]
        mocked_input.side_effect = ["100"]
        data = RouteData()
        with Mute():
            data.load_trips_data(self.TRIPS_PATH)
        with CapturingInputOutput() as output:
            print_shape_ids(data)

        self.assertEqual(output, EXPECTED)


class TestLoadPrintCoordinates(unittest.TestCase):
    SHAPES_PATH = "data/shapes.txt"

    def test_print_shape_ids_not_loaded(self):
        EXPECTED = [
            "Shape ID data hasn't been loaded yet",
        ]

        data = RouteData()
        with CapturingInputOutput() as output:
            print_coordinates(data)

        self.assertEqual(output, EXPECTED)

    @unittest.mock.patch("builtins.input")
    def test_print_shape_ids(self, mocked_input: unittest.mock.Mock):
        # As shown in page 15 of project specs
        EXPECTED = [
            "Enter shape ID: Shape ID coordinates for 112-3-East are:",
            "\t(53.616871, -113.516426)",
            "\t(53.616892, -113.516468)",
            "\t(53.616896, -113.516513)",
            "\t(53.616897, -113.516584)",
            "\t(53.616866, -113.516763)",
        ]

        mocked_input.side_effect = ["112-3-East", "112-3"]
        data = RouteData()

        with Mute():
            data.load_shapes_data(self.SHAPES_PATH)
        with CapturingInputOutput() as output:
            print_coordinates(data)

        self.assertEqual(output[:6], EXPECTED)

    @unittest.mock.patch("builtins.input")
    def test_print_shape_ids_not_found(self, mocked_input: unittest.mock.Mock):
        EXPECTED = ["Enter shape ID: \t** NOT FOUND **"]

        mocked_input.side_effect = ["112-3"]
        data = RouteData()

        with Mute():
            data.load_shapes_data(self.SHAPES_PATH)
        with CapturingInputOutput() as output:
            print_coordinates(data)

        self.assertEqual(output, EXPECTED)


if __name__ == "__main__":
    unittest.main()
