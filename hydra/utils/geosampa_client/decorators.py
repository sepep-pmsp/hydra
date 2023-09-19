import json
from json import JSONDecodeError

import xmltodict

from .exceptions import ResponseNotJson, ResponseNotXML


def raise_for_status(func):
    '''Raises HTTP error for response status codes 4xx or 5xx.
    If not, returns content of response'''

    def decorated(*args, **kwargs):

        response = func(*args, **kwargs)
        response.raise_for_status()
        content = response.content

        return content

    return decorated


def json_response(func):
    '''Parses json response. Raises xml string error if
    xml is returned'''

    def decorated(*args, **kwargs):

        response = func(*args, **kwargs)
        json_txt = response.decode('utf-8')
        try:
            json_data = json.loads(json_txt)
            return json_data
        except JSONDecodeError:
            response = xmltodict.parse(response)
            raise ResponseNotJson(f'Response is not a JSON: {response}')
    
    return decorated

def xml_response(func):
    '''Parses xml response as a dict'''

    def decorated(*args, **kwargs):
        
        try:
            response = func(*args, **kwargs)
            parsed = xmltodict.parse(response)
            return parsed
        except Exception as e:
            raise ResponseNotXML(f'XML parsing failed {e}')
    
    return decorated