# -------------------------------
# Erwin Panergo, Hadi Moughnieh
# Programming Project - Milestone#1
# -------------------------------

import pickle
from datetime import date
from graphics4 import GraphWin, Entry, Text, Point


class SrtParser:
    """Contains methods for parsing of comma separated strings"""

    @staticmethod
    def parse_line(string: str) -> list[str]:
        """
        purpose:
            Takes a comma separated string and returns it as a list of strings
        parameters:
            string: The comma separated string to parse
        returns:
            A list of strings representing each value in the comma separated string
        """
        chars = list(string)
        # First, replace all quoted strings with a NUL character
        strings = SrtParser.__parse_quoted_strings(chars)
        string, removed_strings = SrtParser.__remove_quoted_strings(string, strings)

        # Now that there's no quoted strings, we can separate it by commas normally
        spl = string.split(",")
        builder: list[str] = []
        i = 0

        # Then, substitute the original quoted strings in again
        for substring in spl:
            substring = substring.strip(" \n")
            if substring == "\0":
                substring = removed_strings[i]
                builder.append(substring)
                i += 1
                continue
            builder.append(substring)

        return builder

    @staticmethod
    def __parse_quoted_strings(chars: list[str], new=None) -> list[str]:
        """
        purpose:
            Recursively finds all quoted substrings within a list of chars
        parameters:
            chars: The list of chars to find quoted substrings from
            new: An accumulator list of previously found substrings
        returns:
            A list of the quoted strings found inside chars
        """
        if new is None:
            new = []
        if len(chars) == 0:
            return new
        current = chars.pop()
        # Go to next character if it's not "
        if current != '"':
            return SrtParser.__parse_quoted_strings(chars, new)

        # The current character is ". Now we track all characters until we reach another "
        builder = ""
        while True:
            current = chars.pop()
            if len(chars) == 0:
                raise Exception("Unterminated string")
            builder += current
            if current == '"':
                new.append(builder[-2::-1])
                break

        return SrtParser.__parse_quoted_strings(chars, new)

    @staticmethod
    def __remove_quoted_strings(
        string: str, substrings: list[str]
    ) -> tuple[str, list[str]]:
        """
        purpose:
            Replaces quoted strings with a NUL character
        parameters:
            string: The string to replace quoted strings in
            substrings: The list of substrings to replace
        returns:
            The modified string
        """
        removed_strings: list[str] = []
        new_string = string
        for substring in substrings:
            removed_strings.append(substring)
            new_string = new_string.replace(
                '"' + substring + '"', "\0"
            )  # We mark replaced strings with NUL to fill in later
        return new_string, removed_strings[::-1]


class DateConvert:
    """Contains methods that converts strings into date objects"""

    date_mapping = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    @staticmethod
    def strtodate(string: str) -> date:
        """
        purpose:
            Constructs a date object out of a string
        parameters:
            string: The string of form "MM DD, YY" to convert into a date object
        returns:
            A date object
        """
        string = string.replace(",", "")
        spl = string.split()
        month = DateConvert.date_mapping[spl[0]]
        day = int(spl[1])
        year = int(spl[2])
        return date(year, month, day)


class Coordinates:
    """Represents a point in geographic coordinates"""

    def __init__(self, longitude: float, latitude: float):
        """
        purpose:
            Constructs a Coordinates object
        parameters:
            longitude: A float that represents the longitudinal coordinate
            latitude: A float that represents the latitudinal coordinate
        returns:
            None
        """
        self.longitude = longitude
        self.latitude = latitude

    @staticmethod
    def parse(string: str) -> "Coordinates":
        """
        purpose:
            Parses a string into a Coordinates object
        parameters:
            string: The string of form "POINT (longitude latitude)"
        returns:
            The created Coordinates object
        """
        stripped = string[7:-2].split()
        longitude = float(stripped[0])
        latitude = float(stripped[1])
        return Coordinates(longitude, latitude)


