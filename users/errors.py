"""
These classes represent the possible errors to be returned
in the form of a pair (json, status_code)
A error object has 4 properties:
    - type (usually about:blank)
    - title (the title of the error)
    - status (the status code)
    - detail (a description of the error and it's causes)
"""


class Error:
    def __init__(self, type, title, status, detail):
        """ General error """
        self.type = type # pragma: no cover
        self.title = title # pragma: no cover
        self.status = status # pragma: no cover
        self.detail = detail # pragma: no cover

    def get(self):
        """ Returns the pair (json, status_code) """
        return {
                   "type": self.type,
                   "title": self.title,
                   "status": self.status,
                   "detail": self.detail,
               }, self.status


class Error400(Error):
    def __init__(self, detail):
        """ Bad Request """
        self.type = "about:blank"
        self.title = "Bad Request"
        self.status = 400
        self.detail = detail


class Error404(Error):
    def __init__(self, detail):
        """ Not Found """
        self.type = "about:blank"
        self.title = "Not Found"
        self.status = 404
        self.detail = detail


class Error500(Error):
    def __init__(self):
        """ Internal Server Error
        In GoOutSafe it is usually launched when there is a problem with the database
        or in communication with other microservices.

        It is usually accompanied by a notification to the user asking her to try again
        """
        self.type = "about:blank" # pragma: no cover
        self.title = "Internal Server Error" # pragma: no cover
        self.status = 500 # pragma: no cover
        self.detail = "An error occured, please try again" # pragma: no cover