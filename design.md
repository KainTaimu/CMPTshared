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

### RouteData:
This data structure holds and connects everything and serves as a place to get data (route ids, etc.) from.
#### JSON-like Layout:
```json
{
    // If we don't have the route ID, we can get it from the long name instead.
    "__route_names": {
        "Eaux Claires - West Clareview": "117",
        ...
    },
    "__routes": {
        "117": {
            "route_id": "117",
            "route_name": "Eaux Claires - West Clareview",
            "shape_id": {
                "117-34-East",
                "117-35-West"
            }
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