class Shape:
    """Holds the shape ID and coordinates of a Shape"""

    def __init__(self, shape_id: str):
        """
        purpose:
            Constructs a Shape object
        parameters:
            shape_id: The initialized shape_id string
        returns:
            None
        """
        self.shape_id = shape_id
        self.coordinates: list[tuple[float, float]] = []


class Route:
    """Holds the route ID, full route name, and shape IDs specified in trips.txt"""

    def __init__(self, route_id: str):
        """
        purpose:
            Constructs a Route object
        parameters:
            route_id: The initialized route_id string
        returns:
            None
        """
        self.route_name = None
        self.route_id: str = route_id
        self.shape_ids: set[str] = set()

    def set_shape_id(self, shape_id: str) -> None:
        """
        purpose:
            Sets the shape ID attribute
        parameter:
            shape_id: The string to assign as attribute
        return:
            None
        """
        self.shape_ids.add(shape_id)

    def set_route_name(self, route_name: str) -> None:
        """
        purpose:
            Sets the route long name attribute
        parameter:
            route_name: The string to assign as attribute
        return:
            None
        """
        self.route_name = route_name


class Disruption:
    """Holds the coordinates of a disruption point and its finish date"""

    def __init__(self, finish_date: date, coords: Coordinates):
        """
        purpose:
            Constructs a Disruption object
        parameters:
            finish_date: The initialized finish date
            coords: The initialized Coordinate point
        returns:
            None
        """
        self.finish_date = finish_date
        self.coords = coords


