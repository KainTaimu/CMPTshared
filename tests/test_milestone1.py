from io import StringIO
from pathlib import Path
from CMPT_Milestone1_EP_HM import *
import builtins
import pytest
import sys
import logging
import shutil


LOGGER = logging.getLogger(__name__)


class Mute:
    """Mutes any stdout output during function/methods calls within the context manager"""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        sys.stdout = self._stdout


class Capturing(list):
    """Captures all print() outputs within the context manager"""

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


@pytest.fixture
def route_data():
    """Return a fresh RouteData instance for each test"""
    return RouteData()


@pytest.fixture
def routes_data(route_data: RouteData):
    """Return a RouteData instance with routes data loaded"""
    with Mute():
        route_data.load_routes_data("data/routes.txt")
    return route_data


@pytest.fixture
def shapes_data(route_data: RouteData):
    """Return a RouteData instance with shapes data loaded"""
    with Mute():
        route_data.load_shapes_data("data/shapes.txt")
    return route_data


@pytest.fixture
def complete_route_data(route_data: RouteData):
    """Return a RouteData instance with both shape and trips data loaded"""
    with Mute():
        route_data.load_routes_data("data/routes.txt")
        route_data.load_shapes_data("data/shapes.txt")
        
    return route_data


@pytest.fixture
def no_data_path(monkeypatch):
    """Creates a temporary directory with nothing in it to test when etsdata.p doesn't exist"""
    path = Path(__file__).parent
    monkeypatch.chdir(path)    
    (path / "data").mkdir()
    yield path
    shutil.rmtree(path / "data")


@pytest.fixture
def data_path(monkeypatch):
    """Changes the current directory to a directory with a valid etsdata.p file"""
    path = Path(__file__).parent / "test_files"
    monkeypatch.chdir(path)    
    return path


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


def test_print_menu():
    with Capturing() as output:
        print_menu()
    assert output == TEST_MENU_OUTPUT, "print_menu() prints out the wrong menu!"


@pytest.mark.parametrize(
    "command,expected_message",
    [
        ("99", "Invalid Option"),
        ("3", "Option 3 reserved for Milestone#2"),
        ("6", "Option 6 reserved for Milestone#2"),
        ("9", "Option 9 reserved for Milestone#2"),
    ],
)
def test_invalid_options(monkeypatch, command, expected_message):
    inputs = [command, "0"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(input_iter))

    expected_output = [
        *TEST_MENU_OUTPUT,
        f"Enter Command: {expected_message}",
        *TEST_MENU_OUTPUT,
        "Enter Command: ",
    ]

    with CapturingInputOutput() as output:
        main()

    assert output == expected_output


