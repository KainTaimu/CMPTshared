# -------------------------------
# Erwin Panergo, Hadi Moughnieh
# Programming Project - Milestone#1
# -------------------------------

{"008": ["Shape('117-34-East')", "Shape('117-35-West')"]}  # type: ignore

{"117-35-West": [(53.602366, -113.412183), (53.602160, -113.412500)]}  # type: ignore

# self.__shape_id = {
# "008": [
# Shape("117-34-East", [1, -1]),
# Shape("117-35-West", [-1, 1]),
# ]
# }


class Shape:
    def __init__(self, shape_id: str):
        self.__shape_id = shape_id
        self.coordinates: list[tuple[float, float]] = []


class Route:
    def __init__(self, route_id: str) -> None:
        self.route_id: str = route_id
        self.route_name: str
        self.shape_id: set[str] = set()

    def set_shape_id(self, shape_id: str):
        self.shape_id.add(shape_id)

    def set_route_name(self, route_name: str):
        self.route_name = route_name


class RouteData:
    """
    purpose:
    parameter:
    return:
    """

    def __init__(self):
        self.__routes: dict[str, Route] = {}
        self.__shape_ids: dict[str, Shape] = {}

    def load_trips_data(self, trips_path: str):
        ROUTES_PATH = "data/routes.txt"

        if not trips_path:
            trips_path = "data/trips.txt"

        routes: dict[str, Route] = {}
        with open(trips_path) as f:
            f.readline()
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

        with open(ROUTES_PATH) as f:
            f.readline()
            for line in f:
                spl = line.strip().split(",")
                route_id = spl[0]

                # We remove the quotation marks surroundin the name
                route_name = spl[3].replace('"', "")
                routes[route_id].set_route_name(route_name)

        self.__routes = routes
        print(f"Data from {trips_path} loaded")

    def load_shapes_data(self, shapes_path: str):
        if not shapes_path:
            shapes_path = "data/shapes.txt"
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
                    

        self.__shape_ids = shapes
        print(f"Data from {shapes_path} loaded")

    def get_route_long_name(self, route_id: str):
        if route_id in self.__routes:
            return self.__routes[route_id].route_name
        return None

    def get_coords_from_shape_id(self, shape_id: str):
        if shape_id in self.__shape_ids:
            return self.__shape_ids[shape_id].coordinates
        return None            

    def get_shape_id_from_route_id(self, route_id: str):
        if route_id in self.__routes:
            return self.__routes[route_id].shape_id
        return None

    def routes_loaded(self):
        if self.__routes:
            return True
        return False

    def shapes_loaded(self):
        if self.__shape_ids:
            return True
        return False


def print_menu() -> None:
    """
    purpose:
    parameter:
    return:
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


def load_route_data(data: RouteData):
    path = input("Enter a filename: ")
    try:
        data.load_trips_data(path)
    except IOError:
        print(f"IOError: Couldn't open {path}")


def load_shape_data(data: RouteData):
    path = input("Enter a filename: ")
    try:
        data.load_shapes_data(path)
    except IOError:
        print(f"IOError: Couldn't open {path}")


def print_shape_ids(data: RouteData):
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


def print_coordinates(data: RouteData):
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


def main() -> None:
    """
    purpose:
    parameter:
    return:
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
            pass
        elif user_input == "8":
            pass
        elif user_input == "9":
            print("Option 9 reserved for Milestone#2")
        else:
            print("Invalid Option")


if __name__ == "__main__":
    main()