class RouteData:
    """Provides an interface to load and access routes, shape IDs, and disruption data"""

    def __init__(self):
        """
        purpose:
            Constructs a RouteData object
        parameters:
            None
        returns:
            None
        """
        self.__route_names: dict[str, str] = {}
        self.__routes: dict[str, Route] = {}
        self.__shape_ids: dict[str, Shape] = {}
        self.__disruptions: set[Disruption] = set()

    def load_routes_data(self, routes_path: str) -> None:
        """
        purpose:
            Attempts to load the routes data file. Raises an IOError exception if routes_path is invalid.
        parameter:
            routes_path: A string pointing to a path to a routes data file.
        return:
            None
        """
        self.__routes = self.__load_routes_data(routes_path)

    def load_shapes_data(self, shapes_path: str) -> None:
        """
        purpose:
            Attempts to load the shapes data file. Raises an IOError exception if shapes_path is invalid.
        parameter:
            shapes_path: The file path to the shapes data file.
        return:
            None
        """
        self.__shape_ids = self.__load_shapes_data(shapes_path)

    def load_disruptions_data(self, disruptions_path: str) -> None:
        """
        purpose:
            Attempts to load the disruptions data file. Raises an IOError exception if disruptions_path is invalid.
        parameter:
            disruptions_path: The file path to the disruptions data file.
        return:
            None
        """
        self.__disruptions = self.__load_disruptions_data(disruptions_path)

    def get_route_long_name(self, route_id: str) -> str | None:
        """
        purpose:
            Gets the route long name from a route ID.
        parameter:
            route_id: The route ID string to find its associated route long name for.
        return:
            Returns the route long name of a route ID. Returns None if the route_id does not exist.
        """
        if route_id in self.__routes:
            return self.__routes[route_id].route_name
        return None

    def get_shape_ids_from_route_id(self, route_id: str) -> set[str] | None:
        """
        purpose:
            Gets the shape IDs associated with the route_id.
        parameter:
            route_id: The route ID to search shape IDs for.
        return:
            Returns the set of strings representing the shape IDs for a route ID. Returns None if the route_id does not exist.
        """
        if route_id in self.__routes:
            return self.__routes[route_id].shape_ids
        return None

    def get_coords_from_shape_id(
        self, shape_id: str
    ) -> list[tuple[float, float]] | None:
        """
        purpose:
            Returns the coordinates points associated with the shape ID.
        parameter:
            shape_id: The shape ID to search coordinate points for.
        return:
            Returns the list of coordinate points represented as a two-tuple of floats. Returns None if the shape_id does not exist.
        """
        if shape_id in self.__shape_ids:
            return self.__shape_ids[shape_id].coordinates
        return None


    def get_longest_shape_from_route_id(self, route_id: str) -> tuple[str, int] | None:
        """
        purpose:
            Returns the length, and shape_id associated with the route_id with the largest set of coordinates.
        parameter:
            route_id: The route ID to search a shape with the largest set of coordinates.
        return:
            Returns the shape_id string and the length of its coordinates as a tuple. Returns None if the route_id does not exist.
        """
        shape_ids = self.get_shape_ids_from_route_id(route_id)
        if not shape_ids:
            return None

        tracker: dict[int, str] = {}
        for shape_id in shape_ids:
            # May raise KeyError if routes and disruptions are loaded, but not shapes.
            # But we check for that in the find_longest_shape function anyways.
            # Bad design?
            shape = self.__shape_ids[shape_id]
            tracker[len(shape.coordinates)] = shape_id

        largest = max(tracker)
        return tracker[largest], largest


    def routes_loaded(self) -> bool:
        """
        purpose:
            Checks if the routes data file has been loaded.
        parameter:
            None
        return:
            Returns True if the routes file has been loaded. Otherwise, returns False.
        """
        if self.__routes:
            return True
        return False

    def shapes_loaded(self) -> bool:
        """
        purpose:
            Checks if the shapes data file has been loaded.
        parameter:
            None
        return:
            Returns True if the shapes file has been loaded. Otherwise, returns False.
        """
        if self.__shape_ids:
            return True
        return False

    def disruptions_loaded(self) -> bool:
        """
        purpose:
            Checks if the disruptions data file has been loaded.
        parameter:
            None
        return:
            Returns True if the disruptions file has been loaded. Otherwise, returns False.
        """
        if self.__disruptions:
            return True
        return False

    # BUG:
    # Will not raise an exception if routes_path is set to a wrong, yet valid file, such as trips.txt.
    # This results in routes having an incorrect long name.
    # ie: "8 Abbottsfield" instead of "Abbottsfield - Downtown - University"
    def __load_routes_data(self, routes_path: str) -> dict[str, Route]:
        """
        purpose:
            Parses the routes data file and saves it.
        parameter:
            routes_path: A string pointing to a path to a routes data file.
        return:
            Returns a dictionary with the route id as key and a Route object as value.
        """
        trips_path = "data/trips.txt"
        routes: dict[str, Route] = {}

        # Since trips.txt is hardcoded, the user will not know if opening 'data/trips.txt' raises an error.
        with open(trips_path) as f:
            f.readline()  # We skip the CSV header line
            for line in f:
                spl = line.strip().split(",")
                route_id = spl[0]
                shape_id = spl[6]
                if route_id in routes:
                    routes[route_id].set_shape_id(shape_id)
                else:
                    route = Route(route_id)
                    route.set_shape_id(shape_id)
                    routes[route_id] = route

        with open(routes_path) as f:
            f.readline()
            for line in f:
                spl = line.strip().split(",")
                route_id = spl[0]
                # We remove the quotation marks surrounding the name
                route_name = spl[3].replace('"', "")

                # This can result in a KeyError exception when routes.txt has a route_id not in trips.txt
                routes[route_id].set_route_name(route_name)
                self.__route_names[route_name] = route_id

        return routes

    def __load_shapes_data(self, shapes_path: str) -> dict[str, Shape]:
        """
        purpose:
            Parses the shapes data file and saves the shape IDs and its coordinate points.
        parameter:
            shapes_path: The file path to the shapes data file.
        return:
            None
        """
        shapes: dict[str, Shape] = {}
        with open(shapes_path) as f:
            f.readline()  # Skip header line
            for line in f:
                spl = line.strip().split(",")
                shape_id = spl[0]
                coord = float(spl[1]), float(spl[2])

                if shape_id in shapes:
                    shapes[shape_id].coordinates.append(coord)
                else:
                    shapes[shape_id] = Shape(shape_id)
                    shapes[shape_id].coordinates.append(coord)
        return shapes

    def __load_disruptions_data(self, disruptions_path: str) -> set[Disruption]:
        """
        purpose:
            Parses the disruptions data file and saves the finish dates and coordinates of each disruption
        parameters:
            disruptions_path: The file path to the shapes data file
        returns:
            None
        """
        disruptions: set[Disruption] = set()
        with open(disruptions_path) as f:
            f.readline()
            for line in f:
                data = SrtParser.parse_line(line)
                finish_date = DateConvert.strtodate(data[3])
                coords = Coordinates.parse(data[-1])
                disruption = Disruption(finish_date, coords)
                disruptions.add(disruption)

        return disruptions


