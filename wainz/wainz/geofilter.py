class Geofilter:
    """
    A class representing a earth cap circle from the Google maps API.
    Represents a point on the earth by latitude and longitude, and
    a radius to complete the circle.
    """

    def __init__(self, iden, rad, lat, lng):
        self.id = iden
        self.rad = float(rad)
        self.lat = float(lat)
        self.lng = float(lng)