def test_load_route_data_valid_path(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/routes.txt")
    expected = ["Enter a filename: Data from data/routes.txt loaded"]

    with CapturingInputOutput() as output:
        load_route_data(route_data)

    assert output == expected


def test_load_route_data_invalid_path(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "non_existent_file")
    expected = ["Enter a filename: IOError: Couldn't open non_existent_file"]
    with CapturingInputOutput() as output:
        load_route_data(route_data)

    assert output == expected


def test_load_route_data_default_path(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Enter a filename: Data from data/routes.txt loaded"]

    with CapturingInputOutput() as output:
        load_route_data(route_data)

    assert output == expected


def test_load_shape_data_valid_path(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/shapes.txt")
    expected = ["Enter a filename: Data from data/shapes.txt loaded"]

    with CapturingInputOutput() as output:
        load_shape_data(route_data)

    assert output == expected


def test_load_shape_data_invalid_path(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "non_existent_file")
    expected = ["Enter a filename: IOError: Couldn't open non_existent_file"]

    with CapturingInputOutput() as output:
        load_shape_data(route_data)

    assert output == expected


def test_load_shape_data_default_path(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Enter a filename: Data from data/shapes.txt loaded"]

    with CapturingInputOutput() as output:
        load_shape_data(route_data)

    assert output == expected


def test_print_shape_ids_not_loaded(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Route data hasn't been loaded yet"]

    with CapturingInputOutput() as output:
        print_shape_ids(route_data)

    assert output == expected


def test_print_shape_ids_found(monkeypatch, routes_data):
    monkeypatch.setattr('builtins.input', lambda prompt="": "117")
    expected_1 = [
        "Enter route: Shape ids for route [Eaux Claires - West Clareview]",
        "\t117-34-East",
        "\t117-35-West",
    ]
    expected_2 = [
        "Enter route: Shape ids for route [Eaux Claires - West Clareview]",
        "\t117-35-West",
        "\t117-34-East",
    ]
    
    with CapturingInputOutput() as output:
        print_shape_ids(routes_data)
    
    # print(set) is unpredictable due to nature of data structure
    assert output == expected_1 or output == expected_2


def test_print_shape_ids_not_found(monkeypatch, routes_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "100")
    expected = ["Enter route: \t** NOT FOUND **"]

    with CapturingInputOutput() as output:
        print_shape_ids(routes_data)

    assert output == expected


def test_print_coordinates_not_loaded(route_data):
    expected = ["Shape ID data hasn't been loaded yet"]

    with CapturingInputOutput() as output:
        print_coordinates(route_data)

    assert output == expected


def test_print_coordinates_found(monkeypatch, shapes_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "112-3-East")
    expected = [
        "Enter shape ID: Shape ID coordinates for 112-3-East are:",
        "\t(53.616871, -113.516426)",
        "\t(53.616892, -113.516468)",
        "\t(53.616896, -113.516513)",
        "\t(53.616897, -113.516584)",
        "\t(53.616866, -113.516763)",
    ]

    with CapturingInputOutput() as output:
        print_coordinates(shapes_data)

    assert output[:6] == expected


def test_print_coordinates_not_found(monkeypatch, shapes_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "112-3")
    expected = ["Enter shape ID: \t** NOT FOUND **"]

    with CapturingInputOutput() as output:
        print_coordinates(shapes_data)

    assert output == expected


def test_save_routes_valid_path(monkeypatch, complete_route_data, no_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/etsdata.p")
    expected = ['Enter a filename: Data structures successfully written to data/etsdata.p']
    
    with CapturingInputOutput() as output:
        save_routes(complete_route_data)
    
    assert output == expected
    

def test_save_routes_invalid_path(monkeypatch, complete_route_data, no_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "non_existent_folder/etsdata.p")
    expected = ['Enter a filename: IOError: Couldn\'t save to non_existent_folder/etsdata.p']
    
    with CapturingInputOutput() as output:
        save_routes(complete_route_data)
    
    assert output == expected
    

def test_save_routes_default_path(monkeypatch, complete_route_data, no_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ['Enter a filename: Data structures successfully written to data/etsdata.p']
    
    with CapturingInputOutput() as output:
        save_routes(complete_route_data)
    
    assert output == expected

    
def test_save_routes_routes_not_loaded(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/etsdata.p")
    expected = ["Route data hasn't been loaded yet"]
    
    with CapturingInputOutput() as output:
        save_routes(route_data)
    
    assert output == expected
    
    
def test_save_routes_shapes_not_loaded(monkeypatch, routes_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/etsdata.p")
    expected = ["Shape ID data hasn't been loaded yet"]
    
    with CapturingInputOutput() as output:
        save_routes(routes_data)
    
    assert output == expected
    
# TODO How tf to test loading???
# pickle.load() inside load_routes() fails as RouteData is not defined within this test file's namespace

# def test_load_routes_valid_path(monkeypatch, route_data):
#     monkeypatch.setattr("builtins.input", lambda prompt="": "data/etsdata.p")
#     expected = ["Enter a filename: Routes and shapes Data structures successfully loaded from data/etsdata.p"]
    
#     with CapturingInputOutput() as output:
#         _ = load_routes()
        
#     assert output == expected