def print_menu() -> None:
    """
    purpose:
        Prints the menu.
    parameter:
        None
    return:
        None
    """
    print(
        """
Edmonton Transit System
---------------------------------
(1) Load route data
(2) Load shapes data
(3) Load disruptions data

(4) Print shape IDs for a route
(5) Print coordinates for a shape ID
(6) Find longest shape for route

(7) Save routes and shapes in a pickle
(8) Load routes and shapes from a pickle

(9) Interactive map
(0) Quit
"""
    )


def load_route_data(data: RouteData) -> None:
    """
    purpose:
        Ask for a file path to the routes data file and load it.
        Defaults routes_path to "data/routes.txt"
    parameter:
        data: The RouteData object to load data to.
    return:
        None
    """
    path = input("Enter a filename: ")
    if not path:
        path = "data/routes.txt"
    try:
        data.load_routes_data(path)
        print(f"Data from {path} loaded")
    except IOError:
        print(f"IOError: Couldn't open {path}")


def load_shape_data(data: RouteData) -> None:
    """
    purpose:
        Ask for a file path to the shapes data file and load it.
        Defaults shapes_path to "data/shapes.txt"
    parameter:
        data: The RouteData object to load data to.
    return:
        None
    """
    path = input("Enter a filename: ")
    if not path:
        path = "data/shapes.txt"
    try:
        data.load_shapes_data(path)
        print(f"Data from {path} loaded")
    except IOError:
        print(f"IOError: Couldn't open {path}")


def load_disruptions_data(data: RouteData) -> None:
    """
    purpose:
        Ask for a file path to the disruptions data file and load it.
        Defaults disruptions_path to "data/traffic_disruptions.txt"
    parameter:
        data: The RouteData object to load data to.
    return:
        None
    """
    path = input("Enter a filename: ")
    if not path:
        path = "data/traffic_disruptions.txt"
    try:
        data.load_disruptions_data(path)
        print(f"Data from {path} loaded")
    except IOError:
        print(f"IOError: Couldn't open {path}")


def print_shape_ids(data: RouteData) -> None:
    """
    purpose:
        Asks for a route id and prints the shape IDs associated with it.
    parameter:
        data: The RouteData object to get data from.
    return:
        None
    """
    if not data.routes_loaded():
        print("Route data hasn't been loaded yet")
        return
    route_id = input("Enter route: ")
    route_name = data.get_route_long_name(route_id)
    shape_id = data.get_shape_ids_from_route_id(route_id)
    if not shape_id:
        print("\t** NOT FOUND **")
        return
    print(f"Shape ids for route [{route_name}]")
    for shape in shape_id:
        print("\t" + shape)


def print_coordinates(data: RouteData) -> None:
    """
    purpose:
        Asks for a shape ID and prints its associated coordinate points.
    parameter:
        data: The RouteData object to get data from.
    return:
        None
    """
    if not data.shapes_loaded():
        print("Shape ID data hasn't been loaded yet")
        return
    shape_id = input("Enter shape ID: ")
    coords = data.get_coords_from_shape_id(shape_id)
    if not coords:
        print("\t** NOT FOUND **")
        return
    print(f"Shape ID coordinates for {shape_id} are:")
    for shape in coords:
        print("\t" + repr(shape))


