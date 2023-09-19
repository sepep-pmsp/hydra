from requests.exceptions import HTTPError


class ResponseNotJson(HTTPError):
    '''Raised when the response is not a JSON'''

class ResponseNotXML(HTTPError):
    '''Raised when the response is not a XML'''

class PaginationError(HTTPError):
    '''Raised hen total retrieved features is not equal to total features returned by API'''