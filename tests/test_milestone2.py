# type: ignore
from io import StringIO
from pathlib import Path
from CMPT_Milestone2_EP_HM import *
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


# https://stackoverflow.com/a/16571630
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
        self._original_input = (
            builtins.input
        )  # Save real input function before patching it

        def mock_input_capture(prompt=""):
            if prompt:
                print(prompt, end="")
            return self._original_input()

        # Patch the input function to explicitly print the prompt to stdout
        builtins.input = mock_input_capture
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
        # Unpatch the input function
        builtins.input = self._original_input


@pytest.fixture
def route_data():
    """Return a fresh RouteData instance for each test"""
    return RouteData()


@pytest.fixture
def routes_data(route_data: RouteData):
    """Return a RouteData instance with routes data loaded"""
    with Mute():
        route_data.load_trips_data("tests/test_files/data/trips.txt")
    return route_data


@pytest.fixture
def shapes_data(route_data: RouteData):
    """Return a RouteData instance with shapes data loaded"""
    with Mute():
        route_data.load_shapes_data("tests/test_files/data/shapes.txt")
    return route_data


@pytest.fixture
def routes_shapes_data(route_data: RouteData):
    """Return a RouteData instance with shapes data loaded"""
    with Mute():
        route_data.load_trips_data("tests/test_files/data/trips.txt")
        route_data.load_shapes_data("tests/test_files/data/shapes.txt")
    return route_data


@pytest.fixture
def disruptions_data(route_data: RouteData):
    """Return a RouteData instance with disruptions data loaded"""
    with Mute():
        route_data.load_disruptions_data("tests/test_files/data/traffic_disruptions.txt")
    return route_data

@pytest.fixture
def complete_route_data(route_data: RouteData):
    """Return a RouteData instance with both shape and trips data loaded"""
    with Mute():
        route_data.load_trips_data("tests/test_files/data/trips.txt")
        route_data.load_shapes_data("tests/test_files/data/shapes.txt")
        route_data.load_disruptions_data("tests/test_files/data/traffic_disruptions.txt")

    return route_data


@pytest.fixture
def empty_data_path(monkeypatch):
    """Changes the testing working directory to a empty temporary directory"""
    path = Path(__file__).parent
    monkeypatch.chdir(path)
    (path / "data").mkdir()
    yield path
    shutil.rmtree(path / "data")


@pytest.fixture
def valid_data_path(monkeypatch):
    """Changes the testing working directory to a directory with valid data files for loading testing"""
    path = Path(__file__).parent / "test_files"
    monkeypatch.chdir(path)
    return path


TEST_MENU_OUTPUT = [
    "",
    "Edmonton Transit System",
    "---------------------------------",
    "(1) Load route data",
    "(2) Load shapes data",
    "(3) Load disruptions data",
    "",
    "(4) Print shape IDs for a route",
    "(5) Print coordinates for a shape ID",
    "(6) Find longest shape for route",
    "",
    "(7) Save routes and shapes in a pickle",
    "(8) Load routes and shapes from a pickle",
    "",
    "(9) Interactive map",
    "(0) Quit",
    "",
]


def test_srt_parser(valid_data_path):
    import csv
    with open("data/traffic_disruptions.txt") as f:
        f.readline()
        srt_parsed = [SrtParser.parse_line(line) for line in f]
    with open("data/traffic_disruptions.txt") as f:
        f.readline()
        csv_parsed = [row for row in csv.reader(f)]
    assert srt_parsed == csv_parsed


def test_print_menu():
    with Capturing() as output:
        print_menu()
    assert output == TEST_MENU_OUTPUT, "print_menu() prints out the wrong menu!"


def test_load_route_data_valid_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/trips.txt")
    expected = ["Enter a filename: Data from data/trips.txt loaded"]

    with CapturingInputOutput() as output:
        load_route_data(route_data)

    assert output == expected


def test_load_route_data_invalid_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "non_existent_file")
    expected = ["Enter a filename: IOError: Couldn't open non_existent_file"]
    with CapturingInputOutput() as output:
        load_route_data(route_data)

    assert output == expected


def test_load_route_data_default_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Enter a filename: Data from data/trips.txt loaded"]

    with CapturingInputOutput() as output:
        load_route_data(route_data)

    assert output == expected


def test_load_shape_data_valid_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/shapes.txt")
    expected = ["Enter a filename: Data from data/shapes.txt loaded"]

    with CapturingInputOutput() as output:
        load_shape_data(route_data)

    assert output == expected