def find_longest_shape(data: RouteData) -> None:
    """
    purpose:
        Asks for a route_id and prints out its shape_id with the largest set of coordinates.
    parameter:
        data: The RouteData object to get data from.
    return:
        None
    """
    if not data.routes_loaded():
        print("Route data hasn't been loaded yet")
        return
    if not data.shapes_loaded():
        print("Shape ID data hasn't been loaded yet")
        return
    if not data.disruptions_loaded():
        print("Disruptions data hasn't been loaded yet")
        return
    route_id = input("Enter route ID: ")
    out = data.get_longest_shape_from_route_id(route_id)
    if not out:
        print("\t** NOT FOUND **")
        return
    shape_id, length = out
    print(f"The longest shape for {route_id} is {shape_id} with {length} coordinates")


def save_routes(data: RouteData) -> None:
    """
    purpose:
        Asks the user for a file path to save the pickled RouteData object to.
    parameter:
        data: The RouteData object to save into a file.
    return:
        None
    """
    data_path = input("Enter a filename: ")
    if not data_path:
        data_path = "data/etsdata.p"

    try:
        with open(data_path, "wb") as f:
            pickle.dump(data, f)
            print(f"Data structures successfully written to {data_path}")
    except FileNotFoundError:
        print(f"IOError: Couldn't save to {data_path}")
        return


def load_routes() -> RouteData | None:
    """
    purpose:
        Asks for a path to a pickled RouteData file and loads and returns it as an object.
        Returns None if reading file fails.
    parameter:
        None
    return:
        Returns a RouteData object if loading succeeds. Returns None if loading fails.
    """
    data_path = input("Enter a filename: ")
    if not data_path:
        data_path = "data/etsdata.p"

    try:
        with open(data_path, "rb") as f:
            data = pickle.load(f)
        print(f"Routes and shapes Data structures successfully loaded from {data_path}")
        return data
    except FileNotFoundError:
        print(f"IOError: Couldn't open {data_path}")
        return None


def interactive_map(data: RouteData) -> None:
    """
    purpose:
    parameter:
    return:
    """
    width, height = 800, 920
    ...


def lonlat_to_xy(win: GraphWin, lon: float, lat: float):
    """Written by Philip Mees for CMPT 103
    Purpose: convert longitude/latitude locations to x/y pixel locations
        This avoids the use of the setCoords, toWorld, and toScreen methods and graphics.py incompatibilities
    Parameters:
        win (GraphWin): the GraphWin object of the GUI
        lon, lat (float): longitude and latitude to be converted
    Returns: x, y (int): pixel location inside win"""

    xlow, xhigh = -113.720049, -113.320418
    ylow, yhigh = 53.657116, 53.393703

    width, height = win.getWidth(), win.getHeight()

    x = (lon - xlow) / (xhigh - xlow) * width
    y = (lat - ylow) / (yhigh - ylow) * height

    return int(x), int(y)


def main() -> None:
    """
    purpose:
        The program main loop.
    parameter:
        None
    return:
        None
    """
    data = RouteData()
    running = True
    while running:
        print_menu()
        user_input = input("Enter Command: ").strip()
        if user_input == "0":
            running = False
        elif user_input == "1":
            load_route_data(data)
        elif user_input == "2":
            load_shape_data(data)
        elif user_input == "3":
            load_disruptions_data(data)
        elif user_input == "4":
            print_shape_ids(data)
        elif user_input == "5":
            print_coordinates(data)
        elif user_input == "6":
            find_longest_shape(data)
        elif user_input == "7":
            save_routes(data)
        elif user_input == "8":
            out = load_routes()
            if out:
                data = out
        elif user_input == "9":
            interactive_map(data)
        else:
            print("Invalid Option")


if __name__ == "__main__":
    main()
