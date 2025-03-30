# -------------------------------
# Erwin Panergo, Hadi Moughnieh
# Programming Project - Milestone#1
# -------------------------------

import pickle


class Shape:
    """
    Holds the shape ID and coordinates of a Shape
    """

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
    """
    Holds the route ID, full route name, and shape IDs specified in trips.txt
    """

    def __init__(self, route_id: str):
        """
        purpose:
            Constructs a Route object
        parameters:
            route_id: The initialized route_id string
        returns:
            None
        """
        self.route_id: str = route_id
        self.route_name: str
        self.shape_ids: set[str] = set()

    def set_shape_id(self, shape_id: str) -> None:
        """
        purpose:
            Sets the shape ID attribute.
        parameter:
            shape_id: The string to assign as attribute.
        return:
            None
        """
        self.shape_ids.add(shape_id)

    def set_route_name(self, route_name: str) -> None:
        """
        purpose:
            Sets the route long name attribute.
        parameter:
            route_name: The string to assign as attribute.
        return:
            None
        """
        self.route_name = route_name


class RouteData:
    """
    Provides an interface to load and access routes and shape IDs
    """

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

    def get_shape_id_from_route_id(self, route_id: str) -> set[str] | None:
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

    # REMARK
    # Will not raise an exception if routes_path is set to a wrong, yet valid file, such as trips.txt
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
        TRIPS_PATH = "data/trips.txt"
        routes: dict[str, Route] = {}

        # Since trips.txt is hardcoded, the user will not know if opening 'data/trips.txt' raises an error.
        with open(TRIPS_PATH) as f:
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
(3) Reserved for future use

(4) Print shape IDs for a route
(5) Print coordinates for a shape ID
(6) Reserved for future use

(7) Save routes and shapes in a pickle
(8) Load routes and shapes from a pickle

(9) Reserved for future use
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
    shape_id = data.get_shape_id_from_route_id(route_id)
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
            print("Option 3 reserved for Milestone#2")
        elif user_input == "4":
            print_shape_ids(data)
        elif user_input == "5":
            print_coordinates(data)
        elif user_input == "6":
            print("Option 6 reserved for Milestone#2")
        elif user_input == "7":
            save_routes(data)
        elif user_input == "8":
            out = load_routes()
            if out:
                data = out
        elif user_input == "9":
            print("Option 9 reserved for Milestone#2")
        else:
            print("Invalid Option")
