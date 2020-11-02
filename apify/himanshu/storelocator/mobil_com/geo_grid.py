
from typing import *

class Coord:
    pass
class Rect:
    pass
class GeoGrid:
    pass

class Coord:
    """
    Represents of a coordinate on a map.
    """

    DEFAULT_COORD_DEGREE_PRECISION = 4

    def __init__(self, lat: float, lng: float, precision=DEFAULT_COORD_DEGREE_PRECISION):
        """
        Unsafe creation of a `Coord`. Prefer the static `Coord.safely_create` method, instead.

        :param lat: Latitude.
        :param lng: Longitude.
        :param precision: Precision of the coordinate.
                E.g.: Coord(lat=1.2345, lng=-6.7890, precision=2).__repr__() == "Coord(lat: 1.23, lng: -6.78)"
        """
        self.lat = lat
        self.lng = lng
        self.precision = precision
        self.__repr_precalc = self.__repr_precalc_method()

    def __repr_precalc_method(self):
        lat_whole = int(self.lat)
        lng_whole = int(self.lng)
        lat_part = abs(int((self.lat - lat_whole) * (pow(10, self.precision))))
        lng_part = abs(int((self.lng - lng_whole) * (pow(10, self.precision))))
        return f"Coord(lat: {lat_whole}.{lat_part}, lng: {lng_whole}.{lng_part})"

    @staticmethod
    def safely_create(lat: float, lng: float, precision: int = DEFAULT_COORD_DEGREE_PRECISION):
        """
        Creates a Coord safely; Fails on invalid input with a ValueError.
        """
        c = Coord(lat=lat, lng=lng, precision=precision)
        if not c.is_valid():
            raise ValueError(f"Cannot create Coord with values: {c}")
        return c

    def is_valid(self) -> bool:
        if self.lat < -90.0 or 90 < self.lat:
            return False
        elif self.lng < -180.0 or 180.0 < self.lng:
            return False
        else:
            return True

    def is_north_of(self, other: Coord) -> bool:
        return self.lat > other.lat

    def is_east_of(self, other: Coord) -> bool:
        return self.lng > other.lng

    def __repr__(self):
        return self.__repr_precalc

    def equals(self, other: Coord) -> bool:
        """
        Compares against the result of the `__repr__` method.
        """
        return self.__repr__() == other.__repr__()

class Rect:
    """
    Represents a rectangle, with a top-left (N.E.) and bottom-right (S.W.) coordinates.
    Currently, the rectangle cannot cross the 180 meridian
    """

    def __init__(self, north_east: Coord, south_west: Coord):
        """
        Unsafe creation of `Rect`; prefer the static methods: `Rect.ne_sw` or `Rect.se_nw`
        :param north_east:
        :param south_west:
        """
        self.north_east = north_east
        self.south_west = south_west
        self.south_east = Coord(lat = south_west.lat, lng=north_east.lng)
        self.north_west = Coord(lat = north_east.lat, lng=south_west.lng)

    def is_valid(self) -> bool:
        return self.north_east.is_north_of(self.south_west) and self.north_east.is_east_of(self.south_west)

    def ne_sw(north_east: Coord, south_west: Coord):
        """
        Creates a `Rect` safely; Fails on invalid input with a ValueError.
        """
        r = Rect(north_east=north_east, south_west=south_west)
        if not r.is_valid():
            raise ValueError(f"N.E. coord isn't strictly to the N.E. of the S.W. coord in: {r}")
        return r

    @staticmethod
    def se_nw(south_east: Coord, north_west: Coord):
        """
        Creates a `Rect` safely; Fails on invalid input with a ValueError.
        """
        return Rect.ne_sw(north_east=Coord(north_west.lat, south_east.lng), south_west=Coord(south_east.lat, north_west.lng))

    def area_in_deg(self):
        """
        :return The area in degrees, where both lat and lng degrees are considered as one unit.
        """
        north = self.north_east.lat
        south = self.south_west.lat
        east  = self.north_east.lng
        west  = self.south_west.lng

        return (north - south) * (east - west)

    def __repr__(self):
        return f"Rect(north_east: {self.north_east}, south_west: {self.south_west})"

    def split_in_4(self, coord_precision: int = Coord.DEFAULT_COORD_DEGREE_PRECISION) -> GeoGrid:
        """
        Divides the rectangle into 4 equal sub-rectangles, passing the provided coordinate precision to the new coordinates.
        :return: A `GeoGrid` with named rectangles.
        """

        mid_lat = (self.north_east.lat + self.south_west.lat) / 2.0
        mid_lng = (self.north_east.lng + self.south_west.lng) / 2.0

        midpoint    = Coord(lat=mid_lat,                lng= mid_lng,               precision = coord_precision)
        mid_east    = Coord(lat = mid_lat,              lng = self.north_east.lng,  precision = coord_precision)
        mid_west    = Coord(lat = mid_lat,              lng = self.south_west.lng,  precision = coord_precision)
        north_mid   = Coord(lat = self.north_east.lat,  lng = mid_lng,              precision = coord_precision)
        south_mid   = Coord(lat = self.south_west.lat,  lng = mid_lng,              precision = coord_precision)

        ne_rect = Rect(north_east=self.north_east,  south_west=midpoint)
        se_rect = Rect(north_east=mid_east,         south_west=south_mid)
        nw_rect = Rect(north_east=north_mid,        south_west=mid_west)
        sw_rect = Rect(north_east=midpoint,         south_west=self.south_west)

        return GeoGrid(ne_rect=ne_rect, nw_rect=nw_rect, se_rect=se_rect, sw_rect=sw_rect)


class GeoGrid:
    """
    Represents an area grid divided into 4 sections: NE, SE, NW, SW.
    """

    def __init__(self, ne_rect: Rect, se_rect: Rect, nw_rect: Rect, sw_rect: Rect):
        self.ne_rect = ne_rect
        self.se_rect = se_rect
        self.nw_rect = nw_rect
        self.sw_rect = sw_rect
        self.as_a_list = [ne_rect, se_rect, nw_rect, sw_rect]

    def __repr__(self):
        return f"GeoGrid(ne_rect:{self.ne_rect}, se_rect: {self.se_rect}, nw_rect: {self.nw_rect}, sw_rect: {self.sw_rect})"

    @staticmethod
    def divide_and_conquer(box: Rect,
                           search_in_rect_fn: Callable[[Rect], list],
                           identity_fn: Callable[[object], str],
                           max_results_per_search: int,
                           encountered_ids=None) -> list:
        """
        Uses a divide and conquer approach to search within a rectangle, whereby the search-function has some maximum number
        of results it can return at once.

        :param box: The initial `Rect` to search in.
        :param search_in_rect_fn: A search function within a rectangle.
        :param identity_fn: A function from the result to its unique string representation. Aimed to dedup results.
        :param max_results_per_search: The known maximum results the search function can return at one time.
        :param encountered_ids: For internal usage; mutable set to of encountered ids (produced by `identity_fn`)
        :return: A generator of found values
        """
        if encountered_ids is None:
            encountered_ids = set()

        results = list(search_in_rect_fn(box))

        for r in results:
            rec_id = identity_fn(r)
            if rec_id not in encountered_ids:
                encountered_ids.add(rec_id)
                yield r

        if len(results) >= max_results_per_search:
            for box in box.split_in_4().as_a_list:
                for res in GeoGrid.divide_and_conquer(box=box,
                                                      search_in_rect_fn=search_in_rect_fn,
                                                      identity_fn=identity_fn,
                                                      max_results_per_search=max_results_per_search,
                                                      encountered_ids=encountered_ids):
                    yield res
