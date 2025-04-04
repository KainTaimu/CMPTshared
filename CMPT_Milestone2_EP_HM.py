# -------------------------------
# Erwin Panergo, Hadi Moughnieh
# Programming Project - Milestone#2
# -------------------------------

import pickle
from datetime import date
from graphics4 import *


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
            # We've ran out of characters. Meaning the string is unterminated
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
            The modified string and the list of removed string
        """
        removed_strings: list[str] = []
        new_string = string
        for substring in substrings:
            removed_strings.append(substring)
            # We mark replaced strings with NUL to fill in later
            new_string = new_string.replace('"' + substring + '"', "\0")
        return new_string, removed_strings[::-1]


class DateConvert:
    """Contains methods that converts strings into date objects"""

    # Maps the month short forms to its numerical value
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

    def __init__(self, latitude: float, longitude: float):
        """
        purpose:
            Constructs a Coordinates object
        parameters:
            longitude: A float that represents the longitudinal coordinate
            latitude: A float that represents the latitudinal coordinate
        returns:
            None
        """
        self.latitude = latitude
        self.longitude = longitude

    # REMARK:
    # The shapes.txt file orders its coordinates by latitude and longitude.
    # However, disruptions.txt orders it by longitude and latitude instead.
    def __repr__(self) -> str:
        """
        purpose:
            Returns a tuple-like representation of this Coordinate.
        parameters:
            None
        returns:
            A string of form "({latitude}, {longitude})"
        """
        return f"({self.latitude}, {self.longitude})"

    def get_coords(self) -> tuple[float, float]:
        """
        purpose:
            Returns the longitudinal latitudinal coordinates.
        parameters:
            None
        returns:
            A tuple of floats representing the latitude and longitude coordinates respectively
        """
        return self.latitude, self.longitude

    # Factory methods need a classmethod so it returns the correct class type when
    # it is inherited later. Otherwise, it will return a Coordinate object rather than
    # the inherited type.
    @classmethod
    def parse(cls, string: str):
        """
        purpose:
            Parses a string into a Coordinates object.
            WARNING: The string orders its coordinates longtidude first, latitude second.
        parameters:
            string: The string of form "POINT (longitude latitude)"
        returns:
            The created Coordinates object
        """
        # Skip the first 7 characters, and the trailing bracket
        stripped = string[7:-2].split()
        longitude = float(stripped[0])
        latitude = float(stripped[1])
        return cls(latitude, longitude)


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
        self.coordinates: list[Coordinates] = []

    def __repr__(self) -> str:
        return f'Shape "{self.shape_id}" with {len(self.coordinates)} coordinates'


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
        # Cache the stripped and lowercased route destinations so its easier to access
        self.locations: list[str] = []
        self.route_id: str = route_id
        self.shape_ids: set[str] = set()

    def __repr__(self) -> str:
        """
        purpose:
            Returns a formatted string representation of this Route
        parameters:
            None
        returns:
            A string of form "Route {route_id} {locations}"
        """
        return f'Route {self.route_id} "{self.locations}"'

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
        spl = route_name.split(" - ")
        locations = []
        # strip and lowercase all strings inside the spl list
        for loc in spl:
            locations.append(loc.strip().lower())
        self.locations = locations


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

    def __repr__(self) -> str:
        return (
            f"Disruption: Finish date: {self.finish_date}, Coordinates: {self.coords}"
        )


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
        # Maps the route ID with its corresponding Route object
        self.__routes: dict[str, Route] = {}
        # Maps the shape ID with its corresponding Shape object
        self.__shape_ids: dict[str, Shape] = {}
        self.__disruptions: set[Disruption] = set()

    def __repr__(self) -> str:
        return f"RouteData: Routes: {self.routes_loaded()}, Shape IDs: {self.shapes_loaded()}, Disruptions: {self.disruptions_loaded()}"

    def load_trips_data(self, trips_path: str) -> None:
        """
        purpose:
            Attempts to load the trips data file. Raises an IOError exception if trips_path is invalid.
        parameter:
            trips_path: A string pointing to a path to a trips data file.
        return:
            None
        """
        self.__routes = self.__load_trips_data(trips_path)

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

    def get_routes(self) -> list[Route] | None:
        """
        purpose:
            Gets all loaded Routes
        parameter:
            None
        return:
            Returns a list of Route objects. Returns None if routes is not loaded
        """
        if not self.routes_loaded():
            return None
        return list(self.__routes.values())

    def get_disruptions(self) -> set[Disruption] | None:
        """
        purpose:
            Gets all loaded disruptions
        parameters:
            None
        returns:
            Returns a set of Disruption objects. Returns None if disruptions is not loaded
        """
        if not self.disruptions_loaded():
            return None
        return self.__disruptions

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

    def get_coords_from_shape_id(self, shape_id: str) -> list[Coordinates] | None:
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
            Returns the shape_id, and length associated with the route_id with the largest set of coordinates.
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
            # REMARK:
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
            Checks if the trips data file has been loaded.
        parameter:
            None
        return:
            Returns True if the trips file has been loaded. Otherwise, returns False.
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

    # REMARK:
    # Does not check if trips_path points to a proper trips.txt.
    # May result in incorrect data being saved rather than raising an exception.
    def __load_trips_data(self, trips_path: str) -> dict[str, Route]:
        """
        purpose:
            Parses the trips data file and saves it.
        parameter:
            trips_path: A string pointing to a path to a trips data file.
        return:
            Returns a dictionary with the route id as key and a Route object as value.
        """
        routes_path = "data/routes.txt"
        routes: dict[str, Route] = {}

        with open(trips_path) as f:
            f.readline()  # We skip the CSV header line
            for line in f:
                spl = line.strip().split(",")
                # Get the route_id and shape_id by index
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
                # shapes.txt orders its coordinates by latitude, longitude
                coord = Coordinates(float(spl[1]), float(spl[2]))

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
                # First, parse the line into a list of strings
                data = SrtParser.parse_line(line)
                # Convert the finish date string to a date object
                finish_date = DateConvert.strtodate(data[3])
                # Convert the point string into a Coordinate object
                coords = Coordinates.parse(data[-1])
                # Finally, create a Disruption object with the above objects
                disruption = Disruption(finish_date, coords)
                disruptions.add(disruption)

        return disruptions


class InteractiveMap:
    """Contains methods for creating and manipulating an interactive map"""

    @staticmethod
    def start(data: RouteData) -> None:
        """
        purpose:
            Starts an interactive map window
        parameters:
            data: The RouteData object to get data from.
        returns:
            None
        """
        win, from_entry_box, to_entry_box, search_box, clear_box, feedback_label = (
            InteractiveMap.create_map_window()
        )
        InteractiveMap.draw_disruptions(win, data)
        running = True
        while running:
            try:
                click_point = win.getMouse()
            except GraphicsError as ex:
                # Gracefully exit loop when clicking the close window button
                running = False
                continue

            if InteractiveMap.in_rectangle(click_point, search_box):
                # make entries case insensitive
                from_s = from_entry_box.text.get().strip().lower()
                to_s = to_entry_box.text.get().strip().lower()
                routes = data.get_routes()
                if not routes:
                    feedback_label.setText("ROUTES NOT LOADED")
                    continue
                if not data.shapes_loaded():
                    feedback_label.setText("SHAPES NOT LOADED")
                    continue

                route = InteractiveMap.search(routes, from_s, to_s)
                # route has not been found. do not draw route
                if not route:
                    feedback_label.setText("NOT FOUND")
                    continue

                feedback_label.setText(f"Drawing route {route.route_id}")
                # route has been found. draw it
                InteractiveMap.draw_route(win, data, route)

            # Clear all entry boxes
            elif InteractiveMap.in_rectangle(click_point, clear_box):
                from_entry_box.setText("")
                to_entry_box.setText("")
                feedback_label.setText("")

    @staticmethod
    def draw_disruptions(win: GraphWin, data: RouteData) -> None:
        """
        purpose:
            Draws all disruption points on the map
        parameters:
            win: The GraphWin object to draw to
            data: The RouteData object to get disruption data from
        returns:
            None
        """
        disruptions = data.get_disruptions()
        today = date.today()
        if not disruptions:
            return None
        for disruption in disruptions:
            # Don't draw point if disruption date has passed
            if disruption.finish_date < today:
                continue
            lat, lon = disruption.coords.get_coords()
            # Transform coordinates to pixel values
            x, y = InteractiveMap.lonlat_to_xy(win, lon, lat)

            # Draw red circles where disruptions occur
            point = Circle(Point(x, y), 3)
            point.setFill("red")
            point.draw(win)

    @staticmethod
    def create_map_window() -> (
        tuple[GraphWin, Entry, Entry, Rectangle, Rectangle, Text]
    ):
        """
        purpose:
            Creates the interactive map window
        parameter:
            None
        return:
            A tuple returning the following in order:
            The main window, from_entry_box, to_entry_box,
            search_box, clear_box, feedback_label
        """
        map_path = "edmonton.png"
        ui_width, ui_height = 800, 920

        # Initiate window
        win = GraphWin("ETS Data", ui_width, ui_height)
        win.setBackground("gray")

        # Draw the Edmonton map
        background = Image(Point(ui_width / 2, ui_height / 2), map_path)
        background.draw(win)

        # Create the from entry box
        from_entry_box = Entry(Point(120, 50), 15)
        from_entry_box.draw(win)
        from_entry_box_label = Text(Point(25, 50), "From:")
        from_entry_box_label.draw(win)

        # Create the to entry box
        to_entry_box = Entry(Point(120, 85), 15)
        to_entry_box.draw(win)
        to_entry_box_label = Text(Point(25, 85), "To:")
        to_entry_box_label.draw(win)

        # Create the search box
        search_box = Rectangle(Point(50, 105), Point(189, 125))
        search_box.setFill("lightgray")
        search_box.draw(win)

        # Create the search box label
        search_box_label = Text(Point(120, 116), "Search")
        search_box_label.draw(win)

        # Create the clear box
        clear_box = Rectangle(Point(50, 130), Point(189, 150))
        clear_box.setFill("lightgray")
        clear_box.draw(win)

        # Create the from clear box label
        clear_box_label = Text(Point(120, 141), "Clear")
        clear_box_label.draw(win)

        # Create the feedback label
        # ie: "NOT FOUND" "Drawing route ..."
        feedback_label = Text(Point(120, 165), "")
        feedback_label.setStyle("bold")
        feedback_label.draw(win)

        return win, from_entry_box, to_entry_box, search_box, clear_box, feedback_label

    @staticmethod
    def draw_route(win: GraphWin, data: RouteData, route: Route) -> None:
        """
        purpose:
            Draws a path from the longest shape_id stored by route.
        parameters:
            win: The GraphWin object where the route will be drawn
            data: The RouteData object containing route information
            route: The route to get its longest shape from, and draw it
        returns:
            None
        """
        points: list[Point] = []

        # First, get the longest shape; as specified by the project specification
        out = data.get_longest_shape_from_route_id(route.route_id)

        # We then check if out is a valid tuple.
        if not out:
            return

        # Now that we know for certain that out is a valid tuple, get the shape_id string.
        # We don't need the length of the coordinate list, so discard.
        shape_id = out[0]
        coords = data.get_coords_from_shape_id(shape_id)
        if not coords:
            return

        # Create points from coordinates and save into points list
        for coord in coords:
            lat, lon = coord.get_coords()
            # Transform from geographic coordinates to pixel values
            x, y = InteractiveMap.lonlat_to_xy(win, lon, lat)
            point = Point(x, y)
            points.append(point)

        # Connect each points with lines
        # Each new line starts from the terminating point of the previous line
        i = len(points) - 1
        last = points[-1]
        while i >= 0:
            pt = points[i]
            line = Line(last, pt)
            line.setWidth(4)
            line.setFill("blue")
            line.draw(win)
            last = pt
            i -= 1

    @staticmethod
    def search(routes: list[Route], from_s: str, to_s: str) -> Route | None:
        """
        purpose:
            Searches for a route that contains the specified locations
        parameters:
            routes: The list of routes to search in
            from_s: The lower case starting location string to search for
            to_s: The lower case destination location string to search for
        returns:
            Returns the first route that contains the specified locations. Returns None if no match is found
        """
        # Use sets to determine if a route contains the following search conditions
        search_conditions = set()
        if from_s != "":
            search_conditions.add(from_s)
        if to_s != "":
            search_conditions.add(to_s)

        for route in routes:
            loc = set(route.locations)

            # We have a starting location and a destination
            # Check if both conditions are present
            if from_s and to_s:
                if search_conditions.issubset(loc):
                    return route
            # Only have a starting or destination.
            # Specs state that single inputs should only search for routes with ONE location
            elif from_s:
                if loc == search_conditions:
                    return route
            elif to_s:
                if loc == search_conditions:
                    return route
            else:
                continue

        return None

    @staticmethod
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

    @staticmethod
    def in_rectangle(click_point, rect) -> bool:
        """
        Purpose:
            Determines if the mouse is clicked inside a rectangle
        Parameters:
            click_point - Point object at which the mouse was clicked
            rect - Rectangle object to be checked for mouse click
        Returns:
            True if click-point is inside rect, False otherwise
        """

        # Return True if both the x and y components of the mouse click are inside the rectangle.
        # Rectangle corner points can be any two opposite corner points. There is no guarantee
        # that P1 has lower x- and y-coordinates than P2, unless you program it that way.
        # This method works for all combinations of corner points.

        x_check = (
            rect.getP1().getX() < click_point.getX() < rect.getP2().getX()
            or rect.getP2().getX() < click_point.getX() < rect.getP1().getX()
        )

        y_check = (
            rect.getP1().getY() < click_point.getY() < rect.getP2().getY()
            or rect.getP2().getY() < click_point.getY() < rect.getP1().getY()
        )

        return x_check and y_check


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


# Remark
# Even though this is called load_route_data, this actually asks for trips.txt, not routes.txt.
def load_route_data(data: RouteData) -> None:
    """
    purpose:
        Ask for a file path to the trips data file and load it.
        Defaults trips_path to "data/trips.txt"
    parameter:
        data: The RouteData object to load data to.
    return:
        None
    """
    path = input("Enter a filename: ")
    if not path:
        path = "data/trips.txt"
    try:
        data.load_trips_data(path)
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
        print("\t" + str(shape))


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
        print(
            f"Data structures successfully loaded into routes, shapes and disruptions"
        )
        return data
    except FileNotFoundError:
        print(f"IOError: Couldn't open {data_path}")
        return None


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
            InteractiveMap.start(data)
        else:
            print("Invalid Option")
