"""
``Coordinate``: a simple class with a custom ``__str__``::

    >>> moscow = Coordinate(55.756, 37.617)
    >>> print(moscow)  # doctest:+ELLIPSIS
    <coordinates.Coordinate object at 0x...>
"""
# В примере показан тот же класс Coordinate с двумя атрибутами float и методом __str__, который отображает координаты в формате 55.8°N, 37.6°E.

# tag::COORDINATE[]
class Coordinate:

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

# end::COORDINATE[]