def test_load_shape_data_invalid_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "non_existent_file")
    expected = ["Enter a filename: IOError: Couldn't open non_existent_file"]

    with CapturingInputOutput() as output:
        load_shape_data(route_data)

    assert output == expected


def test_load_shape_data_default_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Enter a filename: Data from data/shapes.txt loaded"]

    with CapturingInputOutput() as output:
        load_shape_data(route_data)

    assert output == expected


def test_load_disruptions_data_valid_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/traffic_disruptions.txt")
    expected = ["Enter a filename: Data from data/traffic_disruptions.txt loaded"]

    with CapturingInputOutput() as output:
        load_disruptions_data(route_data)

    assert output == expected


def test_load_disruptions_data_invalid_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "non_existent_file")
    expected = ["Enter a filename: IOError: Couldn't open non_existent_file"]

    with CapturingInputOutput() as output:
        load_disruptions_data(route_data)

    assert output == expected


def test_load_disruptions_data_default_path(monkeypatch, route_data, valid_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Enter a filename: Data from data/traffic_disruptions.txt loaded"]

    with CapturingInputOutput() as output:
        load_disruptions_data(route_data)

    assert output == expected


def test_print_shape_ids_not_loaded(monkeypatch, route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = ["Route data hasn't been loaded yet"]

    with CapturingInputOutput() as output:
        print_shape_ids(route_data)

    assert output == expected


def test_print_shape_ids_found(monkeypatch, routes_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "117")
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

    LOGGER.info(output[:6])

    assert output[:6] == expected


def test_print_coordinates_not_found(monkeypatch, shapes_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "112-3")
    expected = ["Enter shape ID: \t** NOT FOUND **"]

    with CapturingInputOutput() as output:
        print_coordinates(shapes_data)

    assert output == expected


def test_print_longest_shape_routes_not_loaded(route_data):
    expected = ["Route data hasn't been loaded yet"]

    with CapturingInputOutput() as output:
        find_longest_shape(route_data)

    assert output == expected


def test_print_longest_shape_shapes_not_loaded(routes_data):
    expected = ["Shape ID data hasn't been loaded yet"]

    with CapturingInputOutput() as output:
        find_longest_shape(routes_data)

    assert output == expected

def test_print_longest_shape_disruptions_not_loaded(routes_shapes_data):
    expected = ["Disruptions data hasn't been loaded yet"]

    with CapturingInputOutput() as output:
        find_longest_shape(routes_shapes_data)

    assert output == expected


def test_print_longest_shape_found(monkeypatch, complete_route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "056")
    expected = [
        "Enter route ID: The longest shape for 056 is 056-148-East with 1045 coordinates",
    ]

    with CapturingInputOutput() as output:
        find_longest_shape(complete_route_data)

    assert output == expected


def test_print_longest_shape_not_found(monkeypatch, complete_route_data):
    monkeypatch.setattr("builtins.input", lambda prompt="": "9999")
    expected = ["Enter route ID: \t** NOT FOUND **"]

    with CapturingInputOutput() as output:
        find_longest_shape(complete_route_data)

    assert output == expected


def test_save_routes_valid_path(monkeypatch, complete_route_data, empty_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "data/etsdata.p")
    expected = [
        "Enter a filename: Data structures successfully written to data/etsdata.p"
    ]

    with CapturingInputOutput() as output:
        save_routes(complete_route_data)

    assert output == expected


def test_save_routes_invalid_path(monkeypatch, complete_route_data, empty_data_path):
    monkeypatch.setattr(
        "builtins.input", lambda prompt="": "non_existent_folder/etsdata.p"
    )
    expected = [
        "Enter a filename: IOError: Couldn't save to non_existent_folder/etsdata.p"
    ]

    with CapturingInputOutput() as output:
        save_routes(complete_route_data)

    assert output == expected


def test_save_routes_default_path(monkeypatch, complete_route_data, empty_data_path):
    monkeypatch.setattr("builtins.input", lambda prompt="": "")
    expected = [
        "Enter a filename: Data structures successfully written to data/etsdata.p"
    ]

    with CapturingInputOutput() as output:
        save_routes(complete_route_data)

    assert output == expected


# TODO How tf to test loading???
# pickle.load() inside load_routes() fails as RouteData is not defined within this test file's namespace

# def test_load_routes_valid_path(monkeypatch, route_data):
#     monkeypatch.setattr("builtins.input", lambda prompt="": "data/etsdata.p")
#     expected = ["Enter a filename: Routes and shapes Data structures successfully loaded from data/etsdata.p"]

#     with CapturingInputOutput() as output:
#         _ = load_routes()

#     assert output == expected
