class Errors(Exception):
    """Base class for exceptions"""
    pass

class NotEnoughCannyEdgesError(Errors):

    def __str__(self):
        return "Not enough edges detected by Canny"

class NotEnoughIntersectionsError(Errors):

    # TODO: make it say how many were found
    def __str__(self):
        return "Not enough intersections detected."

class ImproperIntersectionsError(Errors):

    def __str__(self):
        return "Intersections do not form a square."

class NotEnoughPointsToTransformError(Errors):

    def __str__(self):
        return "Not enough points were passed to transform"
