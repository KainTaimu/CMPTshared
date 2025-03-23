### The shit we need to keep track of
We need to keep 4 things:
- route_long_name: The full route name 
  - "Eaux Claires - West Clareview"
- route_id: A short id for a bus route
  - "117"
  - "120X"
- shape_id: No fkn clue why you need an id for a shape
  - "117-34-East"
  - "117-35-West"
- shape_coordinates: The latitude and longitude of a shape_id
  - "(53.616871, -113.516426)"
  - "(53.616892, -113.516468)"

**trips.txt** contains the route IDs and shape IDs  
**routes.txt** contains the route long names  
**shapes.txt** contains the shape_ids and its coordinates  

### Route:
This data structure keeps the three things we load in **trips.txt** and **routes.txt**.  
#### Layout:
```json
{
    "route_id": "117",
    "route_name": "Eaux Claires - West Clareview",
    "shape_ids": [
        "117-34-East",
        "117-35-West"
    ]
}
```

### Shape
This data structure keeps the shape_id and coordinates from **shapes.txt**.  
#### Layout:
```json
{
    "shape_id": "112-3-East",
    "coordinates": [
        (53.616871, -113.516426),
        (53.616892, -113.516468),
            ...         ...
    ]
}
```

### RouteData:
This data structure holds and connects everything and serves as a place to get data (route ids, etc.) from.
#### JSON-like Layout:
```yaml
{
    "__route_names": {
        "Eaux Claires - West Clareview": "117",
        ...
    },
    "__routes": {
        "117": {
            "route_id": "117",
            "route_name": "Eaux Claires - West Clareview",
            "shape_ids": [
                "117-34-East",
                "117-35-West"
            ]
        },
        ...
    },
    "__shapes_ids": {
        "112-3-East": {
            "shape_id": "112-3-East",
            "coordinates": [
                (53.616871, -113.516426),
                (53.616892, -113.516468),
                    ...         ...
            ]
        },
        ...
    }
}
```

#### Methods
load_trips_data(self, trips_path: str):  
N/A

load_shapes_data(self, shapes_path: str):  
N/A

get_route_long_name(self, route_id: str):  
N/A

get_route_id(self, route_long_name: str):  
N/A

get_coords_from_shape_id(self, shape_id: str):  
N/A

get_shape_id_from_route_id(self, route_id: str):  
N/A

routes_loaded(self):  
N/A

shapes_loaded(self):  
N/A

__load_trips_data(self, trips_path: str):  
N/A

__load_shapes_data(self, shapes_path: str):  
N/A
